from sqlmodel import SQLModel


class DriverRead(SQLModel):
    id: int | None
    name: str
    team: str
    laps: dict
    year: int
    country_name: str
