from .states.dfu_fsm_states import DFUState

from .states.dfu_state_standby import DFUStandbyState
from .states.dfu_state_upload import DFUUploadState
from .states.dfu_state_upload_page import DFUUploadPageState

DFU_STATE_CLASSES = {
    DFUState.Standby: DFUStandbyState,
    DFUState.Upload: DFUUploadState,
    DFUState.UploadPage: DFUUploadPageState,
}


class DFU_FSM:
    """
    DFU Finite State Machine. Handles DFU states and incoming UART commands involving DFU.
    """

    def __init__(self,
                 dfu_mgr,
                 init_state: DFUState = DFUState.Standby):
        """

        DFU Finite State Machine initialization.

        :param init_state:  DFUState, optional, Initial UART Finite State Machine state
        """
        self.current_state_id = init_state
        self.current_state = None
        self.dfu_mgr = dfu_mgr

        self.current_state_id = DFUState(init_state)
        self.current_state = DFU_STATE_CLASSES[self.current_state_id]

    def start(self):
        """
        Start DFU Finite State Machine.

        :return: None
        """
        self.current_state.on_enter(self)

    def change_state(self, new_state: DFUState):
        """
        Change DFU Finite State Machine state

        :param new_state:   DFUState, new state
        :return:            None
        """
        if self.current_state:
            self.current_state.on_exit(self)
        new_state = DFUState(new_state)
        self.current_state_id = new_state
        self.current_state = DFU_STATE_CLASSES[new_state]
        self.current_state.on_enter(self)

    def dfu_init_request_message_event(self, msg):
        """
        Standard DFU Init Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_init_request_message_event(self, msg)

    def dfu_init_response_message_event(self, msg):
        """
        Standard DFU Init Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_init_response_message_event(self, msg)

    def dfu_state_request_message_event(self, msg):
        """
        Standard DFU State Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_state_request_message_event(self, msg)

    def dfu_state_response_message_event(self, msg):
        """
        Standard DFU State Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_state_response_message_event(self, msg)

    def dfu_page_create_request_message_event(self, msg):
        """
        Standard DFU Page Create Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_page_create_request_message_event(self, msg)

    def dfu_page_create_response_message_event(self, msg):
        """
        Standard Page Create Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_page_create_response_message_event(self, msg)

    def dfu_write_data_event_message_event(self, msg):
        """
        Standard Write Data Event Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_write_data_event_message_event(self, msg)

    def dfu_page_store_request_message_event(self, msg):
        """
        Standard Page Store Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_page_store_request_message_event(self, msg)

    def dfu_page_store_response_message_event(self, msg):
        """
        Standard Page Store Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_page_store_response_message_event(self, msg)

    def dfu_pre_validation_check_request_message_event(self, msg):
        """
        Standard Pre Validation Check Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_pre_validation_check_request_message_event(self, msg)

    def dfu_pre_validation_check_response_message_event(self, msg):
        """
        Standard Pre Validation Check Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_pre_validation_check_response_message_event(self, msg)

    def dfu_cancel_request_message_event(self, msg):
        """
        Standard Cancel Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_cancel_request_message_event(self, msg)

    def dfu_cancel_response_message_event(self, msg):
        """
        Standard Cancel Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_cancel_response_message_event(self, msg)
