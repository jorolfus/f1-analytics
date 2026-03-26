from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.driver import DriverRead
from app.database.models import Driver
from app.database.session import async_session_maker, create_db_and_tables


async def speicher(driver: DriverRead, session: AsyncSession):
    db_driver = Driver(
        name=driver.name,
        team=driver.team,
        laps=driver.laps,
        year=driver.year,
        country_name=driver.country_name,
    )

    session.add(db_driver)
    await session.commit()
    await session.refresh(db_driver)


async def main():
    await create_db_and_tables()
    driver = DriverRead(
        id=0,
        name="Max Verstappen",
        team="Red Bull",
        laps={"1": "1:20.123"},
        year=2023,
        country_name="Netherlands",
    )

    async with async_session_maker() as session:
        await speicher(driver, session)
