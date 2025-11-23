"""Config flow for Vektiva Smarwi integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class SmarwiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vektiva Smarwi."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Zde můžeš validovat hosta (např. ping na zařízení)
            return self.async_create_entry(title="Vektiva Smarwi", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("hosts"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
