import os
from dotenv import load_dotenv

# Skip the optional timezone probe during init
os.environ['RUN_TIMEZONE_CHECK'] = '0'

from db import init_db  # local module in same folder

load_dotenv()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Done.")