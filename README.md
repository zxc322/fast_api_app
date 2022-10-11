
# How to run

### Manual way
### from root app run

    poetry install
    poetry shell
    poetry run python3 main.py

### Docker way
### How to run with docker

    docker build .
    docker run -p 8000:8000 <image_id>

### app must be running on `localhost:8000` 