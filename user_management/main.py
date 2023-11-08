from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware

from user_management.api.auth.routes import auth_router
from user_management.config import config

app = FastAPI(docs_url="/")


@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(status_code=200, content={"status": "healthy"})


origins = config.ALLOWED_HOSTS

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
