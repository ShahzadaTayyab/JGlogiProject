# app/main.py

from fastapi import FastAPI
from app.database import engine
from app import models
from app.clients import router as clients_router
from app.bookings import router as bookings_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(clients_router, prefix="/clients", tags=["Clients"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])

if __name__ == "__main__":
    import uvicorn
    # run app on port 8000 with auto reload
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
