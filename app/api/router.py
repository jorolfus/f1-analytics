from fastapi import APIRouter, HTTPException, status

from app.database.models import Driver
from app.api.depends import ServiceDep

router = APIRouter()


@router.get("/driver/{year}/{country_name}/{driver_name}", response_model=Driver)
async def get_driver_laps_from_race(
    year: int, country_name: str, driver_name: str, service: ServiceDep
):
    driver_name = " ".join(driver_name.split("_")).lower()
    driver = await service.get(year, country_name, driver_name)

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )
    return driver
