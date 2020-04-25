#!/usr/bin/env python

import logging
import os
import select
import subprocess
import time
from twilio.rest import Client

log = logging.getLogger('__main__')
log.setLevel(logging.INFO)

try:
    ssh_auth_file = os.getenv("SSH_AUTH_FILE")
    target_sms_number = os.getenv("TARGET_SMS_NUMBER")
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_msg_sid = os.getenv("TWILIO_MSG_SID")
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
except:
    logging.error(
        "ERROR: Environment variables not found. (SSH_AUTH_FILE, TARGET_SMS_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_MSG_SID)")


def poll_log_file(ssh_auth_file_path):
    try:
        open_file = subprocess.Popen(["tail", "-F", "-n", "0", ssh_auth_file_path],
                                     encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        poller_object = select.poll()
        print()
        poller_object.register(open_file.stdout)
        while True:
            if poller_object.poll(1):
                process_log_entry(open_file.stdout.readline())
            time.sleep(1)
    except:
        logging.error(f"ERROR: Failed to open SSH log file.")


def process_log_entry(log_line):
    if "sudo" and "COMMAND" in log_line:
        send_sms_msg(log_line)
    elif "ssh" and "session opened" in log_line:
        send_sms_msg(log_line)


def send_sms_msg(log_line_msg):
    try:
        message = twilio_client.messages.create(
            body=log_line_msg,
            messaging_service_sid=twilio_msg_sid,
            to=target_sms_number
        )
        return get_sms_msg_status(message.sid)
    except:
        logging.error(f"ERROR: Failed to send SMS message.")


def get_sms_msg_status(msg_sid):
    try:
        while True:
            message = twilio_client.messages(msg_sid).fetch()
            if message.status == 'delivered':
                logging.info("Successfully delivered SMS message.")
                return 0
            elif message.status in {'failed', 'undelivered'}:
                logging.error(
                    f"ERROR: Failed to deliver SMS message: {message.error-message}")
                return 1
            time.sleep(1)
    except:
        logging.error(f"ERROR: Failed to fetch SMS message.")


if __name__ == "__main__":
    poll_log_file(ssh_auth_file)
