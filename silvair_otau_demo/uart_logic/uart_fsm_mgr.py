import logging

from silvair_uart_common_libs.message_types import FactoryResetSource, AttentionEvent, Error, ModelID, ModelDesc
from silvair_uart_common_libs.messages import FirmwareVersionRequestMessage, DeviceUUIDRequestMessage, GenericMessage, \
    UartCommand

from .states.uart_fsm_states import UART_FSMState
from .states.uart_state_device import UARTDeviceState
from .states.uart_state_init_device import UARTInitDeviceState
from .states.uart_state_init_node import UARTInitNodeState
from .states.uart_state_node import UARTNodeState
from .states.uart_state_unknown import UARTUnknownState

UART_STATE_CLASSES = {
    UART_FSMState.Unknown: UARTUnknownState,
    UART_FSMState.InitDevice: UARTInitDeviceState,
    UART_FSMState.Device: UARTDeviceState,
    UART_FSMState.InitNode: UARTInitNodeState,
    UART_FSMState.Node: UARTNodeState,
}

LOGGER = logging.getLogger(__name__)


class UART_FSM_Output:
    """
    Abstract UART Finite State Machine output class. Implement this to allow UART FSM talk TO modem.
    """

    def send_message(self, msg: GenericMessage):
        """
        Send message to modem

        :param msg: GenericMessage, message to be sent
        :return:    None
        """
        pass


class UART_FSM_EventMgr:
    """
    Abstract UART Finite State Machine event handling class. Implement this to allow UART FSM output events.
    """

    def uart_unexpected_message(self, type: UartCommand):
        """
        Handle uart unexpected message event

        :param type: UartCommand (IntEnum), message opcode
        :return:     None
        """
        pass

    def uart_mesh_request(self, opcode: int, command: bytes):
        """
        Handle uart mesh request message event

        :param opcode: int, mesh opcode
        :param command: bytes, mesh command
        :return:     None
        """
        pass

    def uart_state_changed(self, state: UART_FSMState):
        """
        Handle uart state change event

        :param type: UART_FSMState(IntEnum), new state
        :return:     None
        """
        pass

    def uart_registered_models(self, model_ids: list):
        """
        Handle uart registered models update event

        :param model_ids:   list, list of registered model IDs
        :return:            None
        """
        pass

    def uart_firmware_version_update(self, firmware_version: bytes):
        """
        Handle firmware version update event

        :param model_ids:   bytes, new firmware version description
        :return:            None
        """
        pass

    def uart_uuid_update(self, uuid: bytes):
        """
        Handle device uuid update event

        :param model_ids:   bytes, new uuid
        :return:            None
        """
        pass

    def uart_factory_reset_source(self, cause: FactoryResetSource):
        """
        Handle UART factory reset event

        :param cause:   FactoryResetSource(IntEnum), factory reset source
        :return:        None
        """
        pass

    def uart_soft_reset(self):
        """
        Handle UART soft reset event
        """
        pass

    def uart_attention_event(self, attention: AttentionEvent):
        """
        Handle UART attention event

        :param cause:   AttentionEvent(IntEnum), attention event description
        :return:        None
        """
        pass

    def uart_error(self, error: Error):
        """
        Handle UART error event

        :param cause:   Error(IntEnum), error event description
        :return:        None
        """
        pass


class UART_FSM:
    """
    UART Finite State Machine. Handles UART Modem states and basic incoming UART commands.
    """

    def __init__(self,
                 sender: UART_FSM_Output,
                 event_mgr: UART_FSM_EventMgr,
                 init_state: UART_FSMState = UART_FSMState.Unknown,
                 default_models = (ModelDesc(ModelID(0x1001)),)):
        """
        UART Finite State Machine initialization.
        Note that self.dispatcher and self.event_mgr has to be assigned manually

        :param sender:      UART_FSM_Output, class for outputing UART messages
        :param event_mgr:   UART_FSM_EventMgr, class for outputing events
        :param model:       tuple, models to register
        :param init_state:  UART_FSMState, optional, Initial UART Finite State Machine state
        """
        assert sender is not None
        assert event_mgr is not None

        self.current_state_id = init_state
        self.current_state = UART_STATE_CLASSES[init_state]
        self.dispatcher = sender
        self.event_mgr = event_mgr

        LOGGER.debug("Number of models to register: {:d}".format(len(default_models)))
        self.default_models_to_register = default_models

        LOGGER.info('UART_FSM initialized')

    def start(self):
        """
        Start UART Finite State Machine.

        :return: None
        """
        self.current_state.on_enter(self)

        msg = FirmwareVersionRequestMessage()
        self.dispatcher.send_message(msg)
        msg = DeviceUUIDRequestMessage()
        self.dispatcher.send_message(msg)

        LOGGER.info('UART_FSM started')

    def change_state(self, new_state: UART_FSMState):
        """
        Change UART Finite State Machine state

        :param new_state:   UART_FSMState, new state
        :return:            None
        """
        self.current_state.on_exit(self)
        self.current_state_id = new_state
        self.current_state = UART_STATE_CLASSES[new_state]
        self.current_state.on_enter(self)

        LOGGER.info('UART_FSM changed state to: ' + self.current_state_id.name)

    def ping_request_message_event(self, msg):
        """
        Standard Ping Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.ping_request_message_event(self, msg)

    def pong_response_message_event(self, msg):
        """
        Standard Pong Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.pong_response_message_event(self, msg)

    def init_device_event_message_event(self, msg):
        """
        Standard Init Device Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.init_device_event_message_event(self, msg)

    def create_instances_request_message_event(self, msg):
        """
        Standard Create Instances Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.create_instances_request_message_event(self, msg)

    def create_instances_response_message_event(self, msg):
        """
        Standard Create Instances Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.create_instances_response_message_event(self, msg)

    def init_node_event_message_event(self, msg):
        """
        Standard Init Node Event Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.init_node_event_message_event(self, msg)

    def mesh_message_request_message_event(self, msg):
        """
        Standard Mesh Message Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.mesh_message_request_message_event(self, msg)

    def mesh_message_response_message_event(self, msg):
        """
        Standard Mesh Message Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.mesh_message_response_message_event(self, msg)

    def opcode_error_message_event(self, msg):
        """
        Standard Error Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.opcode_error_message_event(self, msg)

    def start_node_request_message_event(self, msg):
        """
        Standard Start Node Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.start_node_request_message_event(self, msg)

    def start_node_response_message_event(self, msg):
        """
        Standard Start Node Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.start_node_response_message_event(self, msg)

    def factory_reset_request_message_event(self, msg):
        """
        Standard Factory Reset Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.factory_reset_request_message_event(self, msg)

    def factory_reset_response_message_event(self, msg):
        """
        Standard Factory Reset Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.factory_reset_response_message_event(self, msg)

    def factory_reset_event_message_event(self, msg):
        """
        Standard Factory Reset Event Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.factory_reset_event_message_event(self, msg)

    def current_state_request_message_event(self, msg):
        """
        Standard Current State Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.current_state_request_message_event(self, msg)

    def current_state_response_message_event(self, msg):
        """
        Standard Current State Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.current_state_response_message_event(self, msg)

    def error_message_event(self, msg):
        """
        Standard Error Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.error_message_event(self, msg)

    def firmware_version_request_message_event(self, msg):
        """
        Standard Firmware Version Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.firmware_version_request_message_event(self, msg)

    def firmware_version_response_message_event(self, msg):
        """
        Standard Firmware Version Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.firmware_version_response_message_event(self, msg)

    def sensor_update_request_message_event(self, msg):
        """
        Standard Sensor Update Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.sensor_update_request_message_event(self, msg)

    def attention_event_message_event(self, msg):
        """
        Standard Attention Event Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.attention_event_message_event(self, msg)

    def soft_reset_request_message_event(self, msg):
        """
        Standard Soft Reset Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.soft_reset_request_message_event(self, msg)

    def soft_reset_response_message_event(self, msg):
        """
        Standard Soft Reset Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.soft_reset_response_message_event(self, msg)

    def sensor_update_response_message_event(self, msg):
        """
        Standard Sensor Update Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.sensor_update_response_message_event(self, msg)

    def device_uuid_request_message_event(self, msg):
        """
        Standard Device UUID Request Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.device_uuid_request_message_event(self, msg)

    def device_uuid_response_message_event(self, msg):
        """
        Standard Device UUID Response Message event handler

        :param msg:             Received message
        :return:                None
        """
        self.current_state.device_uuid_response_message_event(self, msg)
