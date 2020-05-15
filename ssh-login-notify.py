#!/usr/bin/env python

import logging

from systemd import journal
from check_logs.process import Process


def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('__main__')
    journald_handler = journal.JournalHandler()
    journald_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s'
    ))
    logger.addHandler(journald_handler)


def process_logs():
    process = Process()
    process.poll()


def main():
    configure_logging()
    process_logs()


if __name__ == "__main__":
    main()
