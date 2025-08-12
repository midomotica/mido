"""Sensor para MiDo Cover Counter."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities
) -> None:
    """Configura la entidad del sensor tras el setup."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CoverCountSensor(coordinator)], True)

class CoverCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor que muestra el número de entidades cover."""

    _attr_translation_key = "cover_count"
    _attr_has_entity_name = True
    _attr_unique_id = f"{DOMAIN}_cover_count"
    _attr_unit_of_measurement = "count"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DOMAIN)},
            "name": "Cover Counter",
            "manufacturer": "MiDo",
            "model": "Cover Counter",
        }

    @property
    def state(self) -> int:
        """Devuelve el número actual de entidades cover."""
        return self.coordinator.data.get("cover_count", 0)

    @property
    def available(self) -> bool:
        return True
        
    @property
    def extra_state_attributes(self) -> dict:
        """Atributos extra: lista de covers filtrados y timestamp."""
        detected = self.coordinator.data.get("detected_covers", [])
        last = self.coordinator.last_update_success
        return {
            "detected_covers": detected,
            "last_updated": last.isoformat() if last else None
        }