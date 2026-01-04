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

MOVEMENT_DURATION = 17.0 

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
        self._opening = False
        self._closing = False
        self._closed = True
        self._current_position = 0
        self._movement_start_time = 0
        self._start_position_percentage = 0
        self._loop_task = None
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
    def current_cover_position(self):
        if not (self._opening or self._closing): return self._current_position
        elapsed = time.time() - self._movement_start_time
        progress = elapsed / MOVEMENT_DURATION
        if progress >= 1.0: progress = 1.0
        if self._opening: est = self._start_position_percentage + (progress * (100 - self._start_position_percentage))
        else: est = self._start_position_percentage - (progress * self._start_position_percentage)
        return int(max(0, min(100, est)))
    
    @property
    def is_opening(self): return self._opening
    @property
    def is_closing(self): return self._closing
    @property
    def is_closed(self): return self._current_position == 0

    async def async_open_cover(self, **kwargs): await self._move(100)
    async def async_close_cover(self, **kwargs): await self._move(0)
    async def async_set_cover_position(self, **kwargs): await self._move(int(kwargs[ATTR_POSITION]))
    
    async def async_stop_cover(self, **kwargs):
        if self._loop_task: self._loop_task.cancel()
        self._opening = False; self._closing = False
        await self._ctli.stop()
        await self.async_update()

    async def _move(self, target_pos):
        self._target_position = target_pos
        self._start_position_percentage = self._current_position
        self._movement_start_time = time.time()
        
        if target_pos > self._current_position:
            self._opening = True; self._closing = False; self._closed = False
            diff = target_pos - self._current_position
            await self._ctli.open()
        elif target_pos < self._current_position:
            self._opening = False; self._closing = True; self._closed = False
            diff = self._current_position - target_pos
            await self._ctli.close()
        else: return

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
        while True:
            if time.time() - start >= duration:
                if self._stop_task_scheduled:
                    await self._ctli.stop()
                    self._current_position = target_pos
                else:
                    self._current_position = target_pos
                break
            await asyncio.sleep(1)
            self.async_write_ha_state()
        self._opening = False; self._closing = False
        if self._current_position == 0: self._closed = True
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        if self._opening or self._closing: return
        try:
            res = await self._ctli.get_status()
            self._fw = res.get("fw")
            pos = res.get("pos")
            if pos == 'c': self._current_position = 0; self._closed = True
            elif pos == 'o': self._current_position = 100; self._closed = False
        except: pass