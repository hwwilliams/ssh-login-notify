#!/usr/bin/env python

import json
import os
import time
import subprocess
import select
import logging

from twilio_notifications.messenger import TwilioNotification

logger = logging.getLogger(__name__)


class InvalidJsonLogFile(Exception):
    # Custom exception raised when the log_file json key was not found
    def __init__(self):
        Exception.__init__(
            self, 'Failed to find valid log_file json key.')


def get_log_file():
    log_file_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'settings', 'log_file.json'))

    logger.debug(
        f'Attempting to load ssh log file from: "{log_file_path}".')

    try:
        with open(log_file_path, 'r') as file:
            log_dict = json.load(file)

    except json.JSONDecodeError:
        logger.error(
            f'No valid JSON data found when attempting to load ssh log file from: "{log_file_path}".')
        raise

    except FileNotFoundError:
        logger.error(
            f'contacts file not found: "{log_file_path}"')
        raise

    if 'log_path' in log_dict[0]:
        logger.debug(
            f'Successfully loaded contact information from: "{log_file_path}".')
        return (log_dict[0]['log_path'])

    else:
        logger.error(
            f'Log_path key not found from: "{log_file_path}".')
        raise InvalidJsonLogFile


def twilio_notification(message_to_send):
    client = TwilioNotification()
    client.process_messasge(message_to_send)


class Process:
    def __init__(self):

        self.log_file = get_log_file()

    def poll(self):

        open_file = subprocess.Popen(["tail", "-F", "-n", "0", self.log_file],
                                     encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        poller_object = select.poll()
        poller_object.register(open_file.stdout)

        while True:
            if poller_object.poll(1):
                log_line = open_file.stdout.readline()
                if all(entry in log_line for entry in ('sshd:session' and 'session opened')):
                    twilio_notification(log_line)
            time.sleep(1)
