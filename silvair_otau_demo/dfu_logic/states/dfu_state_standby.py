import logging

from silvair_uart_common_libs.message_types import DFUStatus, DfuStatus

from .dfu_fsm_states import DFUState
from .dfu_state_generic import DFUGenericState

LOGGER = logging.getLogger(__name__)

class DFUStandbyState(DFUGenericState):
    """
    DFU Finite State Machine Standby State.
    In this state DFU process is not initialized.
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
        Notify Mgr about changed state.
        This is called when DFU Finite State Machine changes state to this one.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        fsm_instance.dfu_mgr.update_state(DFUState.Standby)
        fsm_instance.dfu_mgr.send_pre_validation_check_request()

    @staticmethod
    def dfu_init_request_message_event(fsm_instance, msg):
        """
        Initialize OTAU process

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        if fsm_instance.dfu_mgr.init_otau(msg):
            fsm_instance.change_state(DFUState.Upload)

    @staticmethod
    def dfu_state_request_message_event(fsm_instance, msg):
        """
        Respond with state.
        Change state to Standby.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.send_state_response(status=DFUStatus.DFU_SUCCESS, report_empty=True)

    @staticmethod
    def dfu_page_create_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Page Create Request Message should never be sent in this state.
        Change state to Standby.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.report_unexpected_message(msg.type)
        fsm_instance.dfu_mgr.drop_otau()

    @staticmethod
    def dfu_write_data_event_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Write Data Event Message should never be sent in this state.
        Change state to Standby.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.report_unexpected_message(msg.type)
        fsm_instance.dfu_mgr.drop_otau()

    @staticmethod
    def dfu_page_store_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Page Store Request Message should never be sent in this state.
        Change state to Standby.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.dfu_mgr.event_mgr.dfu_unexpected_message(msg.type)
        fsm_instance.dfu_mgr.drop_otau()

    @staticmethod
    def dfu_pre_validation_check_response_message_event(fsm_instance, msg):
        """
        Validate if OTAU is not already validated. If so drop.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        LOGGER.debug("Received pre validation status: " + msg.status.name)
        if msg.status == DfuStatus.InProgress:
            fsm_instance.dfu_mgr.drop_otau()

    @staticmethod
    def dfu_cancel_response_message_event(fsm_instance, msg):
        """
        Do nothing.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass
