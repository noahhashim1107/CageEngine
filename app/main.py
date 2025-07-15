from fastapi import FastAPI
from app.api import router 
from app.logging_config import configure_logging


app = FastAPI()
configure_logging()
app.include_router(router)