from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("EE_DATABASE_URL", cast=str, default="")
SECRET_KEY = config("EE_SECRET_KEY", cast=str, default="")
ALGORITHM = config("EE_ALGORITHM", cast=str, default="")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("EE_ACCESS_TOKEN_EXPIRE_MINUTES", cast=str, default=""))