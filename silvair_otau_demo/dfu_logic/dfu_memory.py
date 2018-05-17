import binascii
import hashlib
import logging

LOGGER = logging.getLogger(__name__)

MIN_SUPPORTED_PAGE_SIZE = 21


class DFUMemoryError(Exception):
    pass


class DFUMemory:
    """
    Mock memory for DFU update testing
    """

    def __init__(self,
                 app_data_file: str,
                 firmware_file: str,
                 sha256_file: str,
                 supported_page_size: int = 256,
                 max_mem_size: int = 0):
        """
        Initialize DFUMemory

        :param app_data_file:       Path to file with app data
        :param firmware_file:       Path to file with firmware data
        :param sha256_file:         Path to file with SHA256
        :param supported_page_size: Max supported page size
        :param max_mem_size:        Max supported firmware image size
        """
        self.app_data_file_path = app_data_file
        self.firmware_file_path = firmware_file
        self.sha256_file_path = sha256_file
        self.supported_page_size = supported_page_size
        self.max_mem_size = max_mem_size

        self.firmware_page_size = 0
        self.firmware_page = bytes()
        self.firmware_page_offset = 0

        try:
            with open(app_data_file, 'rb') as app_data_file:
                self.app_data_memory = app_data_file.read()
        except FileNotFoundError:
            LOGGER.debug("Unable to open app data file")
            self.app_data_memory = bytes()

        try:
            with open(firmware_file, 'rb') as firmware_file:
                self.firmware_memory = firmware_file.read()
                self.firmware_offset = firmware_file.tell()
        except FileNotFoundError:
            LOGGER.debug("Unable to open firmware file")
            self.firmware_memory = bytes()
            self.firmware_offset = 0

        LOGGER.debug("Initialized DFUMemory")

    def set_firmware_memory_size(self, size: int):
        """
        Set firmware memory size, initialize firmware memory

        :param size:    int, firmware memory size
        :return:        False if size is bigger than max mem size, True otherwise
        """
        if size > self.max_mem_size and self.max_mem_size != 0:
            raise DFUMemoryError

        self.firmware_memory = bytearray()
        LOGGER.debug("Got firmware memory size to {:d}".format(size))

    def set_app_data_memory_size(self, size: int):
        """
        Set app data memory size, initialize app data memory

        :param size:    int, app data memory size
        :return:        None
        """
        self.app_data_memory = bytearray()
        self.app_data_memory_size = size
        LOGGER.debug("Got app data memory size to {:d}".format(size))

    def write_app_data(self, data: bytes):
        """
        Writes app data to memory prepared earlier

        :param data:    bytes, data to write
        :return:        None
        """
        if len(data) == self.app_data_memory_size:
            self.app_data_memory = data
            with open(self.app_data_file_path, 'wb') as app_data_file:
                app_data_file.write(self.app_data_memory)
        else:
            LOGGER.debug("Attempted to write too big or too small app data, expected: " + str(
                self.app_data_memory_size) + " got: " + str(len(data)))
            raise DFUMemoryError

        LOGGER.debug("Written app data memory")

    def create_page(self, size: int):
        """
        Create page in memory

        :param size:    int, page size
        :return:        None
        """
        self.firmware_page = bytearray()
        self.firmware_page_offset = 0
        self.firmware_page_size = size

        LOGGER.debug("Created page. Size: {:d}, offset {:d}".format(self.firmware_page_size, self.firmware_offset))

    def write_data(self, data: bytes):
        """
        Write part of page data to memory prepared earlier

        :param data:    bytes, data to write
        :return:        None
        """
        self.firmware_page += data
        self.firmware_page_offset += len(data)

        LOGGER.debug("Written data at offset {:04x}".format(self.firmware_page_offset))

    def page_store(self):
        """
        Store page into firmware memory.
        """
        if len(self.firmware_page) != self.firmware_page_size:
            LOGGER.debug('page store error')
            raise DFUMemoryError

        self.firmware_memory += self.firmware_page
        self.firmware_offset += self.firmware_page_offset

        with open(self.firmware_file_path, 'ab') as firmware_file:
            firmware_file.write(self.firmware_page)

        self.firmware_page = bytes()
        self.firmware_page_offset = 0

        LOGGER.debug("Stored page at offset {:04x}".format(self.firmware_offset))

    def calc_firmware_crc(self):
        """
        Calculate CRC of data already stored in firmware memory

        :return:    int, calculated CRC
        """
        return (binascii.crc32(self.firmware_memory + self.firmware_page) & 0xFFFFFFFF)

    def calc_firmware_sha256(self):
        """
        Calculate SHA256 of data stored in firmware memory

        :return:    bytes, calculated SHA256
        """
        sha = hashlib.sha256(self.firmware_memory).digest()
        sha = bytearray(sha)
        sha.reverse()

        with open(self.sha256_file_path, 'w') as sha256_file:
            sha256_file.write(sha.hex())

        return sha

    def clear(self):
        """
        Clear memory
        """
        self.firmware_memory_size = 0
        self.app_data_memory_size = 0

        self.firmware_memory = None
        self.app_data_memory = None
        self.firmware_offset = 0
        self.firmware_crc = 0

        self.firmware_page = bytes()
        self.firmware_page_offset = 0

        self.app_data_file = open(self.app_data_file_path, 'wb')
        self.firmware_file = open(self.firmware_file_path, 'wb')
        self.sha256_file = open(self.sha256_file_path, 'w')

        self.sha256_file.close()
        self.firmware_file.close()
        self.app_data_file.close()

        LOGGER.debug("Cleared memory")
