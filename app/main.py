from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router 
from app.logging_config import configure_logging


app = FastAPI()
configure_logging()

origins = [
    "http://localhost:3000",
    "https://example-frontend.com"  #replace with real domain 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)