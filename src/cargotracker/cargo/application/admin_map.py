from collections.abc import Mapping

from cargotracker.cargo.application import admin_map_data
from cargotracker.cargo.application.admin_map_data import build_cargo_map_data
from cargotracker.cargo.domain.repository import CargoRepository

UNKNOWN_LOCATION = admin_map_data.UNKNOWN_LOCATION


def build_admin_map_data(
    cargo_repository: CargoRepository,
    location_coordinates: Mapping[str, tuple[float, float]],
) -> list[dict[str, object]]:
    return [
        build_cargo_map_data(cargo, location_coordinates) for cargo in cargo_repository.find_all()
    ]
