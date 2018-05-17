import logging

from .dfu_memory import DFUMemory

LOGGER = logging.getLogger(__name__)

class DFU_FailMgr:

    def __init__(self,
                 expected_app_data: bytes,
                 pre_validation_fail: bool,
                 post_validation_fail: bool):
        """
        Fail manager. Validates DFU operation.

        :param expected_app_data:       bytes, Expected application data
        :param pre_validation_fail:     bool, if True will deliberately cause pre validation fail
        :param post_validation_fail:    bool, if True will deliberately cause post validation fail
        """
        self.expected_app_data = expected_app_data
        self.pre_validation_fail = pre_validation_fail
        self.post_validation_fail = post_validation_fail

    def pre_validation(self, memory : DFUMemory, init_msg):
        """
        Perform pre validation

        :param memory:      DFU Memory
        :param init_msg:    DFU Init message
        :return:            True/False
        """
        if (self.expected_app_data is not None and init_msg.app_data != self.expected_app_data) \
                or self.pre_validation_fail:

            LOGGER.debug("Pre-validation failed: " + str(init_msg))
            return False

    def post_validation(self, memory : DFUMemory):
        """
        Perform post validation

        :param memory:      DFU Memory
        :return:            True/False
        """
        return self.post_validation_fail