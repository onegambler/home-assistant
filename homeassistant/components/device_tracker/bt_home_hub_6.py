"""
Support for BT Home Hub
"""
import logging
import voluptuous as vol
from bthomehub.client import BtHomeClient
from bthomehub.exception import (ResponseException, AuthenticationException)
from requests import RequestException

import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string
})


# pylint: disable=unused-argument
def get_scanner(hass, config):
    scanner = BTHomeHubDeviceScanner(config[DOMAIN])

    return scanner if scanner.success_init else None


class BTHomeHubDeviceScanner(DeviceScanner):
    def __init__(self, config):
        _LOGGER.info("Initialising BT Home Hub 6 Scanner")
        timeout = max(int(config.get(CONF_SCAN_INTERVAL, 10)) - 2, 1)
        self.client = BtHomeClient(host=config.get(CONF_HOST, 'bthomehub.home'), timeout=timeout)

        # Test the router is accessible
        try:
            self.client.authenticate()
            self.success_init = True
        except (AuthenticationException, ResponseException, RequestException):
            _LOGGER.exception("Failed to initialise BT Home Hub 6 Scanner. Device tracker will be disabled")
            self.success_init = False

    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()

        return list(self.last_results)

    def get_device_name(self, mac):
        """Return the name of the given device or None if we don't know."""
        if not self.success_init:
            return None

        # If not initialised and not already scanned and not found.
        if not self.last_results:
            self._update_info()

            if mac not in self.last_results:
                return None

        return self.last_results.get(mac)

    def _update_info(self):
        """Ensure the information from the BT Home Hub is up to date.
        Return boolean if scanning successful.
        """
        if not self.success_init:
            return False

        try:
            results = self.client.get_devices()
        except AuthenticationException:
            self.client.authenticate()
            return False
        except (ResponseException, RequestException):
            _LOGGER.exception('Failed to scan for devices')
            return False

        self.last_results = results
        return True
