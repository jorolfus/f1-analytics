from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()

drivers = [
    {"name": "Hamilton", "team": "Ferrari"},
    {"name": "Verstappen", "team": "Red Bull"},
]


@app.get("/drivers")
def get_drivers():
    return drivers


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
