"""The Vektiva Smarwi integration."""
import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

# Importujeme konstanty pro cover
from homeassistant.components.cover import DOMAIN as COVER_DOMAIN, ATTR_POSITION

DOMAIN = "vektiva_smarwi"
# PŘIDÁNO "button" do seznamu platforem
PLATFORMS = ["cover", "sensor", "button"]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Vektiva Smarwi component."""
    
    async def handle_ventilation(call: ServiceCall):
        """Služba pro otevření na mikroventilaci (15%)."""
        await hass.services.async_call(
            COVER_DOMAIN,
            "set_cover_position",
            {
                "entity_id": call.data.get("entity_id"),
                ATTR_POSITION: 15
            }
        )

    # Registrace služby v Home Assistantu (pro automatizace)
    hass.services.async_register(DOMAIN, "open_ventilation", handle_ventilation)
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Vektiva Smarwi from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)