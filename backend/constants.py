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
DEFAULT_RATE_LIMIT_COOLDOWN_TIME = 60
MAX_COOLDOWN_TIME = 240

# Load AWS Credentials 
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    print("No AWS credentails were configured in .env!")
    exit(0)

# AWS S3 bucket name
BUCKET_NAME = 'nftbatchdownload'
_AWS_REGION = 'us-east-1'
BUCKET_URL_PREFIX = f'https://s3.console.aws.amazon.com/s3/buckets/{BUCKET_NAME}?region={_AWS_REGION}&tab=objects'

# Config
IS_TESTING = True