import databases
from sqlalchemy import create_engine, MetaData

from settings.config import DATABASE_URL

database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()
