"""Inicialización de MiDo Cover Counter."""

import logging
from datetime import timedelta, datetime, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import entity_registry as er

#20250812
from homeassistant.helpers.tag import async_create as async_create_tag  


from .const import DOMAIN, DEFAULT_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura la integración tras completar el config_flow."""
    interval = entry.data.get("update_interval", DEFAULT_INTERVAL)

# 20250812 Crear la etiqueta "mido_excluido"
    await async_create_tag(hass, "mido_excluido", "Etiqueta creada por la integración MiDo")

    async def async_fetch_data():
        """Cuenta todos los covers en HA, excluyendo los etiquetados 'excluido'."""
        try:
            registry = er.async_get(hass)
            valid: list[str] = []
            # Recorre todos los cover.* de Home Assistant
            for entity_id in hass.states.async_entity_ids("cover"):
                # 1) Recupera el registro de la entidad
                entry_obj = registry.async_get(entity_id)
                _LOGGER.debug("RegistryEntry para %s: %s", entity_id, entry_obj)
                _LOGGER.debug(" > opciones (entry_obj.options): %s", entry_obj.options)
                # 2) Las etiquetas de la UI van a entry_obj.tags, no a options
                labels = list(entry_obj.labels) if entry_obj else []
                _LOGGER.debug("Mido Cover Counter: %s labels = %s", entity_id, labels)
                # 3) Si la etiqueta "excluido" está presente, omitimos esta entidad
                if "excluido" in labels:
                    continue
                # 4) Si pasa el filtro, la añadimos al listado
                valid.append(entity_id)
            return {"cover_count": len(valid), "detected_covers": valid}
        except Exception as err:
            raise UpdateFailed(f"Error obteniendo entidades cover: {err}") from err

    # Crear y configurar el coordinador
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="MiDo Cover Counter",
        update_method=async_fetch_data,
        update_interval=timedelta(seconds=interval),
    )

    # Inicializar estado mínimo para que la entidad salga disponible
    registry = er.async_get(hass)
    init_valid: list[str] = []
    for entity_id in hass.states.async_entity_ids("cover"):
        entry_obj = registry.async_get(entity_id)
        labels = entry_obj.options.get("labels", []) if entry_obj else []
        if "excluido" in labels:
            continue
        init_valid.append(entity_id)
    coordinator.data = {"cover_count": len(init_valid), "detected_covers": init_valid}
    coordinator.last_update_success = datetime.now(timezone.utc)

    # Primer refresh real sin bloquear
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning(
            "MiDo Cover Counter: primer refresh falló, manteniendo disponible: %s",
            err
        )

    # Guardar coordinador y forwardear a sensor
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Limpia la integración al eliminar la entrada."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok