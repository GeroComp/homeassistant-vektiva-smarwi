"""Cover entity for Vektiva Smarwi."""

import logging
import time
import asyncio
from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
    CoverDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .smarwi_control import SmarwiControl, SmarwiControlItem

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Smarwi covers from a config entry."""
    ctl = SmarwiControl(entry.data["hosts"])
    entities = [VektivaSmarwi(ctli) for ctli in ctl.list()]
    async_add_entities(entities, True)


class VektivaSmarwi(CoverEntity):
    """Representation of a Smarwi window opener."""

    # ✅ Nové konstanty místo deprecated
    _attr_device_class = CoverDeviceClass.WINDOW
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, ctli: SmarwiControlItem):
        self._ctli = ctli
        self._attr_name = ctli.name
        self._attr_unique_id = ctli.id
        self._fw = ctli.fw

        self._attr_current_cover_position = 0
        self._attr_is_closed = True

        self._opening = False
        self._closing = False
        self._requested_position = 0
        self._last_change = time.time()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._attr_name,
            "manufacturer": "Vektiva",
            "model": "Smarwi",
            "sw_version": self._fw,
        }

    @property
    def is_closed(self) -> bool | None:
        return self._attr_is_closed

    @property
    def current_cover_position(self) -> int | None:
        return self._attr_current_cover_position

    @property
    def is_opening(self) -> bool | None:
        return self._opening

    @property
    def is_closing(self) -> bool | None:
        return self._closing

    @property
    def icon(self):
        """Dynamická ikona podle stavu okna."""
        if self._attr_current_cover_position == 0:
            return "mdi:window-closed"
        elif self._attr_current_cover_position == 100:
            return "mdi:window-open"
        else:
            return "mdi:window-open-variant"

    def _set_position(self, pos: int):
        """Update position and closed state."""
        self._attr_current_cover_position = max(0, min(100, int(pos)))
        self._attr_is_closed = self._attr_current_cover_position == 0
        self._last_change = time.time()

    async def async_open_cover(self, **kwargs):
        self._opening = True
        self._closing = False
        self.async_write_ha_state()
        try:
            await self._ctli.open()
            await asyncio.sleep(1)
            self._set_position(100)
        finally:
            self._opening = False
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        self._closing = True
        self._opening = False
        self.async_write_ha_state()
        try:
            await self._ctli.close()
            await asyncio.sleep(1)
            self._set_position(0)
        finally:
            self._closing = False
            self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        pos = kwargs.get("position")
        if pos is None:
            return
        pos = int(pos)
        self._opening = pos > (self.current_cover_position or 0)
        self._closing = pos < (self.current_cover_position or 0)
        self.async_write_ha_state()
        try:
            await self._ctli.set_position(pos)
            await asyncio.sleep(1)
            self._set_position(pos)
        finally:
            self._opening = False
            self._closing = False
            self.async_write_ha_state()

    async def async_update(self):
        """Refresh state from device."""
        try:
            status = await self._ctli.status()
            self._set_position(status.position)
        except Exception as err:
            _LOGGER.debug("Failed to refresh Smarwi status: %s", err)
