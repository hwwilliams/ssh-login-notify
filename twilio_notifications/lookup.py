#!/usr/bin/env python

import json
import os
import logging

from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class InvalidContacts(Exception):
    # Custom exception raised when all available contacts have invalid phone numbers
    def __init__(self):
        Exception.__init__(
            self, 'All available contacts have invalid phone numbers.')


class InvalidJsonContactsArray(Exception):
    # Custom exception raised when the contacts json array was not found
    def __init__(self):
        Exception.__init__(
            self, 'Failed to find valid contacts json array.')


def get_contacts_data():
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

    if 'contacts' in contacts_dict:
        logger.debug(
            f'Successfully loaded contact information from: "{contacts_json_path}".')
        return (contacts_dict['contacts'], contacts_json_path)

    else:
        logger.error(
            f'Contacts json array not found from: "{contacts_json_path}".')
        raise InvalidJsonContactsArray


class Contacts:
    def __init__(self, twilio_client):
        logger.debug('Attempting to validate contacts.')

        self.client = twilio_client

        (
            self.contacts_dict,
            self.contacts_json_path
        ) = get_contacts_data()

    def lookup(self):
        self.valid_contacts = []
        self.invalid_contacts = []

        for contact in self.contacts_dict:

            contact_name = contact['name']
            contact_phone_number = contact['phone_number']

            logger.debug(
                f'Attempting to validate contact phone number: Contact Name is "{contact_name}" with phone number "{contact_phone_number}".')

            try:
                self.client.lookups.phone_numbers(
                    contact_phone_number).fetch()

            except TwilioRestException as e:
                if e.status == 404:
                    invalid_contact = {
                        'name': f'{contact_name}',
                        'phone_number': f'{contact_phone_number}'
                    }
                    self.invalid_contacts.append(dict(invalid_contact))

                    logger.warning(
                        f'Found invalid Contact Phone Number: Contact Name is "{contact_name}" with phone number "{contact_phone_number}".')
                else:
                    raise e

            else:
                valid_contact = {
                    'name': f'{contact_name}',
                    'phone_number': f'{contact_phone_number}'
                }
                self.valid_contacts.append(dict(valid_contact))

                logger.debug(
                    f'Found valid Contact Phone Number: Contact Name is "{contact_name}" with phone number "{contact_phone_number}".')

    def valid(self):
        if self.valid_contacts:
            if len(self.contacts_dict) == len(self.valid_contacts):
                logger.debug(
                    'Successfully Validated all configured contact phone numbers.')

            elif len(self.valid_contacts) == 1:
                logger.debug(
                    '1 contact with a valid phone number.')

            elif len(self.valid_contacts) > 1:
                logger.debug(
                    f'{len(self.valid_contacts)} contacts with a valid phone number.')

            if len(self.invalid_contacts) == 1:
                logger.warning(
                    '1 contact with an invalid phone number.')

            elif len(self.invalid_contacts) > 1:
                logger.warning(
                    f'{len(self.invalid_contacts)} contacts with an invalid phone number.')

            return (self.valid_contacts)

        else:
            logger.error(
                f'All configured contact phone numbers are invalid from: "{self.contacts_json_path}".')
            raise InvalidContacts
