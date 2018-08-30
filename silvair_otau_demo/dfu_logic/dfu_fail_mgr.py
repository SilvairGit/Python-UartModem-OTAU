import enum
import logging
import time

LOGGER = logging.getLogger(__name__)


class DFUFaultType(enum.IntEnum):
    """
    Enumerator class representing all available types of fault.
    """
    NO_RESPONSE = enum.auto()
    FAULT_WITH_STATUS = enum.auto()


class DFUFault(object):
    """
    Class representing single fault.
    It contains all information related to the fault context.
    """

    def __init__(self, fault_type, call_number, status, callback_func=None, delay_s=0.0):
        """ Construct DFU fault object.

        :param fault_type:      DFUFaultType,      type of fault.
        :param call_number:     int or None,       number of call on which fault should be generated.
                                                   None fault called on every call.
        :param status:          DFUStatus or None, status that should be sent.
                                                   None when no response should be sent.
        :param callback_func:   Callable,          Function that will be called when fault should occur.
                                                   Callback function contains only one argument fault that occured.
                                                   e.g. def fault_handler_func(fault): ...
        :param delay_s:         float,             delay `callback_fault` call by `delay_s` seconds.
                                                   Delay will be executed also in case when `callback_fault` is None.

        """
        if call_number is not None:
            assert call_number > 0, "Call number must be higher than 0."

        self.fault_type = fault_type
        self.status = status
        self.call_number = call_number
        self._callback_func = callback_func
        self._delay_s = delay_s

    def should_send_response(self):
        """ Value that say if response should be send or not.

        :return:    bool, True should send response, False shouldn't send response.
        """
        return self.fault_type == DFUFaultType.FAULT_WITH_STATUS

    def call(self):
        """ Call callback function if callback function is not None. """
        time.sleep(self._delay_s)

        if self._callback_func is None:
            return

        self._callback_func(self)

    @classmethod
    def create_no_response_fault(cls, call_number, callback_func=None, delay_s=0.0):
        """ Create fault that simulate no response.

        :param call_number:     int or None, number of call on which fault should be called.
                                             None fault called on every call.
        :param callback_func:   Callable,    Function that will be called when fault should occur.
                                             Callback function contains only one argument fault that occured.
                                             e.g. def fault_handler_func(fault): ...
        :param delay_s:         float,       delay `callback_fault` call by `delay_s` seconds.
        """
        return cls(DFUFaultType.NO_RESPONSE, call_number, None, callback_func, delay_s)

    @classmethod
    def create_fault_with_status(cls, call_number, status, callback_func=None, delay_s=0.0):
        """ Create fault that simulate response with status.

        :param call_number:     int or None, number of call on which fault should be called.
                                             None fault called on every call.
        :param status:          DFUStatus,   status that should be send in the response.
        :param callback_func:   Callable,    Function that will be called when fault should occur.
                                             Callback function contains only one argument fault that occured.
                                             e.g. def fault_handler_func(fault): ...
        :param delay_s:         float,       delay `callback_fault` call by `delay_s` seconds.
        """
        return cls(DFUFaultType.FAULT_WITH_STATUS, call_number, status, callback_func, delay_s)


class DFUFaultCaller(object):
    """
    Class responsible for faults registering and returning proper fault when it should occur.
    """

    def __init__(self):
        """ Construct DFU fault caller object.
        """
        self._call_number = 1
        self._faults = []

    def _increment_call_number(self):
        """ Increment call number.
        """
        self._call_number += 1

    def add_fault(self, fault):
        """ Add new fault.

        :param fault: DFUFault, any fault
        """
        assert fault is not None, "Could not add fault. Fault cannot be None."
        self._faults.append(fault)

    def call_fault(self):
        """ Call fault.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        call_number = self._call_number
        self._increment_call_number()

        for fault in self._faults:
            if fault.call_number is None:
                fault.call()
                return fault

            if call_number == fault.call_number:
                self._faults.remove(fault)
                fault.call()
                return fault

        return None


class DFUFailMgr(object):
    """
    Class representing DFU fail manager.

    Example usage:

    Generating faults can be done when DFUFailMgr is instantiated during runtime. Example usage:

    fault_manager = DFUFailMgr()
    fault_manager.add_on_pre_validation_fault(DFUFault.create_no_response_fault(None))
    ...

    in place where fault should occur fault should be check and some action can be performed:

    fault = fault_manager.on_pre_validation_fault()
    if fault is None:
        <perform some action when fault occur>
        ...
    """

    def __init__(self):
        """ Construct dfu fail manager object. """
        self._on_pre_validation_fault_caller = DFUFaultCaller()
        self._after_pre_validation_fault_caller = DFUFaultCaller()
        self._on_page_create_fault_caller = DFUFaultCaller()
        self._on_page_store_fault_caller = DFUFaultCaller()
        self._on_post_validation_fault_caller = DFUFaultCaller()

    def on_pre_validation_fault(self):
        """ On pre-validation fault getter.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        return self._on_pre_validation_fault_caller.call_fault()

    def after_pre_validation_fault(self):
        """ After pre-validation fault getter.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        return self._after_pre_validation_fault_caller.call_fault()

    def on_page_create_request_fault(self):
        """ On Page Create Request fault getter.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        return self._on_page_create_fault_caller.call_fault()

    def on_page_store_request_fault(self):
        """ On Page Store Request fault getter.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        return self._on_page_store_fault_caller.call_fault()

    def on_post_validation_fault(self):
        """ On post-validation fault getter.

        :return: DFUFault or None, fault when any fault registered and call number matching.
                                   None when no fault registered or no call number matching.
        """
        return self._on_post_validation_fault_caller.call_fault()

    def add_on_pre_validation_fault(self, fault):
        """ Add on pre-validation fault.

        :param fault: DFUFault, any fault
        """
        self._on_pre_validation_fault_caller.add_fault(fault)

    def add_after_pre_validation_fault(self, fault):
        """ Add after pre-validation fault.

        :param fault: DFUFault, any fault
        """
        self._after_pre_validation_fault_caller.add_fault(fault)

    def add_on_page_create_request_fault(self, fault):
        """ Add on Page Create Request fault.

        :param fault: DFUFault, any fault
        """
        self._on_page_create_fault_caller.add_fault(fault)

    def add_on_page_store_request_fault(self, fault):
        """ Add on Page Store Request fault.

        :param fault: DFUFault, any fault
        """
        self._on_page_store_fault_caller.add_fault(fault)

    def add_on_post_validation_fault(self, fault):
        """ Add on post-validation fault.

        :param fault: DFUFault, any fault
        """
        self._on_post_validation_fault_caller.add_fault(fault)
