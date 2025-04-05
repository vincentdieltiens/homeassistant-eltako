""""""
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .teachin.service import eltako_teachin, eltako_teachout

from .const import DOMAIN, LOGGER, TEACH_IN, TEACH_OUT

CALL_ATTR_TEACH_IN_SECONDS = "teach_in_time"
CALL_ATTR_TEACH_IN_BASE_ID_TO_USE = "base_id"
CALL_ATTR_TEACH_IN_SECONDS_DEFAULT_VALUE_STR = "60"
CALL_ATTR_TEACH_IN_SECONDS_DEFAULT_VALUE = 60

CONF_SENDER_ID = "sender_id"

TEACHIN_STATE = "eltako.service_teachin_state"
TEACHIN_STATE_VALUE_RUNNING = "RUNNING"
TEACHIN_MAX_RUNTIME = 600

SERVICE_SCHEMA = {
    TEACH_IN: vol.All(
        vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Required(CONF_TYPE): cv.string,
            }
        )
    ),
    TEACH_OUT: vol.All(
        vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Required(CONF_TYPE): cv.string,
            }
        )
    ),
}


def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services"""

    services = {TEACH_IN: eltako_teachin, TEACH_OUT: eltako_teachout}

    def call_eltako_service(service_call: ServiceCall) -> None:
        LOGGER.info("Call service %s", str(service_call.service))
        services[service_call.service](hass, service_call)
        LOGGER.info("Service %s has been called", str(service_call.service))

    for service in services:
        hass.services.async_register(
            DOMAIN, service, call_eltako_service, schema=SERVICE_SCHEMA.get(service)
        )
        LOGGER.debug("Request to register service %s has been sent", str(service))

    return True
