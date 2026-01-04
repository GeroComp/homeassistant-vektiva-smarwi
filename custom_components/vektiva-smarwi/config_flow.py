"""Config flow for Vektiva Smarwi integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.components import dhcp, zeroconf

from .const import DOMAIN
from .smarwi_control import SmarwiControl


class SmarwiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vektiva Smarwi."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.discovered_host: str | None = None
        self.discovered_name: str | None = None

    async def _async_handle_discovery(self, host: str, name: str, unique_id: str | None = None) -> FlowResult:
        """Reusable discovery handler."""
        self.discovered_host = host
        # Zkrátíme jméno (odstraníme .local apod.)
        self.discovered_name = name.split(".")[0]

        # Pokud máme unique_id (MAC), použijeme ho pro kontrolu duplicity
        if unique_id:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(updates={"hosts": self.discovered_host})
        
        # Pokud nemáme MAC, zkusíme alespoň zastavit duplicitní hosty
        self._async_abort_entries_match({"hosts": self.discovered_host})

        self.context["title_placeholders"] = {"name": self.discovered_name}
        return await self.async_step_discovery_confirm()

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult:
        """Handle zeroconf discovery (mDNS)."""
        # Zkusíme najít MAC v properties, pokud tam je
        mac = discovery_info.properties.get("mac")
        return await self._async_handle_discovery(
            host=discovery_info.host,
            name=discovery_info.name.replace("._http._tcp.local.", ""),
            unique_id=mac
        )

    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult:
        """Handle DHCP discovery."""
        return await self._async_handle_discovery(
            host=discovery_info.ip,
            name=discovery_info.hostname,
            unique_id=discovery_info.macaddress
        )

    async def async_step_discovery_confirm(self, user_input: dict | None = None) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.discovered_name or "Vektiva Smarwi",
                data={"hosts": self.discovered_host}
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self.discovered_name},
        )

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validace hosta pomocí SmarwiControl
            ctl = SmarwiControl(user_input["hosts"])
            
            # Zkusíme se připojit
            if await ctl.authenticate():
                # Pokud se podaří připojit, vytvoříme záznam
                # Použijeme název ze zařízení nebo výchozí
                title = ctl.title if ctl.title else "Vektiva Smarwi"
                return self.async_create_entry(title=title, data=user_input)
            else:
                # Pokud se nepodaří připojit, vyhodíme chybu definovanou v strings.json
                errors["base"] = "cannot_connect"

        # Pokud jsme přišli z discovery, předvyplníme hosta
        default_host = self.discovered_host or ""

        schema = vol.Schema(
            {
                vol.Required("hosts", default=default_host): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)