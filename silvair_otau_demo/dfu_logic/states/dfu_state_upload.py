from silvair_uart_common_libs.message_types import DFUStatus

from .dfu_fsm_states import DFUState
from .dfu_state_generic import DFUGenericState


class DFUUploadState(DFUGenericState):
    """
    DFU Finite State Machine Upload State.
    In this state DFU process is initialized, but page saving process is not started
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
        Notify Event Mgr about changed state and clear memory.
        This is called when DFU Finite State Machine changes state to this one.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        fsm_instance.dfu_mgr.update_state(DFUState.Upload)

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
        Respond to State Request.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.send_state_response()

    @staticmethod
    def dfu_page_create_request_message_event(fsm_instance, msg):
        """
        Respond to create new page and change state to Upload Page.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.create_page(msg)
        fsm_instance.change_state(DFUState.UploadPage)

    @staticmethod
    def dfu_write_data_event_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Write Data Event Message should never be sent in this state.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.report_unexpected_message(msg.type)

    @staticmethod
    def dfu_page_store_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Page Store Request Message should never be sent in this state.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.send_page_store_response(status=DFUStatus.DFU_OPERATION_NOT_PERMITTED)
        fsm_instance.dfu_mgr.report_unexpected_message(msg.type)

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