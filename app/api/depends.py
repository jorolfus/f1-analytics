from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services.driverservice import DriverService


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_driver_service(session: SessionDep) -> DriverService:
    return DriverService(session)


ServiceDep = Annotated[DriverService, Depends(get_driver_service)]
