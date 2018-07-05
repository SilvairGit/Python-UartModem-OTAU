import logging

from silvair_uart_common_libs import message_factory
from silvair_uart_common_libs.messages import UartCommand, GenericMessage, InvalidOpcode, InvalidLen
from silvair_uart_common_libs.uart_common_classes import UartAdapterObserver

from .dfu_logic.dfu_mgr import DFU_FSM_Output, DFU_FSM
from .uart_logic.uart_fsm_mgr import UART_FSM_Output, UART_FSM

LOGGER = logging.getLogger(__name__)


class Dispatcher(UartAdapterObserver):
    """
    Dispatcher handler communication coming from UartAdapter, creates message classes and
    forward them to appropriate event handlers.

    This class can be registered in UartAdapter as observer
    """

    def __init__(self, uart_fsm: UART_FSM, dfu_fsm: DFU_FSM):
        """
        Initializes Dispatcher
        """
        self.dfu_fsm = dfu_fsm
        self.uart_fsm = uart_fsm

        LOGGER.info("Dispatcher initialized")

    def new_frame_notification(self, data: bytes):
        """
        Handles new frame coming. This function is called by UartAdapter.

        :param data:    bytes, incoming message
        :return:        None
        """
        try:

            LOGGER.debug("Received data " + bytes_to_readable_hex(data))
            msg = message_factory.deserialize_message(data)
            LOGGER.debug("Dispatching UART message: " + str(msg))
            self.dispatch(msg)
        except InvalidLen as e:
            LOGGER.exception("Error while dispatching UART message " + str(type(e)))
            return  # UART Error response can be added later
        except InvalidOpcode as e:
            LOGGER.exception("Error while dispatching UART message " + str(type(e)))
            return  # UART Error response can be added later

    def dispatch(self, msg: GenericMessage):
        """
        Dispatch parsed message to appropriate event handler.

        :param msg:     GenericMessage or derivative, incoming message to dispatch
        :return:        None
        """
        if msg.type == UartCommand.PingRequest:
            self.uart_fsm.ping_request_message_event(msg)

        elif msg.type == UartCommand.PongResponse:
            self.uart_fsm.pong_response_message_event(msg)

        elif msg.type == UartCommand.InitDeviceEvent:
            self.uart_fsm.init_device_event_message_event(msg)

        elif msg.type == UartCommand.CreateInstancesRequest:
            self.uart_fsm.create_instances_request_message_event(msg)

        elif msg.type == UartCommand.CreateInstancesResponse:
            self.uart_fsm.create_instances_response_message_event(msg)

        elif msg.type == UartCommand.InitNodeEvent:
            self.uart_fsm.init_node_event_message_event(msg)

        elif msg.type == UartCommand.MeshMessageRequest:
            self.uart_fsm.mesh_message_request_message_event(msg)

        elif msg.type == UartCommand.OpcodeError:
            self.uart_fsm.opcode_error_message_event(msg)

        elif msg.type == UartCommand.StartNodeRequest:
            self.uart_fsm.start_node_request_message_event(msg)

        elif msg.type == UartCommand.StartNodeResponse:
            self.uart_fsm.start_node_response_message_event(msg)

        elif msg.type == UartCommand.FactoryResetRequest:
            self.uart_fsm.factory_reset_request_message_event(msg)

        elif msg.type == UartCommand.FactoryResetResponse:
            self.uart_fsm.factory_reset_response_message_event(msg)

        elif msg.type == UartCommand.FactoryResetEvent:
            self.uart_fsm.factory_reset_event_message_event(msg)

        elif msg.type == UartCommand.MeshMessageResponse:
            self.uart_fsm.mesh_message_response_message_event(msg)

        elif msg.type == UartCommand.CurrentStateRequest:
            self.uart_fsm.current_state_request_message_event(msg)

        elif msg.type == UartCommand.CurrentStateResponse:
            self.uart_fsm.current_state_response_message_event(msg)

        elif msg.type == UartCommand.Error:
            self.uart_fsm.error_message_event(msg)

        elif msg.type == UartCommand.FirmwareVersionRequest:
            self.uart_fsm.firmware_version_request_message_event(msg)

        elif msg.type == UartCommand.FirmwareVersionResponse:
            self.uart_fsm.firmware_version_response_message_event(msg)

        elif msg.type == UartCommand.SensorUpdateRequest:
            self.uart_fsm.sensor_update_request_message_event(msg)

        elif msg.type == UartCommand.AttentionEvent:
            self.uart_fsm.attention_event_message_event(msg)

        elif msg.type == UartCommand.SoftResetRequest:
            self.uart_fsm.soft_reset_request_message_event(msg)

        elif msg.type == UartCommand.SoftResetResponse:
            self.uart_fsm.soft_reset_response_message_event(msg)

        elif msg.type == UartCommand.SensorUpdateResponse:
            self.uart_fsm.sensor_update_response_message_event(msg)

        elif msg.type == UartCommand.DeviceUUIDRequest:
            self.uart_fsm.device_uuid_request_message_event(msg)

        elif msg.type == UartCommand.DeviceUUIDResponse:
            self.uart_fsm.device_uuid_response_message_event(msg)

        else:

            if msg.type == UartCommand.DfuInitRequest:
                self.dfu_fsm.dfu_init_request_message_event(msg)

            elif msg.type == UartCommand.DfuInitResponse:
                self.dfu_fsm.dfu_init_response_message_event(msg)

            elif msg.type == UartCommand.DfuStatusRequest:
                self.dfu_fsm.dfu_state_request_message_event(msg)

            elif msg.type == UartCommand.DfuStatusResponse:
                self.dfu_fsm.dfu_state_response_message_event(msg)

            elif msg.type == UartCommand.DfuPageCreateRequest:
                self.dfu_fsm.dfu_page_create_request_message_event(msg)

            elif msg.type == UartCommand.DfuPageCreateResponse:
                self.dfu_fsm.dfu_page_create_response_message_event(msg)

            elif msg.type == UartCommand.DfuWriteDataEvent:
                self.dfu_fsm.dfu_write_data_event_message_event(msg)

            elif msg.type == UartCommand.DfuPageStoreRequest:
                self.dfu_fsm.dfu_page_store_request_message_event(msg)

            elif msg.type == UartCommand.DfuPageStoreResponse:
                self.dfu_fsm.dfu_page_store_response_message_event(msg)

            elif msg.type == UartCommand.DfuStateRequest:
                self.dfu_fsm.dfu_pre_validation_check_request_message_event(msg)

            elif msg.type == UartCommand.DfuStateResponse:
                self.dfu_fsm.dfu_pre_validation_check_response_message_event(msg)

            elif msg.type == UartCommand.DfuCancelRequest:
                self.dfu_fsm.dfu_cancel_request_message_event(msg)

            elif msg.type == UartCommand.DfuCancelResponse:
                self.dfu_fsm.dfu_cancel_response_message_event(msg)


class Sender(UART_FSM_Output, DFU_FSM_Output):
    """
    Dispatcher handler communication coming to UartAdapter, creates message classes and
    forward them to UartAdapter.
    """

    def __init__(self, uart_adapter):
        """
        Initializes Sender.
        """
        self.uart_adapter = uart_adapter

    def send_message(self, msg: GenericMessage):
        """
        Serialize and send message to UartAdapter.

        :param msg:     GenericMessage or derivative, message to be sent
        :return:        None
        """
        try:
            data = message_factory.serialize_message(msg)
            LOGGER.debug("Sending UART message " + bytes_to_readable_hex(data))
            self.uart_adapter.write_uart_frame(data)
        except InvalidLen as e:
            LOGGER.exception("Error sending UART message: InvalidLen. {}".format(e))
        except InvalidOpcode as e:
            LOGGER.exception("Error sending UART message: InvalidOpcode. {}".format(e))


def bytes_to_readable_hex(data: bytes):
    """
    Convert data (bytes) to easily readable str

    :param data: bytes, data to convert
    :return:     str, hex
    """
    output = str()
    for byte in data:
        output += hex(byte) + ' '

    return output
