import os, json
import logging
from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from src.routers.authorization import authenticate
import uvicorn
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.types import Scope
from ratelimit.backends.simple import MemoryBackend

from src.routers import services_routers
# from src.routers.authorization import authenticate

app = FastAPI()
# app = FastAPI(dependencies=[Depends(authenticate)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
async def dummy_auth_function(scope: Scope) -> tuple[str, str]:
    return "dummy_uid", "default"
app.add_middleware(
    RateLimitMiddleware,
    authenticate = dummy_auth_function,
    backend=MemoryBackend(),
    config={
        r"^/ntq_services": [Rule(second=150)],
    },
)

app.include_router(services_routers.router, prefix="", tags=["ntq_services"])

def main():
    uvicorn.run("src.main_vi:app", host="0.0.0.0", port=6064)
    logging.info('Services already to use! ......')
if __name__ == "__main__":
    main()
