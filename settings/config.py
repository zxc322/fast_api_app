from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("EE_DATABASE_URL", cast=str, default="")

#  jwt

SECRET_KEY = config("EE_SECRET_KEY", cast=str, default="")
ALGORITHM = config("EE_ALGORITHM", cast=str, default="")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("EE_ACCESS_TOKEN_EXPIRE_MINUTES", cast=str, default=""))

#  auth0

auth0_config = {
    "DOMAIN": config("EE_DOMAIN", cast=str, default=""),
    "API_AUDIENCE": config("EE_API_AUDIENCE", cast=str, default=""),
    "ISSUER": config("EE_ISSUER", cast=str, default=""),
    "AUTH0_ALGORITHM": config("EE_AUTH0_ALGORITHM", cast=str, default="")
    } 


