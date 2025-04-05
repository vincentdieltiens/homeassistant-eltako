"""Handle the config flow for Eltako"""
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_DEVICE
from .const import DOMAIN, ERROR_INVALID_DONGLE_PATH, CONF_DELAY
import voluptuous as vol
from . import dongle
from homeassistant.core import callback

# ConfigFlow of HA is used to make the UI when the integration is 
# added/configured to HA
# We use this to define the path of the dongle at configuration

# OptionFlow of HA is used to make the UI for options
# We use this to define the minimum delay between the calls 
# (see issue https://github.com/vincentdieltiens/homeassistant-eltako/issues/4)

class EltakoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config"""

    # Define the flow to set up the configuration (dongle path)

    VERSION = 1
    MANUAL_PATH_VALUE = "Custom path"

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_detect()

    async def async_step_detect(self, user_input=None):
        """Propose a list of detected paths"""
        errors = {}
        if user_input is not None:
            if user_input[CONF_DEVICE] == self.MANUAL_PATH_VALUE:
                return await self.async_step_manual(None)
            if await self.validate_eltako_conf(user_input):
                return self.create_eltako_entry(user_input)
            errors = {CONF_DEVICE: ERROR_INVALID_DONGLE_PATH}

        bridges = [self.MANUAL_PATH_VALUE]
        bridges.extend(await self.hass.async_add_executor_job(dongle.detect))
        if len(bridges) == 1:
            return await self.async_step_manual(user_input)

        return self.async_show_form(
            step_id="detect",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE): vol.In(bridges)}),
            errors=errors,
        )

    async def async_step_manual(self, user_input=None):
        """Request manual EnOcean dongle path"""
        errors = {}
        default_value = ""
        if user_input is not None:
            if await self.validate_eltako_conf(user_input):
                return self.create_eltako_entry(user_input)
            default_value = user_input[CONF_DEVICE]
            errors = {CONF_DEVICE: ERROR_INVALID_DONGLE_PATH}

        config_schema = vol.Schema(
            {vol.Required(CONF_DEVICE, default=default_value): str}
        )

        return self.async_show_form(
            step_id="manual", data_schema=config_schema, errors=errors
        )

    async def validate_eltako_conf(self, user_input) -> bool:
        """Return True if the user_input contains a valid dongle path"""
        dongle_path = user_input[CONF_DEVICE]
        path_is_valid = await self.hass.async_add_executor_job(
            dongle.validate_path, dongle_path
        )
        return path_is_valid

    def create_eltako_entry(self, user_input):
        """Create the eltako configuration"""
        return self.async_create_entry(title="Eltako", data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input = None
    ):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Eltako", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DELAY,
                        default=self.config_entry.options.get(CONF_DELAY),
                    ): int
                }
            ),
            errors=errors
        )