import logging
import pymongo
import mongomock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = "mongodb://localhost:27017"
TIMEOUT_MS = 2000

# Databases from schema
DB_NAMES = [
    "ai_services",
    "ai_tools",
    "auth_DB",
    "chat_with_pdf_qdrant",
    "file_DB",
    "mom",
    "offline_chatbot",
    "sandarbh",
    "scan_to_word",
    "scanned_to_readable",
    "summarization",
    "user_DB"
]

try:
    logger.info("Attempting connection to local MongoDB...")
    client = pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=TIMEOUT_MS,
        connectTimeoutMS=TIMEOUT_MS
    )
    # Trigger a command to test connection
    client.admin.command('ping')
    logger.info("Successfully connected to real MongoDB instance.")
    is_mock = False
except Exception as e:
    logger.warning(f"Could not connect to real MongoDB (error: {e}). Falling back to in-memory mongomock database.")
    client = mongomock.MongoClient()
    is_mock = True

# Create database dict
dbs = {}
for db_name in DB_NAMES:
    dbs[db_name] = client[db_name]

def get_db(db_name):
    if db_name not in dbs:
        raise ValueError(f"Database {db_name} is not pre-registered in backend.")
    return dbs[db_name]

def get_client():
    return client

def check_is_mock():
    return is_mock
