import logging

from termcolor import cprint
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)

class ConsoleOut:
    """
    Class handling CLI
    """
    progress_bar_enabled = False
    pbar = None

    @classmethod
    def print_standard_message(cls, msg: str):
        """
        Print standard message

        :param msg: str, message to write
        :return:    None
        """
        if not cls.progress_bar_enabled:
            cprint(msg, 'white')

    @classmethod
    def print_error_message(cls, msg: str):
        """
        Print error message

        :param msg: str, message to write
        :return:    None
        """
        cprint(msg, 'red')

    @classmethod
    def print_important_message(cls, msg: str):
        """
        Print important message

        :param msg: str, message to write
        :return:    None
        """
        if not cls.progress_bar_enabled:
            cprint(msg, 'yellow')

    @classmethod
    def print_informative_message(cls, msg: str):
        """
        Print informative message

        :param msg: str, message to write
        :return:    None
        """
        if not cls.progress_bar_enabled:
            cprint(msg, 'green')

    @classmethod
    def start_progress_bar(cls, total: int = 100, initial: int = 0):
        """
        Start displaying progress bar.
        After calling this method and before calling stop_progress_bar,
        printing can cause undefined behaviour

        :param msg: int, progress implying 100% full progress bar
        :param msg: int, initial progress
        :return:    None
        """
        if not cls.progress_bar_enabled:
            LOGGER.debug('Starting progress bar')
            cls.pbar = tqdm(total=total, initial=initial, unit='bytes')
            cls.progress_bar_enabled = True
        else:
            LOGGER.debug('Progress bar already started')

    @classmethod
    def update_progress_bar(cls, progress: int):
        """
        Update progress bar.

        :param progress:    int, new progress
        :return:            None
        """
        if cls.progress_bar_enabled:
            LOGGER.debug('Updating progress bar')
            cls.pbar.update(progress - cls.pbar.last_print_n)
        else:
            LOGGER.debug('Cannot update not started progress bar')

    @classmethod
    def stop_progress_bar(cls):
        """
        Stop progress bar.
        """
        if cls.progress_bar_enabled:
            LOGGER.debug('Closing progress bar')
            cls.pbar.close()
        else:
            LOGGER.debug('Cannot stop not started progress bar')
        cls.progress_bar_enabled = False
