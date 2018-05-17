import unittest
from unittest.mock import Mock

from silvair_uart_common_libs.message_types import ModemState, ModelID, ModelDesc
from silvair_uart_common_libs.messages import PingRequestMessage, PongResponseMessage, CurrentStateResponseMessage, \
    InitDeviceEventMessage, \
    CreateInstancesRequestMessage, CreateInstancesResponseMessage, InitNodeEventMessage, StartNodeRequestMessage, \
    StartNodeResponseMessage
from silvair_otau_demo.uart_logic.uart_fsm_mgr import UART_FSM
from silvair_otau_demo.uart_logic.states.uart_fsm_states import UART_FSMState


class UART_FSMTests(unittest.TestCase):
    def setUp(self):
        self.sender_mock = Mock()
        self.event_mgr_mock = Mock()

        self.uart_fsm = UART_FSM(self.sender_mock, self.event_mgr_mock, default_models=(ModelDesc(ModelID(0x1300)),))

        self.uart_fsm.start()

        self.sender_mock.send_message.assert_called()
        self.sender_mock.send_message.reset_mock()
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.Unknown)
        self.event_mgr_mock.uart_state_changed.reset_mock()

    def reset_mock(self):
        self.sender_mock.send_message.reset_mock()
        self.event_mgr_mock.uart_state_changed.reset_mock()

    def test_ping_pong(self):
        msg = PingRequestMessage()
        msg.data = 0xAA
        self.uart_fsm.ping_request_message_event(msg)

        msg = PongResponseMessage()
        msg.data = 0xAA
        self.sender_mock.send_message.assert_called_once_with(msg)

    def test_unknown_to_init_device(self):
        msg = CurrentStateResponseMessage()
        msg.state = ModemState.InitDevice
        self.uart_fsm.current_state_response_message_event(msg)

        self.assertEquals(UART_FSMState.InitDevice, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.InitDevice)

    def test_unknown_to_device(self):
        msg = CurrentStateResponseMessage()
        msg.state = ModemState.Device
        self.uart_fsm.current_state_response_message_event(msg)

        self.assertEquals(UART_FSMState.Device, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.Device)

    def test_unknown_to_init_node(self):
        msg = CurrentStateResponseMessage()
        msg.state = ModemState.InitNode
        self.uart_fsm.current_state_response_message_event(msg)

        self.assertEquals(UART_FSMState.InitNode, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.InitNode)

    def test_unknown_to_node(self):
        msg = CurrentStateResponseMessage()
        msg.state = ModemState.Node
        self.uart_fsm.current_state_response_message_event(msg)

        self.assertEquals(UART_FSMState.Node, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.Node)

    def test_init_device_to_device(self):
        self.test_unknown_to_init_device()
        self.reset_mock()

        msg = InitDeviceEventMessage()
        model_id = ModelID(0x1300)
        msg.model_ids = [model_id]

        self.uart_fsm.init_device_event_message_event(msg)

        msg = CreateInstancesRequestMessage()
        model_id = ModelDesc(ModelID(0x1300))
        msg.model_descs = (model_id, )

        self.sender_mock.send_message.assert_called_once_with(msg)

        msg = CreateInstancesResponseMessage()
        model_id = ModelID(0x1300)
        msg.model_ids = [model_id]

        self.uart_fsm.create_instances_response_message_event(msg)

        self.assertEquals(UART_FSMState.Device, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.Device)

    def test_device_to_init_node(self):
        self.test_init_device_to_device()
        self.reset_mock()

        msg = InitNodeEventMessage()
        model_id = ModelID(0x1300)
        msg.model_ids = [model_id]

        self.uart_fsm.init_node_event_message_event(msg)

        self.assertEquals(UART_FSMState.InitNode, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.InitNode)

    def test_init_node_to_node(self):
        self.test_device_to_init_node()
        self.event_mgr_mock.uart_state_changed.reset_mock()

        msg = InitNodeEventMessage()
        model_id = ModelID(0x1300)
        msg.model_ids = [model_id]

        self.uart_fsm.init_node_event_message_event(msg)

        msg = StartNodeRequestMessage()
        self.sender_mock.send_message.assert_called_once_with(msg)
        self.reset_mock()

        msg = StartNodeResponseMessage()
        self.uart_fsm.start_node_response_message_event(msg)

        self.assertEquals(UART_FSMState.Node, self.uart_fsm.current_state_id)
        self.event_mgr_mock.uart_state_changed.assert_called_once_with(ModemState.Node)