import json
import logging

LOGGER = logging.getLogger(__name__)

class DFU_NVM:
    """
    DFU Non Volatile Memory, allow to store serializable dict as JSON in a file
    """
    def __init__(self, path = 'nvm'):
        """
        Init DFU_NVM

        :param path: Path to file used to store state
        """
        self.path = path
        try:
            with open(path, 'r') as file:
                self.data_dict = json.load(file)
            LOGGER.debug("Successfully loaded data from file")
        except:
            self.data_dict = dict()
            LOGGER.debug("Unable to read data from file")

        LOGGER.info("DFU_NVM initialized")

    def get(self, key):
        """
        Get value indexed by key
        :param key: Key
        :return:    Value
        """
        try:
            return self.data_dict[key]
        except KeyError:
            self.update(key, None)
            return self.data_dict[key]

    def update(self, key, value):
        """
        Update value related to key

        :param key:     Key
        :param value:   value
        :return:        None
        """
        self.data_dict.update( {key : value} )

        try:
            with open(self.path, 'w') as file:
                json.dump(self.data_dict, file)
            LOGGER.debug("Successfully updated nvm file")
        except:
            LOGGER.error("Unable to update nvm file")