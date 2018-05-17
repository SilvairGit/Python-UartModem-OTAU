from .uart_fsm_states import UART_FSMState
from .uart_state_generic import UARTGenericState

from silvair_uart_common_libs.message_types import ModemState
from silvair_uart_common_libs.messages import CurrentStateRequestMessage, PongResponseMessage

class UARTUnknownState(UARTGenericState):
    """
    UART Finite State Machine Device State.
    This state is connected with UART Modem Device FSM and is used to determine what is going on
    """

    @staticmethod
    def on_exit(fsm_instance):
        """
        Do nothing on exit.
        This is called when UART Finite State Machine leaves this state.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def on_enter(fsm_instance):
        """
        Notify Event Mgr about changed state and ask UART Modem about current state.
        This is called when UART Finite State Machine changes state to this one.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        fsm_instance.event_mgr.uart_state_changed(ModemState.Unknown)

        request = CurrentStateRequestMessage()
        fsm_instance.dispatcher.send_message(request)

    @staticmethod
    def ping_request_message_event(fsm_instance, msg):
        """
        Respond to ping message.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        response = PongResponseMessage()
        response.data = msg.data
        fsm_instance.dispatcher.send_message(response)

    @staticmethod
    def init_device_event_message_event(fsm_instance, msg):
        """
        Assume state init device.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.change_state(UART_FSMState.InitDevice)

    @staticmethod
    def init_node_event_message_event(fsm_instance, msg):
        """
        Assume state init node.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.change_state(UART_FSMState.InitNode)

    @staticmethod
    def current_state_response_message_event(fsm_instance, msg):
        """
        Enter new state accordingly to received Current State Response

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        if msg.state == ModemState.InitDevice:
            fsm_instance.change_state(UART_FSMState.InitDevice)
        elif msg.state == ModemState.Device:
            fsm_instance.change_state(UART_FSMState.Device)
        elif msg.state == ModemState.InitNode:
            fsm_instance.change_state(UART_FSMState.InitNode)
        elif msg.state == ModemState.Node:
            fsm_instance.change_state(UART_FSMState.Node)
