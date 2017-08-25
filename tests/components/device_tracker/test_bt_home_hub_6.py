"""The tests for the BT Home Hub 5 device tracker platform."""
import unittest
from typing import Dict
from unittest.mock import patch

from bthomehub.exception import AuthenticationException, ResponseException
from requests import RequestException

from homeassistant.components.device_tracker.bt_home_hub_6 import BTHomeHubDeviceScanner

MOCK_DEVICE_LIST = {"74-C2-87-BE-46-A7": "user_1", "12-B1-78-AA-45-D0": "user_2"}


class TestBTHomeHubDeviceScanner(unittest.TestCase):
    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__init(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config=dict(CONF_SCAN_INTERVAL=1))
        client_mock.return_value.authenticate.assert_called_once()
        self.assertTrue(under_test.success_init)

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__init_exception_not_initalised(self, client_mock):
        client_mock.return_value.authenticate.side_effect = AuthenticationException()
        under_test = BTHomeHubDeviceScanner(config=dict(CONF_SCAN_INTERVAL=1))

        client_mock.return_value.authenticate.assert_called_once()
        self.assertFalse(under_test.success_init)

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__update_info_updates_correctly(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        instance = client_mock.return_value
        instance.get_devices.return_value = MOCK_DEVICE_LIST

        result = under_test._update_info()
        self.assertTrue(result)
        self.assertEqual(under_test.last_results, MOCK_DEVICE_LIST)
        instance.get_devices.assert_called_once()

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__update_info_returns_False_when_not_successfully_initialised(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = False

        instance = client_mock.return_value
        instance.get_devices.return_value = MOCK_DEVICE_LIST

        result = under_test._update_info()
        self.assertFalse(result)
        instance.get_devices.assert_not_called()

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__update_info_returns_False_when_authentication_exception(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        instance = client_mock.return_value
        instance.get_devices.side_effect = AuthenticationException()

        result = under_test._update_info()
        self.assertFalse(result)
        instance.get_devices.assert_called_once()
        self.assertEqual(instance.authenticate.call_count, 2)

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__update_info_returns_False_when_response_exception(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        instance = client_mock.return_value
        instance.get_devices.side_effect = ResponseException()

        result = under_test._update_info()
        self.assertFalse(result)
        instance.get_devices.assert_called_once()
        instance.authenticate.assert_called_once()

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__update_info_returns_False_when_request_exception(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        instance = client_mock.return_value
        instance.get_devices.side_effect = RequestException()

        result = under_test._update_info()
        self.assertFalse(result)
        instance.get_devices.assert_called_once()
        instance.authenticate.assert_called_once()

    def test__get_device_name_return_correct_value(self):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        under_test.last_results = MOCK_DEVICE_LIST

        result = under_test.get_device_name("74-C2-87-BE-46-A7")
        self.assertEqual(result, "user_1")
        result = under_test.get_device_name("12-B1-78-AA-45-D0")
        self.assertEqual(result, "user_2")
        result = under_test.get_device_name("nothing")
        self.assertIsNone(result)

    def test__get_device_name_return_None_if_not_initialised(self):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = False

        under_test.last_results = MOCK_DEVICE_LIST

        result = under_test.get_device_name("74-C2-87-BE-46-A7")
        self.assertIsNone(result)
        result = under_test.get_device_name("12-B1-78-AA-45-D0")
        self.assertIsNone(result)

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__get_device_name_updates_if_not_present(self, client_mock):
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True
        under_test.last_results = None

        instance = client_mock.return_value
        instance.get_devices.return_value = MOCK_DEVICE_LIST

        result = under_test.get_device_name("74-C2-87-BE-46-A7")
        self.assertEqual(result, "user_1")
        instance.get_devices.assert_called_once()

    @patch('homeassistant.components.device_tracker.bt_home_hub_6.BtHomeClient')
    def test__scan_devices_works_as_expected(self, client_mock):
        """Scan for new devices and return a list with found device IDs."""
        under_test = BTHomeHubDeviceScanner(config={})
        under_test.success_init = True

        instance = client_mock.return_value
        instance.get_devices.return_value = MOCK_DEVICE_LIST

        result = under_test.scan_devices()
        self.assertEqual(result, ['74-C2-87-BE-46-A7', '12-B1-78-AA-45-D0'])
