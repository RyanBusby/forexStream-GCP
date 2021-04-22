import os

SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

u, p = os.getenv('uname'), os.getenv('upass')
ip = os.getenv('db_ip')
db = os.getenv('db_name')
port = os.getenv('port')

SQLALCHEMY_DATABASE_URI =\
f'postgresql://{u}:{p}@{db_ip}:{port}/{db}'
