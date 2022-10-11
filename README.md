
# How to run

### without docker
### from root app run

    poetry install
    poetry shell
    poetry run python3 main.py

### with docker

    docker build .
    docker run -p 8000:8000 -v "$(pwd)/src:/app/src" <image_id>

### app must be running on `localhost:8000` 

