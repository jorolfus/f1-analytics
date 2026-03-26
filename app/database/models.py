from sqlalchemy import JSON
from sqlmodel import Column, SQLModel, Field


class Driver(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    team: str
    laps: dict = Field(sa_column=Column(JSON))
    year: int
    country_name: str
