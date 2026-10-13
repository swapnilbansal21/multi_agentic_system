import uvicorn

from src.core.auth import CurrentOfficer, get_current_officer
from src.main import app


async def _fake_officer():
    return CurrentOfficer(email="swapnilbansal37@gmail.com", roles=["Admin", "PA"])

app.dependency_overrides[get_current_officer] = _fake_officer

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
