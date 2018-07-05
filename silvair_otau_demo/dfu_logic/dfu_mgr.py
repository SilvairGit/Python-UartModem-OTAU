import binascii
import logging

from silvair_uart_common_libs.message_types import DFUStatus
from silvair_uart_common_libs.messages import GenericMessage, UartCommand, DfuInitResponseMessage, \
    DfuStatusResponseMessage, DfuPageCreateResponseMessage, DfuPageStoreResponseMessage, DfuCancelRequestMessage, \
    DfuStateRequestMessage

from ..console_out import ConsoleOut
from .dfu_fail_mgr import DFUFailMgr
from .dfu_fsm import DFU_FSM
from .dfu_memory import DFUMemory
from .dfu_nvm import DFU_NVM
from .states.dfu_fsm_states import DFUState

LOGGER = logging.getLogger(__name__)


class DFU_FSM_Output:
    """
    Abstract DFU Finite State Machine output class. Implement this to allow DFU FSM talk TO modem.
    """

    def send_message(self, msg: GenericMessage):
        """
        Send message to modem

        :param msg: GenericMessage, message to be sent
        :return:    None
        """
        pass


class DFU_FSM_EventMgr:
    """
    Abstract DFU Finite State Machine event handling class. Implement this to allow DFU FSM output events.
    """

    def dfu_unexpected_message(self, type: UartCommand):
        """
        Handle DFU unexpected message event

        :param cause:   UartCommand, message opcode
        :return:        None
        """
        pass

    def dfu_state_changed(self, state: DFUState):
        """
        Handle DFU state change event

        :param cause:   DFUState(IntEnum), new DFU state
        :return:        None
        """
        pass

    def dfu_initialized(self, firmware_size: int, firmware_crc: int, app_data: bytes, initial: int):
        """
        Handle DFU initialized event

        :param firmware_size:   int, firmware size
        :param firmware_crc:    int, firmware crc
        :param app_data:        bytes, received app data
        :param initial:         int, initial progress
        :return:                None
        """
        pass

    def dfu_page_stored(self, firmware_offset: int):
        """
        Handle DFU page stored event

        :param firmware_offset: int, firmware offset
        :return:                None
        """
        pass

    def dfu_update_complete(self):
        """
        Handle DFU update complete event
        """
        pass

    def dfu_failed(self):
        """
        Handle DFU update failed event
        """
        pass


class DFU_Mgr:
    def __init__(self,
                 sender: DFU_FSM_Output,
                 event_mgr: DFU_FSM_EventMgr,
                 memory: DFUMemory,
                 fail_mgr: DFUFailMgr,
                 nvm: str,
                 expected_app_data: bytes):
        """
        DFU Manager initialization

        :param sender:                  DFU_FSM_Output, UART Sender object
        :param event_mgr:               DFU_FSM_EventMgr, Event manager object
        :param memory:                  DFU_FSM_Memory, Mock memory object
        :param nvm:                     str, NVM file path
        :param expected_app_data:       bytes, expected app data, ignored if None
        """

        assert sender is not None
        assert event_mgr is not None
        assert memory is not None

        self.dispatcher = sender
        self.event_mgr = event_mgr
        self.dfu_memory = memory
        self.fail_mgr = fail_mgr
        self.expected_app_data = expected_app_data
        self.nvm = DFU_NVM(nvm)

        self.initial_state_id = self.nvm.get('current_state_id')
        self.firmware_image_size = self.nvm.get('firmware_image_size')
        self.firmware_image_sha256 = self.nvm.get('firmware_image_sha256')

        if not self.firmware_image_size:
            self.update_firmware_size(0)

        if not self.firmware_image_sha256:
            self.update_firmware_sha256(b'')
        else:
            self.firmware_image_sha256 = bytes.fromhex(self.firmware_image_sha256)

        LOGGER.debug("initial state: {}".format(str(self.initial_state_id)))

        if self.initial_state_id is not None:
            self.initial_state_id = DFUState(self.initial_state_id)

            LOGGER.debug("initial state: {:s}".format(str(self.initial_state_id.name)))
            if self.initial_state_id == DFUState.Upload or self.initial_state_id == DFUState.UploadPage:

                self.event_mgr.dfu_initialized(self.firmware_image_size,
                                               self.firmware_image_sha256,
                                               self.dfu_memory.app_data_memory,
                                               self.dfu_memory.firmware_offset)
            self.dfu_fsm = DFU_FSM(self, self.initial_state_id)
        else:
            self.dfu_fsm = DFU_FSM(self)

        LOGGER.info("DFU_Mgr initialized")

    def update_firmware_size(self, firmware_size: int):
        """
        Update OTAU firmware size

        :param firmware_size:   int, New size
        :return:                None
        """
        self.firmware_image_size = firmware_size
        self.nvm.update('firmware_image_size', firmware_size)

    def update_firmware_sha256(self, firmware_sha: bytes):
        """
        Update OTAU firmware SHA

        :param firmware_size:   bytes, New SHA
        :return:                None
        """
        self.firmware_image_sha256 = firmware_sha
        self.nvm.update('firmware_image_sha256', firmware_sha.hex())

    def update_state(self, new_state_id: DFUState):
        """
        Update OTAU state

        :param new_state_id:    DFUState, New state
        :return:                None
        """
        self.current_state_id = new_state_id
        self.nvm.update('current_state_id', new_state_id.value)
        self.event_mgr.dfu_state_changed(new_state_id)

    def init_otau(self, msg):
        """
        Initialize DFU process.

        :param msg:             Received message
        :return:                True if success, False otherwise
        """
        self.dfu_memory.clear()
        self.update_firmware_size(0)
        self.update_firmware_sha256(b'')

        fault = self.fail_mgr.on_pre_validation_fault()
        if fault is not None:
            LOGGER.debug("Failure manager called fault: %s", fault)

            if fault.should_send_response():
                self.send_dfu_init_response(status=fault.status)

            self.event_mgr.dfu_failed()
            return False

        if self.expected_app_data is not None and self.expected_app_data != msg.app_data:
            self.send_dfu_init_response(status=DFUStatus.DFU_INVALID_OBJECT)

            str_expected = binascii.hexlify(self.expected_app_data).decode("ascii")
            str_got = binascii.hexlify(msg.app_data).decode("ascii")

            ConsoleOut.print_error_message("Invalid app_data! expected: '{}', got: '{}'".format(str_expected, str_got))
            return False

        try:
            self.dfu_memory.set_app_data_memory_size(msg.app_data_length)
            self.dfu_memory.write_app_data(msg.app_data)
            self.dfu_memory.set_firmware_memory_size(msg.firmware_size)
        except Exception as err:
            self.send_dfu_init_response(status=DFUStatus.DFU_INSUFFICIENT_RESOURCES)
            ConsoleOut.print_error_message("Initializing memory failed: {}".format(str(err)))
            LOGGER.debug("Initializing memory failed: %s", str(err))
            return False

        self.update_firmware_size(msg.firmware_size)
        self.update_firmware_sha256(msg.firmware_sha256)

        self.send_dfu_init_response(status=DFUStatus.DFU_SUCCESS)
        self.event_mgr.dfu_initialized(self.firmware_image_size,
                                       self.firmware_image_sha256,
                                       self.dfu_memory.app_data_memory,
                                       0)

        LOGGER.info("DFU process initialized")

        return True

    def send_state_response(self, status: DFUStatus = DFUStatus.DFU_SUCCESS, report_empty: bool = False):
        """
        Send state response message.

        :param status:          DFUStatus, status
        :param report_empty:    bool, if True firmware offset and firmware crc will be reported 0
        :return:                None
        """
        fault = self.fail_mgr.after_pre_validation_fault()
        if fault is not None:
            LOGGER.debug("Failure manager called fault: %s", fault)

            if fault.should_send_response():
                self.send_dfu_init_response(status=fault.status)

            return False

        response = DfuStatusResponseMessage()
        response.status = status  # TODO
        response.supported_page_size = self.dfu_memory.supported_page_size

        if report_empty:
            response.firmware_offset = 0
            response.firmware_crc = 0
        else:
            response.firmware_offset = self.dfu_memory.firmware_offset + self.dfu_memory.firmware_page_offset
            response.firmware_crc = self.dfu_memory.calc_firmware_crc()

        self.dispatcher.send_message(response)

    def send_page_create_response(self, status: DFUStatus = DFUStatus.DFU_SUCCESS):
        """
        Send page create response.

        :param status:  DFUStatus, status
        :return:        None
        """
        response = DfuPageCreateResponseMessage()
        response.status = status
        self.dispatcher.send_message(response)

    def send_page_store_response(self, status: DFUStatus = DFUStatus.DFU_SUCCESS):
        """
        Send page store response.

        :param status:  DFUStatus, status
        :return:        None
        """
        response = DfuPageStoreResponseMessage()
        response.status = status
        self.dispatcher.send_message(response)

    def send_dfu_init_response(self, status: DFUStatus = DFUStatus.DFU_SUCCESS):
        """
        Send dfu init response.

        :param status:  DFUStatus, status
        :return:        None
        """
        response = DfuInitResponseMessage()
        response.status = status
        self.dispatcher.send_message(response)

    def send_pre_validation_check_request(self):
        """
        Send pre validation check request
        """
        request = DfuStateRequestMessage()
        self.dispatcher.send_message(request)

    def create_page(self, msg):
        """
        Create page in memory and send page create response

        :param msg:     Received message
        :return:        None
        """
        fault = self.fail_mgr.on_page_create_request_fault()
        if fault is not None:
            LOGGER.debug("Failure manager called fault: %s", fault)

            if fault.should_send_response():
                self.send_page_create_response(status=fault.status)

            return False

        self.dfu_memory.create_page(msg.requested_page_size)
        self.send_page_create_response(status=DFUStatus.DFU_SUCCESS)

    def process_write_data(self, data):
        """
        Write data portion.

        :param data: Received data
        :return:     None
        """
        self.dfu_memory.write_data(data)

    def page_store(self):
        """
        Validate and store page in memory

        :return:    True if success, False otherwise
        """
        fault = self.fail_mgr.on_page_store_request_fault()
        if fault is not None:
            LOGGER.debug("Failure manager called fault: %s", fault)

            if fault.should_send_response():
                self.send_page_store_response(status=fault.status)

            return False

        try:
            self.dfu_memory.page_store()
        except Exception as e:
            self.send_page_store_response(status=DFUStatus.DFU_INVALID_OBJECT)

            LOGGER.debug("Storing page failed: " + str(e))
            return False

        if self.dfu_memory.firmware_offset == self.firmware_image_size:
            if self.dfu_memory.calc_firmware_sha256() == self.firmware_image_sha256:
                fault = self.fail_mgr.on_post_validation_fault()
                if fault is not None:
                    LOGGER.debug("Failure manager called fault: %s", fault)

                    if fault.should_send_response():
                        self.send_page_store_response(status=DFUStatus.DFU_INVALID_OBJECT)

                    self.event_mgr.dfu_failed()
                    return False

                self.send_page_store_response(status=DFUStatus.DFU_FIRMWARE_SUCCESSFULLY_UPDATED)

                self.event_mgr.dfu_page_stored(self.dfu_memory.firmware_offset)
                self.event_mgr.dfu_update_complete()

                LOGGER.info("Firmware successfully updated")
                return False

            else:
                self.send_page_store_response(status=DFUStatus.DFU_INVALID_OBJECT)
                self.event_mgr.dfu_failed()
                return False
        else:
            self.send_page_store_response(status=DFUStatus.DFU_SUCCESS)
            self.event_mgr.dfu_page_stored(self.dfu_memory.firmware_offset)

            LOGGER.debug("Page store success")
            return True

    def drop_otau(self):
        """
        Drop ongoing OTAU process
        """
        request = DfuCancelRequestMessage()
        self.dispatcher.send_message(request)

    def report_unexpected_message(self, msg_type):
        """
        Report unexpected message

        :param msg_type:    Received message type
        :return:            None
        """
        self.event_mgr.dfu_unexpected_message(msg_type)

    def report_dfu_fail(self):
        """
        Report DFU fail
        """
        self.event_mgr.dfu_failed()
