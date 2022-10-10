from fastapi import FastAPI
import uvicorn


app = FastAPI()

@app.get('/')
def home():
    return {'status': 'Working 123asd'}



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)