import unittest
from unittest.mock import Mock

from silvair_uart_common_libs.message_types import DFUStatus
from silvair_uart_common_libs.messages import DfuInitRequestMessage, DfuStatusResponseMessage, DfuInitResponseMessage, \
    DfuStatusRequestMessage, DfuPageCreateRequestMessage, DfuPageCreateResponseMessage, DfuWriteDataEventMessage, \
    DfuPageStoreRequestMessage, DfuPageStoreResponseMessage

from silvair_otau_demo.dfu_logic.dfu_fsm import DFU_FSM
from silvair_otau_demo.dfu_logic.states.dfu_fsm_states import DFUState


class DFU_FSMTests(unittest.TestCase):
    def setUp(self):
        self.dfu_mgr_mock = Mock()

        self.dfu_fsm = DFU_FSM(self.dfu_mgr_mock)

        self.dfu_fsm.start()
        self.dfu_mgr_mock.update_state.assert_called_once_with(DFUState.Standby)
        self.dfu_mgr_mock.update_state.reset_mock()

    def reset_mock(self):
        self.dfu_mgr_mock.reset_mock()

    def test_status_in_standby(self):
        msg = DfuStatusRequestMessage()
        self.dfu_fsm.dfu_state_request_message_event(msg)

        self.dfu_mgr_mock.send_state_response.assert_called_once_with(status=DFUStatus.DFU_SUCCESS, report_empty=True)
        self.dfu_mgr_mock.send_message.reset_mock()
        self.assertEquals(self.dfu_fsm.current_state_id, DFUState.Standby)

    def test_dfu_init(self):
        msg = DfuInitRequestMessage()
        msg.firmware_size = 160
        msg.firmware_crc = 1234
        msg.app_data_length = 16
        msg.app_data = b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"

        self.dfu_fsm.dfu_init_request_message_event(msg)

        self.dfu_mgr_mock.init_otau.assert_called_once_with(msg)

        self.assertEquals(self.dfu_fsm.current_state_id, DFUState.Upload)

    def test_dfu_page_create(self):
        self.test_dfu_init()

        msg = DfuPageCreateRequestMessage()
        msg.requested_page_size = 16

        self.dfu_fsm.dfu_page_create_request_message_event(msg)

        self.dfu_mgr_mock.create_page.assert_called_once_with(msg)
        self.assertEquals(self.dfu_fsm.current_state_id, DFUState.UploadPage)

    def test_dfu_write_page(self):
        self.test_dfu_init()

        write_msg = DfuWriteDataEventMessage()
        write_msg.data_len = 4
        write_msg.data = b"\xAA\xBB\xCC\xDD"

        for _ in range(9):

            msg = DfuPageCreateRequestMessage()
            msg.requested_page_size = 16

            self.dfu_fsm.dfu_page_create_request_message_event(msg)

            self.dfu_mgr_mock.create_page.assert_called_once_with(msg)
            self.dfu_mgr_mock.create_page.reset_mock()
            self.assertEquals(self.dfu_fsm.current_state_id, DFUState.UploadPage)

            for __ in range(4):
                self.assertEquals(self.dfu_fsm.current_state_id, DFUState.UploadPage)
                self.dfu_fsm.dfu_write_data_event_message_event(write_msg)

            msg = DfuPageStoreRequestMessage()
            self.dfu_fsm.dfu_page_store_request_message_event(msg)
            self.assertEquals(self.dfu_fsm.current_state_id, DFUState.Upload)

            self.dfu_mgr_mock.page_store.assert_called()

        msg = DfuPageCreateRequestMessage()
        msg.requested_page_size = 16

        self.dfu_fsm.dfu_page_create_request_message_event(msg)

        self.dfu_mgr_mock.create_page.assert_called_once_with(msg)
        self.assertEquals(self.dfu_fsm.current_state_id, DFUState.UploadPage)

        for __ in range(4):
            self.assertEquals(self.dfu_fsm.current_state_id, DFUState.UploadPage)
            self.dfu_fsm.dfu_write_data_event_message_event(write_msg)

        self.dfu_mgr_mock.page_store = Mock(return_value=False)

        msg = DfuPageStoreRequestMessage()
        self.dfu_fsm.dfu_page_store_request_message_event(msg)
        self.assertEquals(self.dfu_fsm.current_state_id, DFUState.Standby)
