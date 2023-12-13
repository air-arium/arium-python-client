import sys

sys.path.append("../../src")

from api_call.client import APIClient
from auth.okta_auth import Auth
import urllib3

urllib3.disable_warnings()

from config.get_logger import get_logger

logger = get_logger("auth")
logger.setLevel("ERROR")

logger = get_logger("api_call")
logger.setLevel("INFO")


prefix = "PDCA"
auth_settings = {
}

auth = Auth(
    tenant="",
    role="admin",
    settings=auth_settings,
    authorization_code=False,
    verify=False,
)
client = APIClient(auth=auth)

print(f"Credits: {client.get_pdca().get_credits()}")
