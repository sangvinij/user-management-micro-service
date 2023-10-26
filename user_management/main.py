from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from user_management.env_config import env

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(status_code=200, content={"status": "healthy"})


origins = env.ALLOWED_HOSTS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
