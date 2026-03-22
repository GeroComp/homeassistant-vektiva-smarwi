"""Button platform for Vektiva Smarwi."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .smarwi_control import SmarwiControl

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Nastavení tlačítek z konfiguračního vstupu."""
    ctl = SmarwiControl(config_entry.data["hosts"])
    entities = []
    for ctli in ctl.list():
        entities.append(SmarwiVentilationButton(ctli))
    async_add_entities(entities, True)

class SmarwiVentilationButton(ButtonEntity):
    """Tlačítko pro rychlé nastavení mikroventilace (15%)."""

    def __init__(self, ctli):
        self._ctli = ctli
        self._attr_name = "Mikroventilace"
        self._attr_unique_id = f"{ctli.id}_vent_btn"
        self._attr_icon = "mdi:window-open-variant"

    @property
    def device_info(self):
        """Přiřazení tlačítka ke správnému zařízení okna."""
        return {
            "identifiers": {("cover", self._ctli.id)},
            "name": self._ctli.name,
        }

    async def async_press(self) -> None:
        """Akce po stisknutí tlačítka v UI."""
        await self._ctli.set_position(10)