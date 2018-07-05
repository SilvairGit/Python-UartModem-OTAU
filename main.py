import click
import json
import logging
import os
import sys
import time

from silvair_otau_demo.app_data import AppData
from silvair_otau_demo.console_out import ConsoleOut
from silvair_otau_demo.dfu_logic.dfu_fail_mgr import DFUFailMgr, DFUFault
from silvair_otau_demo.event_mgr import EventMgr
from silvair_otau_demo.script_mgr import McuOtauMock
from silvair_uart_common_libs.message_types import DFUStatus
from silvair_uart_common_libs.uart_common_classes import UartAdapter
from silvair_otau_demo.dfu_logic.dfu_memory import MIN_SUPPORTED_PAGE_SIZE

LOGGER = logging.getLogger('silvair_otau_demo')
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def config_logger_stdout(verbose, logger, formatter):
    """
    Configure stdout for given logger

    :param verbose: Verbosity level
    :param logger: logger object instance
    :param formatter: formatter for logger
    """
    ch_cli = logging.StreamHandler(sys.stdout)
    ch_cli.setFormatter(formatter)
    ch_cli.setLevel(logging.WARNING)
    if verbose > 0:
        if verbose == 1:
            ch_cli.setLevel(logging.INFO)
        elif verbose == 2:
            ch_cli.setLevel(logging.DEBUG)
    logger.addHandler(ch_cli)


def config_logger_file(path, logger, formatter):
    """
    Configure file log

    :param path: Path to file
    :param logger: logger object instance
    :param formatter: formatter for logger
    """
    ch_file = logging.FileHandler(path)
    ch_file.setFormatter(formatter)
    ch_file.setLevel(logging.DEBUG)
    logger.addHandler(ch_file)


def parse_config_file(config_file_path, logger):
    """
    Parses config file to dictionary

    :param config_file_path: str, path to configuration file
    :param logger: logger object instance
    :return: dict with parsed parameters from config file
    """
    config_dict = dict()
    logger.info("Loading configuration from file")
    try:
        with open(config_file_path, "r") as file:
            config = json.load(file)
            config_dict["com_port"] = config["com_port"]
            config_dict["clear"] = bool(config["clear"])
            config_dict["forget_state"] = bool(config["forget_state"])
            config_dict["app_data_file"] = config["app_data_file"]
            config_dict["firmware_file"] = config["firmware_file"]
            config_dict["sha256_file"] = config["sha256_file"]
            config_dict["nvm_file"] = config["nvm_file"]
            config_dict["supported_page_size"] = config["supported_page_size"]
            config_dict["max_mem_size"] = config["max_mem_size"]
            config_dict["expected_app_data"] = config["expected_app_data"]
            config_dict["pre_validation_fail"] = bool(config["pre_validation_fail"])
            config_dict["post_validation_fail"] = bool(config["post_validation_fail"])
            config_dict["log_file"] = config["log_file"]
            config_dict["model"] = config["model"]
    except FileNotFoundError:
        logger.error("File %s not found", config_file_path)
        raise
    except KeyError as e:
        logger.error("Config file should contain %s key", e.args[0])
        raise
    return config_dict


def remove_file(path):
    """
    Removes file.

    :param path: str, path to file to be removed
    :return: bool True when success False when failure
    """
    path = os.path.abspath(path)

    if not os.path.exists(path):
        LOGGER.warning("Could not remove file: '%s'. File not exists.", path)
        return False

    if not os.path.isfile(path):
        LOGGER.warning("Could not remove file: '%s'. Invalid file type.", path)
        return False

    os.remove(path)
    return True


@click.command()
@click.option('-c', '--config_file', help='JSON configuration file path. Overwrites cli arguments.')
@click.option('-s', '--com_port', help='COM port name')
@click.option('-a', '--app_data_file', default='app_data', help='File to save app data')
@click.option('-f', '--firmware_file', default='firmware', help='File to save firmware data')
@click.option('-h', '--sha256_file', default='sha256', help='File to save firmware SHA256')
@click.option('-n', '--nvm_file', default='nvm', help='File to save DFU state')
@click.option('-p', '--supported_page_size', default=1024, help='Max supported page size in bytes')
@click.option('-x', '--max_mem_size', default=0, type=int, help='Max supported firmware size in bytes, 0 implies unlimited')
@click.option('-e', '--expected_app_data', type=str, help='File with expected app data (binary) used in pre validation')
@click.option('-b', '--pre_validation_fail', is_flag=True, help='Deliberately cause pre validation fail')
@click.option('-q', '--post_validation_fail', is_flag=True, help='Deliberately cause post validation fail')
@click.option('-v', '--verbose', count=True, help='Verbosity level; -vv for full log')
@click.option('-l', '--log_file', default='otau.log', help='File to save logs')
@click.option('-t', '--forget_state', is_flag=True, default=False, help='Set to ignore saved state')
@click.option('-r', '--clear', is_flag=True, help='Remove created files on start')
@click.option('-m', '--model', type=str, multiple=True,
              help='Model to register, use multiple times to add more than one model. Example: -m 0003 -m 1300')
def start(**kwargs):
    """
    Start OTAU script.

    If config file is specified other arguments are ignored.
    """
    if kwargs["com_port"] is None and kwargs["config_file"] is None:
        LOGGER.warning("You have to specify at least com port or config json! See --help for more")
        return

    if kwargs["config_file"]:
        cli_args = parse_config_file(kwargs["config_file"], LOGGER)
    else:
        cli_args = kwargs

    config_logger_stdout(kwargs["verbose"], LOGGER, FORMATTER)
    config_logger_file(cli_args["log_file"], LOGGER, FORMATTER)

    if int(cli_args["supported_page_size"]) < MIN_SUPPORTED_PAGE_SIZE:
        LOGGER.error("Supported page size has to be bigger than {:d}".format(MIN_SUPPORTED_PAGE_SIZE))
        raise ValueError

    if cli_args["clear"]:
        LOGGER.debug("Clearing files")
        remove_file(cli_args["app_data_file"])
        remove_file(cli_args["firmware_file"])
        remove_file(cli_args["sha256_file"])
        remove_file(cli_args["nvm_file"])

    if cli_args["forget_state"]:
        LOGGER.debug("Clearing nvm file")
        with open(cli_args["nvm_file"], "w") as _:
            pass

    uart_adapter = UartAdapter(port=cli_args["com_port"])
    uart_adapter.start()

    cli_event_manager = EventMgr(ConsoleOut)
    dfu_fail_mgr = DFUFailMgr()

    if cli_args["pre_validation_fail"]:
        dfu_fail_mgr.add_on_pre_validation_fault(DFUFault.create_fault_with_status(None, DFUStatus.DFU_INVALID_OBJECT))

    if cli_args["post_validation_fail"]:
        dfu_fail_mgr.add_on_post_validation_fault(DFUFault.create_fault_with_status(None, DFUStatus.DFU_INVALID_OBJECT))

    if not len(cli_args["model"]):
        LOGGER.warning("Model not provided. Will register Light Lightness Server (1300)")
        cli_args["model"] = ("1300",)

    try:
        McuOtauMock(uart_adapter,
                    cli_event_manager,
                    dfu_fail_mgr,
                    cli_args["app_data_file"],
                    cli_args["firmware_file"],
                    cli_args["sha256_file"],
                    cli_args["nvm_file"],
                    cli_args["supported_page_size"],
                    cli_args["max_mem_size"],
                    cli_args["expected_app_data"],
                    cli_args["model"],
                    )

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            LOGGER.info("Caught Keyboard interrupt!")

    except ValueError as e:
        LOGGER.info("Caught exception: {}!".format(e))

    finally:
        uart_adapter.stop()
        cli_event_manager.stop()


if __name__ == "__main__":
    start()
