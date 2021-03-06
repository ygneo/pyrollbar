"""
Tests for the RollbarHandler logging handler
"""
import copy
import logging
import mock
import urllib
import sys

import rollbar
from rollbar.logger import RollbarHandler

from . import BaseTest


_test_access_token = 'aaaabbbbccccddddeeeeffff00001111'
_test_environment = 'test'
_default_settings = copy.deepcopy(rollbar.SETTINGS)


class LogHandlerTest(BaseTest):
    def setUp(self):
        rollbar._initialized = False
        rollbar.SETTINGS = copy.deepcopy(_default_settings)

    def _create_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        rollbar_handler = RollbarHandler(_test_access_token, _test_environment)
        rollbar_handler.setLevel(logging.WARNING)

        logger.addHandler(rollbar_handler)

        return logger

    @mock.patch('rollbar.send_payload')
    def test_message_stays_unformatted(self, send_payload):
        logger = self._create_logger()
        logger.warning("Hello %d %s", 1, 'world')

        payload = send_payload.call_args[0][0]

        self.assertEqual(payload['data']['body']['message']['body'], "Hello %d %s")
        self.assertEqual(payload['data']['body']['message']['args'], (1, 'world'))

        self.assertEqual(payload['data']['body']['message']['record']['name'], __name__)


    def test_request_is_get_from_log_record_if_present(self):
        logger = self._create_logger()
        # Request objects vary depending on python frameworks or packages.
        # Using a dictionary for this test is enough.
        request = {"fake": "request", "for":  "testing purporse"}

        # No need to test request parsing and payload sent,
        # just need to be sure that proper rollbar function is called
        # with passed request as argument.
        with mock.patch("rollbar.report_message") as report_message_mock:
            logger.warning("Warning message", extra={"request": request})
            self.assertEquals(report_message_mock.call_args[1]["request"], request)

        # Python 2.6 doesnt support extra param in logger.exception.
        if not sys.version_info[:2] == (2, 6):
            with mock.patch("rollbar.report_exc_info") as report_exc_info:
                logger.exception("Exception message", extra={"request": request})
                self.assertEquals(report_exc_info.call_args[1]["request"], request)
