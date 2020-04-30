#!/usr/bin/env python

import logging

from systemd.journal import JournaldLogHandler
from check_logs.process import Process


def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('__main__')
    journald_handler = JournaldLogHandler()
    journald_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s'
    ))
    logger.addHandler(journald_handler)

    twilio_http_client_logger = logging.getLogger('twilio.http_client')
    twilio_http_client_logger.setLevel(logging.WARNING)

    urllib3_connectionpool_logger = logging.getLogger('urllib3.connectionpool')
    urllib3_connectionpool_logger.setLevel(logging.WARNING)


def process_logs():
    process = Process()
    process.poll()


def main():
    configure_logging()
    process_logs()


if __name__ == "__main__":
    main()
