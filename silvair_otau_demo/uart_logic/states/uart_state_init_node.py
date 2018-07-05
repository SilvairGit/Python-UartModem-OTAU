from .uart_fsm_states import UART_FSMState
from .uart_state_generic import UARTGenericState

from silvair_uart_common_libs.message_types import ModemState
from silvair_uart_common_libs.messages import PongResponseMessage, StartNodeRequestMessage

class UARTInitNodeState(UARTGenericState):
    """
    UART Finite State Machine Init Node State.
    This state is connected with UART Modem Init Node state.
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
        Notify Event Mgr about changed state and send Start Node Request Message
        This is called when UART Finite State Machine changes state to this one.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        fsm_instance.event_mgr.uart_state_changed(ModemState.InitNode)

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
    def pong_response_message_event(fsm_instance, msg):
        """
        Do nothing.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def init_device_event_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Init Device Event should be sent in this state.
        Change state to Unknown.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)
        fsm_instance.change_state(UART_FSMState.Unknown)

    @staticmethod
    def create_instances_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Create Instances Response should be sent in this state.
        Change state to Unknown.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)
        fsm_instance.change_state(UART_FSMState.Unknown)

    @staticmethod
    def init_node_event_message_event(fsm_instance, msg):
        """
        Send Start Node Request Message in order to enter Node state
        This is called when UART Finite State Machine changes state to this one.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        fsm_instance.event_mgr.uart_registered_models(msg.model_ids)
        response = StartNodeRequestMessage()
        fsm_instance.dispatcher.send_message(response)

    @staticmethod
    def mesh_message_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Mesh Message Request should be sent in this state.
        Change state to Unknown.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)
        fsm_instance.change_state(UART_FSMState.Unknown)

    @staticmethod
    def mesh_message_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Mesh Message Request should be sent in this state.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)
        fsm_instance.change_state(UART_FSMState.Unknown)

    @staticmethod
    def start_node_response_message_event(fsm_instance, msg):
        """
        UART Modem is now in Node state. Change state to Node.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.change_state(UART_FSMState.Node)

    @staticmethod
    def factory_reset_response_message_event(fsm_instance, msg):
        """
        Do nothing.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def factory_reset_event_message_event(fsm_instance, msg):
        """
        Report factory reset and change state to Init Device

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def current_state_response_message_event(fsm_instance, msg):
        """
        Validate current state with received Current State Response

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        if msg.state != ModemState.InitNode:
            fsm_instance.event_mgr.uart_unexpected_message(msg.type)
            fsm_instance.change_state(UART_FSMState.Unknown)

    @staticmethod
    def error_message_event(fsm_instance, msg):
        """
        Report error and change state to Init Device

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_error(msg.error)

    @staticmethod
    def firmware_version_response_message_event(fsm_instance, msg):
        """
        Update Firmware Version

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_firmware_version_update(msg.firmware_version)

    @staticmethod
    def attention_event_message_event(fsm_instance, msg):
        """
         Report attention event

         :param fsm_instance:    UART Finite State Machine instance
         :param msg:             Received message
         :return:                None
         """
        fsm_instance.event_mgr.uart_attention_event(msg.attention)

    @staticmethod
    def soft_reset_request_message_event(fsm_instance, msg):
        """
        Do nothing.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def soft_reset_response_message_event(fsm_instance, msg):
        """
        Report soft reset event

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_soft_reset()

    @staticmethod
    def device_uuid_response_message_event(fsm_instance, msg):
        """
        Update Device UUID

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_uuid_update(msg.uuid)
