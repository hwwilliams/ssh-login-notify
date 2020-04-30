#!/usr/bin/env python

import logging
import time

from twilio.base.exceptions import TwilioRestException

from twilio_notifications.client import TwilioClient
from twilio_notifications.lookup import Contacts


logger = logging.getLogger(__name__)


class Messenger:
    def __init__(self, twilio_client, twilio_msg_service_sid):

        self.client = twilio_client
        self.msg_service_sid = twilio_msg_service_sid

    def send_message(self, body_message, contact_name, contact_phone_number):
        logger.debug(
            f'Attempting to queue SMS message to {contact_name} at phone number {contact_phone_number}.')

        try:
            message = self.client.messages.create(
                body=body_message,
                messaging_service_sid=self.msg_service_sid,
                to=contact_phone_number
            )

        except TwilioRestException as e:
            logger.error(
                f'Failed to queue SMS message to {contact_name} at phone number {contact_phone_number}.')
            logger.error(e)

        else:
            logger.debug(
                f'Sucessfully queued SMS message to {contact_name} at phone number {contact_phone_number}.')
            return (message)

    def get_message_delivery_status(self, message_sid, contact_name, contact_phone_number):
        logger.debug(
            f'Attempting to get SMS message delivery status for {contact_name} at phone number {contact_phone_number}.')

        try:
            while True:
                message = self.client.messages(message_sid).fetch()

                if message.status == 'delivered':
                    logger.info('Successfully delivered SMS message.')
                    logger.debug(
                        f'Successfully delivered SMS message to {contact_name} at phone number {contact_phone_number}.')
                    return

                elif message.status in {'failed', 'undelivered'}:
                    logger.debug(
                        f'Failed to deliver SMS message to {contact_name} at phone number {contact_phone_number}.')
                    logger.error(f'Failed to deliver SMS message.')
                    logger.error(message.error-message)
                    return

                time.sleep(1)

        except TwilioRestException as e:
            logger.error(
                f'Failed to get SMS message to with message SID "{message_sid}".')
            logger.error(e)


class TwilioNotification:
    def __init__(self):
        logger.debug(
            'Attemping to initilize Twilio notification client, messenger, and contacts.')

        self.client = TwilioClient().client
        self.msg_service_sid = TwilioClient().msg_service_sid

        self.messenger = Messenger(self.client, self.msg_service_sid)

        self.contacts = Contacts(self.client)
        self.contacts.lookup()
        self.valid_contacts = self.contacts.valid()

        logger.debug(
            'Successfully initilized Twilio notification client, messenger, and contacts.')

    def process_messasge(self, message_to_send):
        for contact in self.valid_contacts:

            contact_name = contact['name']
            contact_phone_number = contact['phone_number']

            message = self.messenger.send_message(
                message_to_send, contact_name, contact_phone_number)

            self.messenger.get_message_delivery_status(
                message.sid, contact_name, contact_phone_number)
