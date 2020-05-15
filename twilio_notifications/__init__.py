import logging

twilio_http_client_logger = logging.getLogger('twilio.http_client')
twilio_http_client_logger.setLevel(logging.WARNING)

urllib3_connectionpool_logger = logging.getLogger('urllib3.connectionpool')
urllib3_connectionpool_logger.setLevel(logging.WARNING)
