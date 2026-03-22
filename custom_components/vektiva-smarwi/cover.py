"""Platform for cover integration."""
import logging
import time
import asyncio
import voluptuous

import homeassistant.helpers.config_validation as cv
from homeassistant.components.cover import PLATFORM_SCHEMA, CoverEntity, ATTR_POSITION
from homeassistant.const import CONF_HOSTS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .smarwi_control import SmarwiControl

try:
    from homeassistant.components.cover import CoverEntityFeature, CoverDeviceClass
except ImportError:
    from homeassistant.components.cover import CoverEntityFeatures as CoverEntityFeature
    from homeassistant.components.cover import CoverDeviceClass

_LOGGER = logging.getLogger(__name__)

MOVEMENT_DURATION = 12.0 

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Required(CONF_HOSTS): cv.string,
})

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    ctl = SmarwiControl(config_entry.data["hosts"])
    async_add_entities([VektivaSmarwi(ctli) for ctli in ctl.list()], True)
    return True

class VektivaSmarwi(CoverEntity):
    def __init__(self, ctli):
        self._ctli = ctli
        self._name = ctli.name
        self._id = ctli.id
        self._fw = None
        self._current_position = 0
        self._start_position = 0
        self._closed = True
        self._opening = False
        self._closing = False
        self._loop_task = None
        self._movement_start_time = 0
        self._stop_task_scheduled = False

    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._id
    @property
    def device_info(self):
        return {'identifiers': {("cover", self._id)}, 'name': self._name, 'manufacturer': 'Vektiva', 'model': "Smarwi"}
    @property
    def device_class(self): return CoverDeviceClass.WINDOW
    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION | CoverEntityFeature.STOP
    
    @property
    def is_closed(self): return self._closed
    @property
    def is_opening(self): return self._opening
    @property
    def is_closing(self): return self._closing
    @property
    def current_cover_position(self): return self._current_position

    async def async_open_cover(self, **kwargs): await self.async_set_cover_position(position=100)
    async def async_close_cover(self, **kwargs): await self.async_set_cover_position(position=0)
    
    async def async_stop_cover(self, **kwargs):
        await self._ctli.stop()
        if self._loop_task: self._loop_task.cancel()
        self._opening = False; self._closing = False
        await self.async_update()
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        target_pos = kwargs.get(ATTR_POSITION)
        if target_pos is None or target_pos == self._current_position: return

        self._start_position = self._current_position
        self._opening = target_pos > self._current_position
        self._closing = target_pos < self._current_position
        self._movement_start_time = time.time()
        
        await self._ctli.set_position(target_pos)

        diff = abs(target_pos - self._current_position)
        travel_time = (diff / 100.0) * MOVEMENT_DURATION
        
        if target_pos in [0, 100]:
            travel_time += 2.0
            self._stop_task_scheduled = False
        else:
            self._stop_task_scheduled = True

        if self._loop_task: self._loop_task.cancel()
        self.async_write_ha_state()
        self._loop_task = asyncio.create_task(self._loop(travel_time, target_pos))

    async def _loop(self, duration, target_pos):
        start = self._movement_start_time
        start_pos = self._start_position
        while True:
            elapsed = time.time() - start
            if elapsed >= duration:
                if self._stop_task_scheduled: await self._ctli.stop()
                self._current_position = target_pos
                break
            
            progress = elapsed / duration
            self._current_position = int(start_pos + (target_pos - start_pos) * progress)
            self._current_position = max(0, min(100, self._current_position))
            self.async_write_ha_state()
            await asyncio.sleep(0.5)
            
        self._opening = False; self._closing = False
        self._closed = (self._current_position == 0)
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        if self._opening or self._closing: return
        try:
            res = await self._ctli.get_status()
            pos = res.get("pos")
            if pos == 'c':
                self._current_position = 0; self._closed = True
            elif pos == 'o':
                if self._current_position == 0: self._current_position = 100
                self._closed = False
        except Exception: pass