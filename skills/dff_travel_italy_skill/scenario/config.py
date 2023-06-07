import os  
from dotenv import load_dotenv

load_dotenv()

TERMINUSDB_SERVER_DB = os.getenv("TERMINUSDB_SERVER_DB")
TERMINUSDB_SERVER_TEAM = os.getenv("TERMINUSDB_SERVER_TEAM")
TERMINUSDB_SERVER_PASSWORD = os.getenv("TERMINUSDB_SERVER_PASSWORD")
assert TERMINUSDB_SERVER_PASSWORD, "TerminusDB server password is not specified in env"
TERMINUSDB_SERVER_URL = os.getenv("TERMINUSDB_SERVER_URL")
