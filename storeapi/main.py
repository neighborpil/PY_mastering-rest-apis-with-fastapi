import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from storeapi.database import database
from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Hello from lifespaan")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# 정적 파일을 제공하기 위한 디렉토리 마운트
app.mount("/static", StaticFiles(directory="storeapi/static"), name="static")


# favicon.ico 요청을 정적 파일로 리다이렉트
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


app.include_router(post_router)


# 기본 헬스체크 엔드포인트
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
