import logging
import os

from silvair_otau_demo.dfu_logic.dfu_memory import DFUMemory
from silvair_otau_demo.dfu_logic.dfu_mgr import DFU_Mgr
from silvair_otau_demo.dispatcher import Dispatcher, Sender
from silvair_otau_demo.uart_logic.uart_fsm_mgr import UART_FSM
from silvair_uart_common_libs.message_types import ModelID, ModelDesc

LOGGER = logging.getLogger(__name__)


def parse_model_ids(model, logger):
    """
    Parse given model ids from HEX strings to ints

    :param model:   list, model ids as strings (representing hexes, i.e. ['1001', '1300'])
    :param logger:  logger object instance
    :return:        tuple, model ids as ints
    """
    models_to_register = tuple()
    for m in model:
        logger.debug("Requested models to register: %s" % m)

        try:
            mid_value = int(m, 16)
        except ValueError:
            logger.error("Failed to parse model ids. Passed value: '%s' is not valid hex value.", m)
            raise

        try:
            mid = ModelID(mid_value)
        except ValueError:
            logger.error("Failed to parse model ids. ModelID: '%s' is not supported.", m)
            raise

        mdesc = ModelDesc(mid)
        models_to_register += (mdesc,)

    return models_to_register


class McuOtauMock:
    """
    Class mocking external MCU during OTAU process.
    """

    def __init__(self,
                 uart_adapter,
                 event_manager,
                 fail_manager,
                 app_data_file,
                 firmware_file,
                 sha256_file,
                 nvm_file,
                 supported_page_size,
                 max_mem_size,
                 expected_app_data_file,
                 model,
                 ):
        """
        :param uart_adapter:              UartAdapter object used to communicate with firmware
        :param event_manager:             EventManager object used for generating events
        :param fail_manager:              FailManager object that generates negative scenarios during dfu
        :param app_data_file:             str, path to file with app data used in OTAU
        :param firmware_file:             str, path to file with firmware for validation
        :param sha256_file:               str, path to sha256 of app data
        :param nvm_file:                  str, path to tile when nvm is stored
        :param supported_page_size:       int, denotes page size for OTAU process
        :param max_mem_size:              int, max supported size of firmware in bytes, 0 implies unlimited
        :param expected_app_data_file:    str, path to app data file used in validation for OTAU
        :param model:                     str representing hex of models to register (with appropriate parameters)
        """
        self.uart_adapter = uart_adapter
        self.event_manager = event_manager
        self.fail_manager = fail_manager

        self.app_data_file = app_data_file
        self.firmware_file = firmware_file
        self.sha256_file = sha256_file
        self.nvm_file = nvm_file
        self.supported_page_size = supported_page_size
        self.max_mem_size = max_mem_size
        self.expected_app_data_file = expected_app_data_file
        self.model = model

        self.sender = None
        self.uart_fsm = None
        self.dfu_memory = None
        self.dfu_mgr = None
        self.dfu_dispatcher = None

        try:
            with open(self.expected_app_data_file, 'rb') as f:
                self.expected_app_data = f.read()

        except TypeError:
            LOGGER.debug("Flag '--expected_app_data_file' has not been set. Application data will not be checked.")
            self.expected_app_data = None

        except OSError:
            LOGGER.warning("Could not open app data file: '%s'. Application data will not be checked.",
                           self.expected_app_data_file)
            self.expected_app_data = None

        self.setup_objects()

    def setup_objects(self):
        """
        Create and bind objects used in MCU DFU script. If config file is specified other arguments are ignored.
        """
        LOGGER.info("Starting application!")
        self.sender = Sender(self.uart_adapter)

        models_to_register = parse_model_ids(self.model, LOGGER)
        self.uart_fsm = UART_FSM(self.sender, self.event_manager, default_models=models_to_register)

        self.dfu_memory = DFUMemory(self.app_data_file,
                                    self.firmware_file,
                                    self.sha256_file,
                                    self.supported_page_size,
                                    self.max_mem_size)

        self.dfu_mgr = DFU_Mgr(self.sender,
                               self.event_manager,
                               self.dfu_memory,
                               self.fail_manager,
                               self.nvm_file,
                               self.expected_app_data)

        self.dfu_dispatcher = Dispatcher(self.uart_fsm, self.dfu_mgr.dfu_fsm)
        self.uart_adapter.register_observer(self.dfu_dispatcher)

        self.uart_fsm.start()
        self.dfu_mgr.dfu_fsm.start()

    def delete_objects(self):
        """
        Unregister dispatcher from observers and set objects to None for deletion.
        """
        self.uart_adapter.unregister_observer(self.dfu_dispatcher)
        self.sender = None
        self.uart_fsm = None
        self.dfu_memory = None
        self.dfu_mgr = None
        self.dfu_dispatcher = None
