"""Sensor platform for Vektiva Smarwi."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .smarwi_control import SmarwiControl

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Nastavení senzorů."""
    ctl = SmarwiControl(config_entry.data["hosts"])
    entities = []
    for ctli in ctl.list():
        entities.append(SmarwiDiag(ctli, "diag", "Diagnostika"))
        entities.append(SmarwiDiag(ctli, "state", "Stav okna"))
        entities.append(SmarwiDiag(ctli, "pos", "Otevření okna"))
    async_add_entities(entities, True)

class SmarwiDiag(SensorEntity):
    """Diagnostické senzory Smarwi."""

    def __init__(self, ctli, kind, name):
        self._ctli = ctli
        self._kind = kind
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_unique_id = f"{ctli.id}_{kind}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        
        if kind == "pos": 
            self._attr_native_unit_of_measurement = "%"

    @property
    def device_info(self):
        return {'identifiers': {("cover", self._ctli.id)}, 'name': self._ctli.name, 'manufacturer': 'Vektiva', 'model': "Smarwi"}

    async def async_update(self):
        """Aktualizace dat – nyní s propojením na stav coveru."""
        try:
            data = await self._ctli.get_status()
            pos_raw = data.get("pos")
            
            if self._kind == "diag":
                self._attr_native_value = "Online"
                self._attr_icon = "mdi:wifi-check"

            elif self._kind == "state":
                self._attr_native_value = "Otevřeno" if pos_raw == 'o' else "Zavřeno"
                self._attr_icon = "mdi:window-open-variant" if pos_raw == 'o' else "mdi:window-closed-variant"

            elif self._kind == "pos":
                if pos_raw == 'c':
                    self._attr_native_value = 0
                    self._attr_icon = "mdi:window-closed-variant"
                else:
                    # Pokusíme se získat aktuální polohu přímo z entity coveru v HA
                    cover_entity_id = f"cover.{self._ctli.id}"
                    state = self.hass.states.get(cover_entity_id)
                    
                    if state and "current_position" in state.attributes:
                        # Přebereme vypočítanou hodnotu (např. těch 37%)
                        self._attr_native_value = state.attributes["current_position"]
                    else:
                        # Záložní plán: pokud cover není dostupný, dáme 100
                        self._attr_native_value = 100
                    
                    self._attr_icon = "mdi:window-shutter-open" if self._attr_native_value < 100 else "mdi:window-open-variant"

        except Exception as err:
            _LOGGER.error("Update failed for %s sensor: %s", self._kind, err)
            if self._kind == "diag":
                self._attr_native_value = "Odpojeno"
                self._attr_icon = "mdi:wifi-off"