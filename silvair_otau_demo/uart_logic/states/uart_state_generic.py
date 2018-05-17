class UARTGenericState:
    """
    UART Finite State Machine Generic State.
    This class implements standard behaviour to some events.
    """

    @staticmethod
    def on_exit(fsm_instance):
        """
        No standard on exit behaviour. Overload this in derivative class.
        This is called when UART Finite State Machine leaves this state.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def on_enter(fsm_instance):
        """
        No standard on start behaviour. Overload this in derivative class.
        This is called when UART Finite State Machine changes state to this one.

        :param fsm_instance:    UART Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def ping_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def pong_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def init_device_event_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def create_instances_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Create Instance Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def create_instances_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def init_node_event_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def mesh_message_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def mesh_message_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def opcode_error_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Opcode Error should be sent

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def start_node_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Start Node Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def start_node_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def factory_reset_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Factory Reset Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def factory_reset_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def factory_reset_event_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def mesh_message_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Mesh Message Response should never be sent

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def current_state_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Current State Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def current_state_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def error_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def firmware_version_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Firmware Version Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def firmware_version_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def sensor_update_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Sensor Update Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def attention_event_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def soft_reset_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def soft_reset_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def sensor_update_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Sensor Update Request should never be sent

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def device_uuid_request_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Device UUID Request should never be sent to MCU

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.uart_unexpected_message(msg.type)

    @staticmethod
    def device_uuid_response_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    UART Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass
