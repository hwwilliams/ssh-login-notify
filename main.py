#!/usr/bin/env python

import logging, os, select, subprocess, select, time
from twilio.rest import Client

log = logging.getLogger('__main__')
log.setLevel(logging.INFO)

try:
  ssh_auth_file = os.getenv("SSH_AUTH_FILE")
  target_sms_number = os.getenv("TARGET_SMS_NUMBER")
  twilio_msg_sid = os.getenv("TWILIO_MSG_SID")
  twilio_token = os.getenv("TWILIO_TOKEN")
  twilio_client = Client(twilio_msg_sid, twilio_token)
except:
  logging.critical("ERROR: Environment variables not found. (TARGET_SMS_NUMBER, TWILIO_MSG_SID, TWILIO_TOKEN)")

def poll_log_file(ssh_auth_file_path):
  try:
    open_file = subprocess.Popen(["tail", "-F", "-n", "0", ssh_auth_file_path], encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    poller_object = select.poll()
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
    return

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
        logging.error(f"ERROR: Failed to deliver SMS message: {message.error-message}")
        return 1
      time.sleep(1)
    return
  except:
    logging.error(f"ERROR: Failed to fetch SMS message.")

if __name__ == "__main__":
    poll_log_file(ssh_auth_file)
