import random
import unittest

from silvair_otau_demo.dfu_logic.dfu_fail_mgr import DFUFault, DFUFaultType, DFUFaultCaller
from silvair_uart_common_libs.message_types import DFUStatus


def any_dfu_status():
  return DFUStatus[random.choice([dfu_fault.name for dfu_fault in DFUStatus])]


def any_call_number():
  return random.randrange(1, 100)


class TestDFUFaultCaller(unittest.TestCase):

  def test_call_number_should_be_set_to_one_when_DFUFaultCaller_object_has_been_created(self):
    # When
    fault_caller = DFUFaultCaller()

    # Then
    self.assertEqual(1, fault_caller._call_number)

  def test_should_increment_call_number_when_call_fault_method_is_called(self):
    # Given
    fault_caller = DFUFaultCaller()
    current_call_number = fault_caller._call_number

    # When
    fault_caller.call_fault()

    # Then
    self.assertEqual(current_call_number + 1, fault_caller._call_number)

  def test_should_return_None_when_no_fault_has_been_registered_and_call_fault_method_is_called(self):
    # Given
    fault_caller = DFUFaultCaller()

    # When
    ret_fault = fault_caller.call_fault()

    # Then
    self.assertEqual(None, ret_fault)

  def test_should_always_return_no_response_DFUFault_when_fault_has_been_added_and_call_fault_method_is_called(self):
    # Given
    fault = DFUFault.create_no_response_fault(None)

    fault_caller = DFUFaultCaller()
    fault_caller.add_fault(fault)

    for _ in range(random.randrange(10, 1000)):
      # When
      ret_fault = fault_caller.call_fault()

      # Then
      self.assertEqual(fault, ret_fault)

  def test_should_always_return_DFUFault_with_status_when_fault_has_been_added_and_call_fault_method_is_called(self):
    # Given
    fault = DFUFault.create_fault_with_status(None, any_dfu_status())

    fault_caller = DFUFaultCaller()
    fault_caller.add_fault(fault)

    for _ in range(random.randrange(10, 1000)):
      # When
      ret_fault = fault_caller.call_fault()

      # Then
      self.assertEqual(fault, ret_fault)

  def test_should_return_fault_only_when_call_number_is_equal_to_fault_call_number_and_call_fault_method_is_called(self):
    # Given
    call_number = any_call_number()
    fault = DFUFault(DFUFaultType.FAULT_WITH_STATUS, call_number, any_dfu_status(), None)

    fault_caller = DFUFaultCaller()
    fault_caller.add_fault(fault)

    # Then
    for _ in range(call_number - 1):
      self.assertEqual(None, fault_caller.call_fault())

    self.assertEqual(fault, fault_caller.call_fault())

    for _ in range(random.randrange(1, 100)):
      self.assertEqual(None, fault_caller.call_fault())
