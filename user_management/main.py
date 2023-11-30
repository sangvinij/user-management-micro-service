from botocore.exceptions import EndpointConnectionError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware

from user_management.api.auth.routes import auth_router
from user_management.api.users.routes import user_router
from user_management.config import config
from user_management.logger_settings import logger

app = FastAPI(docs_url="/")


@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(status_code=200, content={"status": "healthy"})


origins = config.ALLOWED_HOSTS

app.include_router(auth_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")

    response = await call_next(request)

    response_body: bytes = b""

    async for chunk in response.body_iterator:
        response_body += chunk

    logger.info(f"Sent response: status_code: {response.status_code}, body: {response_body}\n")

    return Response(
        status_code=response.status_code,
        content=response_body,
        headers=dict(response.headers),
    )


@app.exception_handler(EndpointConnectionError)
async def aws_exception_handler(request: Request, exc: EndpointConnectionError):
    logger.error(exc)
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": "aws error"})
