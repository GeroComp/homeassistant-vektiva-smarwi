"""Sensor platform for Vektiva Smarwi."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .smarwi_control import SmarwiControl

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    ctl = SmarwiControl(config_entry.data["hosts"])
    entities = []
    for ctli in ctl.list():
        entities.append(SmarwiDiag(ctli, "diag", "Diagnostika"))
        entities.append(SmarwiDiag(ctli, "state", "Stav okna"))
        # Zde jsem změnil název na "Otevření okna"
        entities.append(SmarwiDiag(ctli, "pos", "Otevření okna"))
    async_add_entities(entities, True)

class SmarwiDiag(SensorEntity):
    def __init__(self, ctli, kind, name):
        self._ctli = ctli
        self._kind = kind
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_unique_id = f"{ctli.id}_{kind}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if kind == "pos": self._attr_native_unit_of_measurement = "%"

    @property
    def device_info(self):
        return {'identifiers': {("cover", self._ctli.id)}, 'name': self._ctli.name, 'manufacturer': 'Vektiva', 'model': "Smarwi"}

    async def async_update(self):
        try:
            data = await self._ctli.get_status()
            pos = data.get("pos")
            
            if self._kind == "diag":
                self._attr_native_value = "Online"
                self._attr_icon = "mdi:wifi-check"
                self._attr_extra_state_attributes = {"fw": data.get("fw")}

            elif self._kind == "state":
                if pos == 'o': 
                    self._attr_native_value = "Otevřeno"
                    self._attr_icon = "mdi:window-open-variant"
                elif pos == 'c': 
                    self._attr_native_value = "Zavřeno"
                    self._attr_icon = "mdi:window-closed-variant"
                else: 
                    self._attr_native_value = "Neznámý"
                    self._attr_icon = "mdi:alert-circle-outline"

            elif self._kind == "pos":
                # --- ZDE JE UPRAVENÁ ČÁST PRO IKONY ---
                if pos == 'c': 
                    self._attr_native_value = 0
                    self._attr_icon = "mdi:window-closed-variant" # Ikona pro zavřeno
                elif pos == 'o': 
                    self._attr_native_value = 100
                    self._attr_icon = "mdi:window-open-variant"   # Ikona pro otevřeno
                else: 
                    self._attr_native_value = 50
                    self._attr_icon = "mdi:window-shutter-open"   # Ikona pro mezipolohu

        except:
            self._attr_native_value = "Odpojeno"
            self._attr_icon = "mdi:wifi-off"