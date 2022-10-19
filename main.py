from fastapi import FastAPI, Response, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging, random, string
from datetime import datetime

from db.connection import database
from my_redis.config import init_redis_pool
from api_routers import routers
app = FastAPI()

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

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
    return {'status': 'Working'}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """ Writing request exequting time to file """

    logger.info(f"Starting request path={request.url.path}")
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time) * 1000
    logger.info(f"Request   completed_in={process_time}ms status_code={response.status_code}")
    with open('logs_response_time.log','a') as f:
        f.write('REQUEST [URL]={} [EXECUTE_TIME]={}s [STATUS_CODE]={}\n'.format(request.url.path, process_time, response.status_code))
    
    
    return response

app.include_router(routers.api_router)



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)