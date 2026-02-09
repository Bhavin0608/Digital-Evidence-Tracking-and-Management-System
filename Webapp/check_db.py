# this is used to check the connection to the database before running the server.......

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.db import connections
from django.db.utils import OperationalError

db_conn = connections['default']
try:
    c = db_conn.cursor()
    print("Connection to the PostgreSQL database successful!")
except OperationalError as e:
    print(f"Failed to connect to the PostgreSQL database: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
