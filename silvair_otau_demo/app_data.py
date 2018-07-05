"""
Class for mcu dfu app data
"""


class AppData(object):
    """
    Represents app data used in MCU OTAU.
    """
    def __init__(self, app_data_path, logger=None):
        """
        :param app_data_path: str, path to app data file
        :param logger: logger object
        """
        self.app_data_path = app_data_path
        self.logger = logger

    def load_app_data(self):
        """
        Loads app data into bytes type.

        :return: bytes, expected app data or None if unable to load data
        """
        if self.logger:
            self.logger.info("Loading expected app data from file")

        try:
            with open(self.app_data_path, 'rb') as expected_app_data_file:
                expected_app_data_bytes = expected_app_data_file.read()
            if self.logger:
                self.logger.debug("Loaded app data: {}".format(self.app_data_path.hex()))

        except (FileNotFoundError, ValueError):
            if self.logger:
                self.logger.error("Failed to open / read expected app data file, ignoring app data.")
            expected_app_data_bytes = None

        return expected_app_data_bytes
