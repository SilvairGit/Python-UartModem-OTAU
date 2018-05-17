class DFUGenericState:
    """
    DFU Finite State Machine Generic State.
    This class implements standard behaviour to some events.
    """

    @staticmethod
    def on_exit(fsm_instance):
        """
        No standard on exit behaviour. Overload this in derivative class.
        This is called when DFU Finite State Machine leaves this state.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def on_enter(fsm_instance):
        """
        No standard on start behaviour. Overload this in derivative class.
        This is called when DFU Finite State Machine changes state to this one.

        :param fsm_instance:    DFU Finite State Machine instance
        :return:                None
        """
        pass

    @staticmethod
    def dfu_init_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_init_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as DFU Init Response should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.dfu_unexpected_message(msg.type)

    @staticmethod
    def dfu_state_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_state_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as DFU State Response should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.dfu_unexpected_message(msg.type)

    @staticmethod
    def dfu_page_create_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_page_create_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Page Create Response should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.dfu_unexpected_message(msg.type)

    @staticmethod
    def dfu_write_data_event_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_page_store_request_message_event(fsm_instance, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_page_store_response_message_event(fsm_instance, msg):
        """
        Generate unexpected message event, as Page Store Response should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        fsm_instance.event_mgr.dfu_unexpected_message(msg.type)

    @staticmethod
    def dfu_pre_validation_check_request_message_event(self, msg):
        """
        Generate unexpected message event, as Pre Validation Check Request should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_pre_validation_check_request_message_event(self, msg)

    @staticmethod
    def dfu_pre_validation_check_response_message_event(self, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass

    @staticmethod
    def dfu_cancel_request_message_event(self, msg):
        """
        Generate unexpected message event, as Cancel Request should never be sent to MCU

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        self.current_state.dfu_cancel_request_message_event(self, msg)

    @staticmethod
    def dfu_cancel_response_message_event(self, msg):
        """
        No standard behaviour. Overload this in derivative class.

        :param fsm_instance:    DFU Finite State Machine instance
        :param msg:             Received message
        :return:                None
        """
        pass
