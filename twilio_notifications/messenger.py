import json
import os
import logging
import time

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logger = logging.getLogger(__name__)


class EmptyEnvironmentVariables(Exception):
    # Custom exception raised when environment variables are not found
    def __init__(self):
        Exception.__init__(
            self, 'One or more Twilio environment variables not found. (TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN or TWILIO_MSG_SERVICE_SID)')


class InvalidContacts(Exception):
    # Custom exception raised when all available contacts have invalid phone numbers
    def __init__(self):
        Exception.__init__(
            self, 'All available contacts have invalid phone numbers.')


def load_twilio_env_vars():
    logger.debug('Attempting to load Twilio environment variables.')

    empty_env_vars = []

    try:
        twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_msg_service_sid = os.getenv('TWILIO_MSG_SERVICE_SID')

        if not twilio_account_sid:
            empty_env_vars.append('TWILIO_ACCOUNT_SID')

        if not twilio_auth_token:
            empty_env_vars.append('TWILIO_AUTH_TOKEN')

        if not twilio_msg_service_sid:
            empty_env_vars.append('TWILIO_MSG_SERVICE_SID')

        if empty_env_vars:
            for env_var in empty_env_vars:
                logger.error(
                    f'Twilio environment variable {env_var} not found.')
            raise EmptyEnvironmentVariables

    except EmptyEnvironmentVariables:
        raise

    else:
        logger.debug('Successfully loaded Twilio environment variables.')
        return (twilio_account_sid, twilio_auth_token, twilio_msg_service_sid)


def load_contacts_file():
    contacts_json_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'settings', 'contacts.json'))

    logger.debug(
        f'Attempting to load contact information from: "{contacts_json_path}".')

    try:
        with open(contacts_json_path, 'r') as file:
            contacts_dict = json.load(file)

    except json.JSONDecodeError:
        logger.error(
            f'No valid JSON data found when attempting to load contact information from: "{contacts_json_path}".')
        raise

    except FileNotFoundError:
        logger.error(
            f'contacts file not found: "{contacts_json_path}"')
        raise

    else:
        logger.debug(
            f'Successfully loaded contact information from: "{contacts_json_path}".')
        return (contacts_dict, contacts_json_path)


class Client:
    def __init__(self):
        logger.debug('Attempting to initilize Twilio client.')

        (
            twilio_account_sid,
            twilio_auth_token,
            twilio_msg_service_sid,
        ) = load_twilio_env_vars()

        self.twilio_msg_service_sid = twilio_msg_service_sid

        try:
            self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

        except TwilioRestException:
            logger.error('Failed to initilize Twilio client.')
            raise

        else:
            logger.info('Successfully initilized Twilio client.')

    def validate_contacts(self):
        logger.debug('Attempting to validate contacts.')

        valid_contacts = []
        invalid_contacts = []

        (
            contacts_dict,
            contacts_json_path
        ) = load_contacts_file()

        for contact in contacts_dict:
            contact_name = contact['name']
            contact_phone_number = contact['phone_number']

            try:
                self.twilio_client.lookups.phone_numbers(
                    contact_phone_number).fetch()

            except TwilioRestException:
                logger.warning(
                    f'Invalid Contact Phone Number: Contact Name is "{contact_name}" with phone number "{contact_phone_number}".')

                invalid_contact = {
                    'name': f'{contact_name}',
                    'phone_number': f'{contact_phone_number}'
                }
                invalid_contacts.append(dict(invalid_contact))

            else:
                valid_contact = {
                    'name': f'{contact_name}',
                    'phone_number': f'{contact_phone_number}'
                }
                valid_contacts.append(dict(valid_contact))

                logger.debug(
                    f'Valid Contact Phone Number: Contact Name is "{contact_name}" with phone number "{contact_phone_number}".')

        if valid_contacts:
            if len(contacts_dict) == len(valid_contacts):
                logger.debug(
                    f'Validated all configured contact phone numbers.')

            elif len(valid_contacts) == 1:
                logger.debug(
                    f'{len(valid_contacts)} contact with a valid phone number.')

            elif len(valid_contacts) > 1:
                logger.debug(
                    f'{len(valid_contacts)} contacts with a valid phone number.')

            if len(invalid_contacts) == 1:
                logger.warning(
                    f'{len(invalid_contacts)} contact with an invalid phone number.')

            elif len(invalid_contacts) > 1:
                logger.warning(
                    f'{len(invalid_contacts)} contacts with an invalid phone number.')

            return (valid_contacts)

        else:
            logger.error(
                f'All configured contact phone numbers are invalid from: "{contacts_json_path}".')
            raise InvalidContacts

    def send_message(self, body_message, contact_name, contact_phone_number):
        logger.debug('Attempting to create SMS message.')

        try:
            message = self.twilio_client.messages.create(
                body=body_message,
                messaging_service_sid=self.twilio_msg_service_sid,
                to=contact_phone_number
            )

        except TwilioRestException:
            logger.error(f'Failed to create SMS message.')

        else:
            logger.debug('Sucessfully created SMS message.')
            logger.debug(
                f'Attemping to send SMS message to {contact_name} at phone number {contact_phone_number}.')
            return (message)

    def get_message_delivery_status(self, message_sid, contact_name, contact_phone_number):
        logger.debug('Attempting to get SMS message delivery status.')

        try:
            while True:
                message = self.twilio_client.messages(message_sid).fetch()

                if message.status == 'delivered':
                    logger.info('Successfully delivered SMS message.')
                    logger.debug(
                        f'Successfully delivered SMS message to {contact_name} at phone number {contact_phone_number}.')
                    return

                elif message.status in {'failed', 'undelivered'}:
                    logger.error(
                        f'Failed to deliver SMS message: {message.error-message}')
                    logger.debug(
                        f'Failed to deliver SMS message to {contact_name} at phone number {contact_phone_number}: {message.error-message} .')
                    return

                time.sleep(1)

        except TwilioRestException:
            logger.error('Failed to get SMS message delivery status.')
            logger.debug(
                f'Failed to get SMS message to with message SID "{message_sid}".')


class Messenger:
    def __init__(self):
        logger.debug('Attemping to initilize Twilio messgener.')

        self.client = Client()
        self.contacts = self.client.validate_contacts()

        logger.debug('Successfully initilized Twilio messgener.')

    def process_messasge(self, message_to_send):
        for contact in self.contacts:

            contact_name = contact['name']
            contact_phone_number = contact['phone_number']

            message = self.client.send_message(
                message_to_send, contact_name, contact_phone_number)

            message_status = self.client.get_message_delivery_status(
                message.sid, contact_name, contact_phone_number)
