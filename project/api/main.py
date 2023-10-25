from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from project.env_config import env

app = FastAPI()


@app.get("/")
def index():
    return {}


origins = env.ALLOWED_HOSTS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
