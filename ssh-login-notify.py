#!/usr/bin/env python

import logging

# from systemd.journal import JournaldLogHandler
from twilio_notifications.messenger import TwilioNotification


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s : %(name)s : %(message)s')
    logger = logging.getLogger('__main__')
    # journald_handler = JournaldLogHandler()
    # journald_handler.setFormatter(logging.Formatter(
    #     '[%(levelname)s] %(message)s'
    # ))
    # logger.addHandler(journald_handler)

    twilio_http_client_logger = logging.getLogger('twilio.http_client')
    twilio_http_client_logger.setLevel(logging.WARNING)

    urllib3_connectionpool_logger = logging.getLogger('urllib3.connectionpool')
    urllib3_connectionpool_logger.setLevel(logging.WARNING)


def twilio_notifications(message_to_send):
    client = TwilioNotification()
    client.process_messasge(message_to_send)


def main():
    configure_logging()
    twilio_notifications('Test Message')


if __name__ == "__main__":
    main()
