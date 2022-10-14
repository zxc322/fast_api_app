from fastapi import FastAPI, Response, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from db.connection import database
from db.base import SessionLocal, engine
from my_redis.config import init_redis_pool
from api_routers import routers

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    app.state.redis = await init_redis_pool()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await app.state.redis.close()


@app.get('/')
def home():
    return {'status': 'Working111'}

#  gor test redis 

@app.get('/redis/{key}/{value}/')
async def redis_test(key: str, value: str):
    try:
        await app.state.redis.set(key, value)
        value = await app.state.redis.get(key)
    except Exception as ex:  # noqa: E722
        print(ex, "Smth wrong...")
    return {key:value}

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

app.include_router(routers.api_router)



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)