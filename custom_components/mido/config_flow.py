"""Config flow para MiDo Cover Counter."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, DEFAULT_INTERVAL

DATA_SCHEMA = vol.Schema({
    vol.Required("update_interval", default=DEFAULT_INTERVAL): int,
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manejo del flujo de configuración."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Paso inicial: solicita el intervalo de actualización."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title="Cover Counter",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )
