from dotenv import load_dotenv
import os

# Load environment variables in .env
load_dotenv()
ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")

# Ensure that Alchemy URL was set
if not ALCHEMY_KEY:
    print("No ALCHEMY_KEY was configured in .env!")
    exit(0)

ALCHEMY_URL = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}'

# Directory to store locally downloaded images temporarily
IMAGE_CACHE_DIR = "imageCache"
DEFAULT_RATE_LIMIT_COOLDOWN_TIME = 120
MAX_COOLDOWN_TIME = 240