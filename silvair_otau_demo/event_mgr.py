import logging

from silvair_uart_common_libs.message_types import FactoryResetSource, AttentionEvent, Error
from silvair_uart_common_libs.messages import UartCommand

from .console_out import ConsoleOut
from .dfu_logic.dfu_mgr import DFU_FSM_EventMgr
from .dfu_logic.states.dfu_fsm_states import DFUState
from .uart_logic.states.uart_fsm_states import UART_FSMState
from .uart_logic.uart_fsm_mgr import UART_FSM_EventMgr

LOGGER = logging.getLogger(__name__)

class EventMgr(UART_FSM_EventMgr, DFU_FSM_EventMgr):
    """
    Handles events coming from inside DFU script
    """

    def __init__(self, cli):
        """
        Initialize event mgr
        :param cli:     CLI for outputing messages
        """
        assert cli is not None
        self.cli = cli

        LOGGER.info("EventMgr initialized")

    def uart_unexpected_message(self, type: UartCommand):
        """
        Handle uart unexpected message event

        :param type: UartCommand (IntEnum), message opcode
        :return:     None
        """
        self.cli.print_error_message("Received unexpected UART message: " + type.name)

    def uart_mesh_request(self, opcode: int, command: bytes):
        """
        Handle uart mesh request message event

        :param opcode: int, mesh opcode
        :param command: bytes, mesh_command
        :return:     None
        """
        self.cli.print_standard_message("Received UART Mesh Message Request with opcode: 0x{:04x}".format(opcode))

    def uart_state_changed(self, state: UART_FSMState):
        """
        Handle uart state change event

        :param type: UART_FSMState(IntEnum), new state
        :return:     None
        """
        self.cli.print_important_message("UART state changed to: " + state.name)

    def uart_registered_models(self, model_ids: list):
        """
        Handles uart registered models update event

        :param model_ids:   list, list of registered model IDs
        :return:            None
        """
        output = str()
        for model_id in model_ids:
            output += "0x{:04x} ".format(model_id)

        self.cli.print_standard_message("UART registered models: " + output)

    def uart_firmware_version_update(self, firmware_version: bytes):
        """
        Handles firmware version update event

        :param model_ids:   bytes, new firmware version description
        :return:            None
        """
        self.cli.print_informative_message("UART Firmware Version: " + firmware_version.hex())

    def uart_uuid_update(self, uuid: bytes):
        """
        Handles device uuid update event

        :param model_ids:   bytes, new uuid
        :return:            None
        """
        self.cli.print_informative_message("UART UUID: " + uuid.hex())

    def uart_factory_reset_source(self, cause: FactoryResetSource):
        """
        Handle UART factory reset event

        :param cause:   FactoryResetSource(IntEnum), factory reset source
        :return:        None
        """
        self.cli.print_standard_message("UART Factory Reset! " + cause.name)

    def uart_soft_reset(self):
        """
        Handle UART soft reset event
        """
        self.cli.print_standard_message("UART Soft Reset!")

    def uart_attention_event(self, attention: AttentionEvent):
        """
        Handle UART attention event

        :param cause:   AttentionEvent(IntEnum), attention event description
        :return:        None
        """
        self.cli.print_important_message("UART Attention: " + attention.name)

    def uart_error(self, error: Error):
        """
        Handle UART error event

        :param cause:   Error(IntEnum), error event description
        :return:        None
        """
        self.cli.print_error_message("UART Error! " + error.name)
	
        if error == Error.NoLicenseForModelRegistration or error == Error.NoResourcesForModelRegistration:
            LOGGER.critical("Not recoverable error occurred: " + error.name)
            exit()

    def dfu_unexpected_message(self, type: UartCommand):
        """
        Handle DFU unexpected message event

        :param cause:   UartCommand, message opcode
        :return:        None
        """
        self.cli.print_error_message("Received unexpected DFU message")

    def dfu_state_changed(self, state: DFUState):
        """
        Handle DFU state change event

        :param cause:   DFUState(IntEnum), new DFU state
        :return:        None
        """
        # if state != DFUState.UploadPage:
        self.cli.print_important_message("DFU state changed to: " + state.name)

    def dfu_initialized(self, firmware_size: int, firmware_sha: bytes, app_data: bytes, initial: int = 0):
        """
        Handle DFU initialized event

        :param firmware_size:   int, firmware size
        :param firmware_sha:    int, firmware crc
        :param app_data:        bytes, received app data
        :return:                None
        """
        output = "DFU Initialized!\n"
        output += "Firmware size:\t{:d}\n".format(firmware_size)

        output += "Firmware SHA256:\t{:s}\n".format(firmware_sha.hex())
        output += "Received App data:\n"

        bytes_in_row = 16
        for i in range(int(len(app_data) / bytes_in_row)):
            output += app_data[i * bytes_in_row:(i + 1) * bytes_in_row].hex() + '\n'

        output += app_data[len(app_data) - (len(app_data) % bytes_in_row):].hex()

        self.cli.print_important_message(output)
        self.cli.start_progress_bar(firmware_size, initial)

    def dfu_page_stored(self, firmware_offset: int):
        """
        Handle DFU page stored event

        :param firmware_offset: int, firmware offset
        :return:                None
        """
        self.cli.update_progress_bar(firmware_offset)

    def dfu_update_complete(self):
        """
        Handle DFU update complete event
        """
        self.cli.stop_progress_bar()
        self.cli.print_important_message("DFU Update completed with success!")

    def dfu_failed(self):
        """
        Handle DFU update failed event
        """
        self.cli.stop_progress_bar()
        self.cli.print_error_message("DFU Update failed!")
