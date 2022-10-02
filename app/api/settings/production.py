import os

dbuser = os.environ.get('VAPOR_DBUSER', 'user_vapormap')
password = os.environ.get('VAPOR_DBPASS', 'vapormap')
dbhost = os.environ.get('VAPOR_DBHOST', 'localhost')
dbname = os.environ.get('VAPOR_DBNAME', 'db_vapormap')

SECRET_KEY = os.environ.get('VAPOR_SECRET_KEY', 'gjhliksqsdfghsdgfbhsdkjgnlkdsfj:nglbksjdhnbk')

SQLALCHEMY_DATABASE_URI = F'mysql://{dbuser}:{password}@{dbhost}/{dbname}'