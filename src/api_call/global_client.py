from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from api_call.client import APIClient


def set_client(client: 'APIClient', workspace):
    global global_client
    if global_client is None:
        global_client = {}
    global_client[workspace] = client


def get_client(workspace="workspace2") -> Union[None, 'APIClient']:
    global global_client
    if isinstance(global_client, dict):
        return global_client.get(workspace, global_client[list(global_client.keys())[-1]])
    return None


global_client = None
