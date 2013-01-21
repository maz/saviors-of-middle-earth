import os

DEVELOPMENT="development"
PRODUCTION="production"

try:
    env=DEVELOPMENT if os.environ['SERVER_SOFTWARE'].startswith('dev') else PRODUCTION
except:
    env=PRODUCTION
