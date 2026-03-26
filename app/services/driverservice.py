from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.database.models import Driver
from app.services.openf1 import get_lap_times_from_driver
from app.database.speicher import speicher


class DriverService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, year: int, country_name: str, driver_name: str):
        statement = select(Driver).where(
            Driver.year == year,
            Driver.name == driver_name,
            Driver.country_name == country_name,
        )

        result = await self.session.execute(statement)

        driver = result.first()

        if driver is not None:
            return driver[0]

        driver = await get_lap_times_from_driver(year, country_name, driver_name)
        if driver is None:
            raise HTTPException(status_code=404, detail="Driver not found")

        await speicher(driver, self.session)
        return driver
