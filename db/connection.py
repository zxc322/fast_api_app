import databases

from settings.config import DATABASE_URL
database = databases.Database(DATABASE_URL)