
# How to run

### without docker
### from root app run

    poetry install
    poetry shell
    poetry run python3 main.py

### with docker

    docker build -t appimage .
    docker run -p 8000:8000 -v "$(pwd)/src:/app/src" appimage

### app must be running on `localhost:8000` 

