#!/usr/bin/env python

import os
import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logger = logging.getLogger(__name__)


class EmptyEnvironmentVariables(Exception):
    # Custom exception raised when environment variables are not found
    def __init__(self):
        Exception.__init__(
            self, 'One or more Twilio environment variables not found. (TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN or TWILIO_MSG_SERVICE_SID)')


def get_client_credentials():
    logger.debug('Attempting to load Twilio environment variables.')

    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_msg_service_sid = os.getenv('TWILIO_MSG_SERVICE_SID')

    empty_env_vars = []

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

    logger.debug('Successfully loaded Twilio environment variables.')
    return (twilio_account_sid, twilio_auth_token, twilio_msg_service_sid)


class TwilioClient:
    def __init__(self):
        logger.debug('Attempting to initilize Twilio client.')

        (
            twilio_account_sid,
            twilio_auth_token,
            twilio_msg_service_sid,
        ) = get_client_credentials()

        self.msg_service_sid = twilio_msg_service_sid

        try:
            self.client = Client(twilio_account_sid, twilio_auth_token)

        except TwilioRestException:
            logger.error('Failed to initilize Twilio client.')
            raise

        else:
            logger.debug('Successfully initilized Twilio client.')
