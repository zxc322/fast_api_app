
# How to run

### without docker
### from root app run

    poetry install
    poetry shell
    poetry run python3 main.py

### with docker (*supposed u have runing postgresql and redis)

    docker build -t appimage .
    docker run -p 8000:8000 -v "$(pwd)/src:/app/src" appimage

### or use docker-compose to run app with databases from docker

    docker-compose up --build

### app must be running on `localhost:8000` 
### postgres UI on `localhost:5050`
###### You can open with pass "zxc", add server with params ["host: postgres", "port:5432", "db_name:fastapi_dev", "username:zxc", "password:zxc"]
### redis UI on `localhost:8081`
###### You can open with ["user:zxc", "password:zxc"]
###### test redis on `localhost:8000/redis/{key}/{value} will add {"key": "value"} to redis


