import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST', '127.0.0.2')
PORT = int(os.getenv('PORT', 5008))
VISIBLE_ROWS = 5  # Number of rows visible before scrolling
RECORDS_PER_PAGE = 25