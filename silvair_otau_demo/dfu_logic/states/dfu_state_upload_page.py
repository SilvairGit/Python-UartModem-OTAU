from .dfu_fsm_states import DFUState
from .dfu_state_generic import DFUGenericState


class DFUUploadPageState(DFUGenericState):
    """
    DFU Finite State Machine Upload Page State.
    In this state DFU process is initialized, and page saving process is in progress
    """

    @staticmethod
    def on_exit(fsm_instance):
        """
        Do nothing on exit.
        This is called when DFU Finite State Machine leaves this state.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def on_enter(fsm_instance):
        """
        Notify Event Mgr about changed state.
        This is called when DFU Finite State Machine changes state to this one.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        fsm_instance.dfu_mgr.update_state(DFUState.UploadPage)

    @staticmethod
    def dfu_init_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Init Request Message should never be sent in this state.
        Change state to Standby. Forward message.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.report_unexpected_message(msg.type)
        fsm_instance.dfu_mgr.report_dfu_fail()
        fsm_instance.change_state(DFUState.Standby)
        fsm_instance.dfu_init_request_message_event(msg)

    @staticmethod
    def dfu_state_request_message_event(fsm_instance, msg):
        """
        Respond with state

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.send_state_response()

    @staticmethod
    def dfu_page_create_request_message_event(fsm_instance, msg):
        """
        Change state to Upload and forward message.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.change_state(DFUState.Upload)
        fsm_instance.dfu_page_create_request_message_event(msg)

    @staticmethod
    def dfu_write_data_event_message_event(fsm_instance, msg):
        """
        Write data to memory.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.process_write_data(msg.data)

    @staticmethod
    def dfu_page_store_request_message_event(fsm_instance, msg):
        """
        Handle page store event. Change state to Upload (if success) or Standby (if failed)

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        if fsm_instance.dfu_mgr.page_store():
            fsm_instance.change_state(DFUState.Upload)
        else:
            fsm_instance.change_state(DFUState.Standby)

    @staticmethod
    def dfu_pre_validation_check_response_message_event(fsm_instance, msg):
        """
        Validate if OTAU is already validated.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_cancel_response_message_event(fsm_instance, msg):
        """
        Do nothing.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.report_dfu_fail()
        fsm_instance.change_state(DFUState.Standby)
