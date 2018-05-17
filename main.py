import json
import logging
import os
import sys
import time

import click
from silvair_uart_common_libs.message_types import ModelID, ModelDesc
from silvair_uart_common_libs.uart_common_classes import UartAdapter

from silvair_otau_demo.dfu_logic.dfu_fail_mgr import DFU_FailMgr
from silvair_otau_demo.console_out import ConsoleOut
from silvair_otau_demo.dfu_logic.dfu_memory import DFUMemory, MIN_SUPPORTED_PAGE_SIZE
from silvair_otau_demo.dfu_logic.dfu_mgr import DFU_Mgr
from silvair_otau_demo.dispatcher import Dispatcher, Sender
from silvair_otau_demo.event_mgr import EventMgr
from silvair_otau_demo.uart_logic.uart_fsm_mgr import UART_FSM

LOGGER = logging.getLogger('silvair_otau_demo')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger('silvair_otau_demo')
log.setLevel(logging.DEBUG)


def config_logger(verbose):
    """
    Configure stdout logger

    :param verbose: Verbosity level
    """
    ch_cli = logging.StreamHandler(sys.stdout)
    ch_cli.setFormatter(formatter)
    ch_cli.setLevel(logging.ERROR)
    if verbose > 0:
        if verbose == 1:
            ch_cli.setLevel(logging.INFO)
        elif verbose == 2:
            ch_cli.setLevel(logging.DEBUG)
    log.addHandler(ch_cli)

def config_file_logger(path):
    """
    Configure file logger

    :param path: Path to file
    """
    ch_file = logging.FileHandler(path)
    ch_file.setFormatter(formatter)
    ch_file.setLevel(logging.DEBUG)
    log.addHandler(ch_file)

def parse_model_ids(model):
    """
    Parse given model ids from HEX strings to ints

    :param model:   list, model ids as strings
    :return:        tuple, model ids as ints
    """
    models_to_register = tuple()
    for m in model:
        LOGGER.debug("Requested models to register: %s" % m)
        m_id = ModelDesc(ModelID(int(m, 16)))
        models_to_register += (m_id,)

    return models_to_register

def load_app_data(expected_app_data):
    """
    Loads app data.

    :param expected_app_data:   Path to file with expected app data
    :return:                    bytes, expected app data
    """
    if expected_app_data:
        try:
            LOGGER.info("Loading expected app data from file")

            with open(expected_app_data, 'rb') as expected_app_data_file:
                expected_app_data_bytes = expected_app_data_file.read()

            LOGGER.debug("Loaded app data: " + expected_app_data.hex())
        except:
            LOGGER.error("Failed to open expected app data file, ignoring app data.")

            expected_app_data_bytes = None
    else:
        expected_app_data_bytes = None

    return expected_app_data_bytes

@click.command()
@click.option('-c', '--config_file', help='JSON configuration file path')
@click.option('-s', '--com_port', help='COM port name')
@click.option('-a', '--app_data_file', default='app_data', help='File to save app data')
@click.option('-f', '--firmware_file', default='firmware', help='File to save firmware data')
@click.option('-h', '--sha256_file', default='sha256', help='File to save firmware SHA256')
@click.option('-n', '--nvm_file', default='nvm', help='File to save DFU state')
@click.option('-p', '--supported_page_size', default=1024, help='Max supported page size in bytes')
@click.option('-x', '--max_mem_size', default=0, type=int, help='Max supported firmware size in bytes')
@click.option('-e', '--expected_app_data', type=str, help='File with expected app data (binary) used in pre validation')
@click.option('-b', '--pre_validation_fail', type=bool, default=False, help='Deliberately cause pre validation fail')
@click.option('-q', '--post_validation_fail', type=bool, default=False, help='Deliberately cause post validation fail')
@click.option('-v', '--verbose', count=True, help='Verbosity level; -vv for full log')
@click.option('-l', '--log_file', default='otau.log', help='File to save logs')
@click.option('-t', '--forget_state', count=True, help='Set to ignore saved state')
@click.option('-r', '--clear', count=True, help='Remove created files on start')
@click.option('-m', '--model', type=str, help='Model to register', multiple=True)
def start(config_file,
          com_port,
          app_data_file,
          firmware_file,
          sha256_file,
          nvm_file,
          supported_page_size,
          max_mem_size,
          expected_app_data,
          pre_validation_fail,
          post_validation_fail,
          verbose,
          log_file,
          forget_state,
          clear,
          model):
    """
    Python OTAU script.

    If config file is specified other arguments are ignored.
    """
    if clear:
        print('Clearing files')
        os.remove(app_data_file)
        os.remove(firmware_file)
        os.remove(sha256_file)
        os.remove(nvm_file)

    if com_port is None and config_file is None:
        print("You have to specify at least com port or config json! See --help for more")
        return

    config_logger(verbose)

    LOGGER.info("Starting application!")

    if config_file:
        LOGGER.info("Loading configuration from file")
        try:
            with open(config_file) as file:
                config = json.load(file)
                com_port = config['com_port']
                app_data_file = config['app_data_file']
                firmware_file = config['firmware_file']
                sha256_file = config['sha256_file']
                nvm_file = config['nvm_file']
                supported_page_size = config['supported_page_size']
                max_mem_size = config['max_mem_size']
                expected_app_data = config['expected_app_data']
                pre_validation_fail = bool(config['pre_validation_fail'])
                post_validation_fail = bool(config['post_validation_fail'])
                log_file = config['log_file']
                model = config['model']
        except FileNotFoundError:
            print("File {:s} not found".format(config_file))
            exit()
        except KeyError as e:
            print("Config file should contain {:s} key".format(e.args[0]))
            exit()

    config_file_logger(log_file)

    if supported_page_size < MIN_SUPPORTED_PAGE_SIZE:
        print("Supported page size has to be bigger than {:d}".format(MIN_SUPPORTED_PAGE_SIZE))
        exit()

    event_mgr = EventMgr(ConsoleOut)
    uart_adapter = UartAdapter(com_port)
    sender = Sender(uart_adapter)

    models_to_register = parse_model_ids(model)
    uart_fsm = UART_FSM(sender, event_mgr, default_models=models_to_register)

    if forget_state:
        LOGGER.info("Clearing nvm file")
        nvm_file_handler = open(nvm_file, 'w')
        nvm_file_handler.close()

    expected_app_data_bytes = load_app_data(expected_app_data)
    dfu_fail_mgr = DFU_FailMgr(expected_app_data_bytes,
                               pre_validation_fail,
                               post_validation_fail)
    dfu_memory = DFUMemory(app_data_file,
                           firmware_file,
                           sha256_file,
                           supported_page_size,
                           max_mem_size)
    dfu_mgr = DFU_Mgr(sender,
                      event_mgr,
                      dfu_memory,
                      dfu_fail_mgr,
                      nvm_file)

    dfu_dispatcher = Dispatcher(uart_fsm, dfu_mgr.dfu_fsm)
    uart_adapter.register_observer(dfu_dispatcher)

    uart_adapter.start()
    uart_fsm.start()
    dfu_mgr.dfu_fsm.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOGGER.info("Caught KeyboardInterrupt")

    uart_adapter.stop()
    ConsoleOut.stop_progress_bar()

    print("Bye!")

if __name__ == "__main__":
    start()
