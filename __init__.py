"""The profiler integration."""
import asyncio
import cProfile
import logging
import time

from pyprof2calltree import convert
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

SERVICE_START = "start"
CONF_SECONDS = "seconds"

DOMAIN = "profiler"

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the profiler component."""

    async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_START,
        _async_generate_profile,
        schema=vol.Schema({vol.Optional(CONF_SECONDS, default=60.0): float}),
    )

    return True


async def _async_generate_profile(call: ServiceCall):
    start_time = int(time.time() * 1000000)
    profiler = cProfile.Profile()
    profiler.enable()
    await asyncio.sleep(float(call.data.get(CONF_SECONDS)))
    profiler.disable()
    profiler.create_stats()
    profiler.dump_stats(f"profile.{start_time}.cprof")
    convert(profiler.getstats(), f"callgrind.out.{start_time}")
