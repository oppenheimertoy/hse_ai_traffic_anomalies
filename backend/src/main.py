import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI

# извините
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.api.http.v1.routers import api_router
from src.deps import make_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)

root_http_router = APIRouter(prefix="/api")
root_http_router.include_router(api_router)

app: FastAPI = make_app(root_http_router)


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    params: dict[str, Any] = {
        "host": "0.0.0.0",
    }
    params = {**params, "port": 8000, "reload": True}
    uvicorn.run("main:app", **params)


if __name__ == "__main__":
    main()
