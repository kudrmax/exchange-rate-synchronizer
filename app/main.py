import uvicorn
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from api import CurrencyAPI

Base.metadata.create_all(bind=engine)

api = CurrencyAPI()
api.app.mount("/static", StaticFiles(directory="app/static/plots"), name="static")

if __name__ == "__main__":
    uvicorn.run('main:api.app', host="0.0.0.0", port=8000, reload=True)
