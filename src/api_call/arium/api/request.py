import json
import logging.config
from http import HTTPStatus
from time import sleep
from typing import List, Optional, Dict, Callable, Union
from typing import TYPE_CHECKING
from uuid import UUID

import urllib3
from requests.models import Response

from constants import LOGGING_CONFIG

if TYPE_CHECKING:
    from api_call.client import APIClient

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class AriumException(Exception):
    def __init__(self, response):
        self.response = response


def exception_handler(fun):
    def wrapper(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except AriumException as e:
            try:
                content_message = json.loads(e.response.content).get('message', 'No message.')
            except json.decoder.JSONDecodeError:
                logger.exception(e.response.content)
                raise Exception(e.response.content)
            message = f"Exception occurred: {e.response.reason} - {e.response.status_code} - {content_message}"
            logger.exception(message)
            raise Exception(message)
        except Exception as e:
            logger.exception(f"Exception occurred: {e}")
            raise

    return wrapper


def _get_content(response, load=True):
    if response.status_code == HTTPStatus.OK:
        if not load:
            return response.content
        try:
            content = json.loads(response.content)
        except Exception as e:
            return response.content.decode("utf-8")
        return content
    else:
        raise AriumException(response)


@exception_handler
def asset_get(client: 'APIClient', collection: str, asset_id: UUID) -> Optional[Dict]:
    logger.debug(f"getting {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"status: {response.status_code}, found {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_set_description(client: 'APIClient', collection: str, asset_id: UUID, description: str) -> Optional[str]:
    logger.debug(f"setting description {collection}/{asset_id}... to {description}")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/description", data=description)
    logger.info(f"asset: {response.status_code}, found {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_rename(client: 'APIClient', collection: str, asset_id: UUID, name: str) -> Optional[Dict]:
    logger.debug(f"moving {collection}/{asset_id} to {name}...")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/move?assetName={name}")
    logger.info(f"status: {response.status_code}, renamed {collection}/{asset_id}")
    return _get_content(response).pop()


@exception_handler
def asset_list(client: 'APIClient', collection: str, latest: bool = True) -> Optional[List]:
    logger.debug("collecting {}...".format(collection))
    latest_param = str(latest).lower()
    response = client.get_request(f"/{{tenant}}/{collection}/assets?latest={latest_param}")
    payload = _get_content(response)
    logger.info(f"status: {response.status_code}, Found {payload['count']} of {payload['total']} {collection}")
    return payload["content"]


@exception_handler
def asset_versions(client: 'APIClient', collection: str, asset_id: UUID) -> Optional[List]:
    logger.debug(f"versions {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/versions")
    payload = _get_content(response)
    logger.info(f"status: {response.status_code}, versions {len(payload)} {collection}{asset_id}")
    return payload


@exception_handler
def asset_get_description(client: 'APIClient', collection: str, asset_id: UUID) -> Optional[str]:
    logger.info(f"getting description {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"description: {response.status_code}, found {collection}/{asset_id}")
    return _get_content(response)["description"]


@exception_handler
def asset_get_payload_description(client: 'APIClient', collection: str, asset_id: UUID) -> Optional[str]:
    logger.info(f"getting description {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description")
    logger.info(f"status: {response.status_code}, received description {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_update_payload_description(client: 'APIClient', collection: str, asset_id: UUID,
                                     description: str) -> Optional[str]:
    logger.info(f"updating description {collection}/{asset_id} to {description}...")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description", data=description)
    logger.info(f"status: {response.status_code}, updated description {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_delete(client: 'APIClient', collection: str, asset_id: UUID) -> Optional[Dict]:
    logger.debug(f"removing {collection}/{asset_id} ...")
    response = client.delete_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"status: {response.status_code}, removed {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_copy(client: 'APIClient', collection: str, asset_id: UUID, name: str) -> Optional[Dict]:
    logger.debug(f"copying {collection}/{asset_id} to {name}...")
    response = client.post_request(f"/{{tenant}}/{collection}/assets/{asset_id}/copy?assetName={name}")
    logger.info(f"status: {response.status_code}, copied {collection}/{asset_id} to {name}")
    return _get_content(response)


@exception_handler
def asset_lock(client: 'APIClient', collection: str, asset_id: UUID, locked: bool) -> Optional[Dict]:
    logger.debug(f"locking {collection}/{asset_id} to {locked}...")
    url_locked = "lock" if locked else "unlock"
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/{url_locked}")
    logger.info(f"status: {response.status_code}, locked {collection}/{asset_id}")
    return _get_content(response)


@exception_handler
def asset_is_empty(client: 'APIClient', collection: str) -> Optional[Dict]:
    logger.debug(f"checking if {collection} is empty...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/empty")
    logger.info(f"status: {response.status_code}, {collection}/empty")
    return _get_content(response)


@exception_handler
def asset_copy_workspace(client: 'APIClient', collection: str, from_tenant: str, to_tenant: str,
                         asset_ids: List[str] = None, wait: bool = True) -> Optional[Dict]:
    request = {
        "from_tenant": from_tenant,
        "to_tenant": to_tenant,
        **({"assets": asset_ids} if asset_ids else {})
    }
    logger.debug(f"Copying {collection} {request}...")
    response = client.post_request(f"/{{tenant}}/{collection}/assets/copy", json=request)
    logger.info(f"status: {response.status_code}, found {collection}/empty")
    if wait:
        return copy_workspace_pooling(client, collection, _get_content(response)['id'])
    else:
        return _get_content(response)


@exception_handler
def asset_get_data(client: 'APIClient', collection: str, asset_id: UUID, presigned: bool = False) -> Optional[bytes]:
    logger.debug(f"getting data payload {collection}/{asset_id}...")
    url_mode = 'presigned' if presigned else 'auto'
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload?assetPayloadMode={url_mode}")
    location_header = response.headers.get("Location", None)

    if location_header is None:
        content = _get_content(response, False)
        logger.info(f"status: {response.status_code}, received DIRECT data payload  {collection}/{asset_id} "
                    f"of length: {len(content)}, headers: {response.headers}")
        return content
    else:
        response = urllib3.PoolManager().request("GET", location_header)
        content = response.data
        logger.info(f"status: {response.status}, received PRESIGNED data payload  {collection}/{asset_id} "
                    f"of length: {len(content)}, headers: {response.headers}")
        return content


@exception_handler
def asset_post(client: 'APIClient', collection, name, data: Union[str, Dict], params: Dict = None,
               presigned: bool = False, wait=True) -> Optional[Dict]:
    logger.debug(f"creating {collection}/{name}...")

    url_params = f"assetName={name}"
    url_params = url_params + f"&assetPayloadMode=presigned" if presigned else url_params

    if params is not None:
        for key, value in params.items():
            url_params = url_params + f"&{key}={value}"

    logger.debug(f"url_params {url_params}")
    response = client.post_request(f"/{{tenant}}/{collection}/assets?{url_params}",
                                   json=data if not presigned else None)
    location_header = response.headers.get("Location", None)

    content = _get_content(response)
    if location_header is None:
        dump = json.dumps(content, sort_keys=True, indent=4)
        logger.info(f"created: {response.status_code}, {collection}/{name}: {dump} .")
        return content
    else:
        logger.debug(f"euploading: {response.status_code}, {collection}/{name}, location_header: {location_header} ")
        urllib3.PoolManager().request("PUT", location_header, body=data.encode('utf-8').strip())
        if wait:
            asset_pooling(client, collection, content["id"])
        return asset_get(client, collection, content["id"])


def asset_pooling(client, collection, asset_id):
    logger.debug("Pooling {} {}...".format(collection, asset_id))

    status = asset_get(client, collection, asset_id)["status"]
    while status in ("uploading", "processing"):
        status = asset_get(client, collection, asset_id)["status"]
        sleep(1.0)
        logger.debug("Pooling {} {}...".format(collection, asset_id))
    logger.info("Upload finished.")


def calc_pooling(client, endpoint: str, response_collector: Callable[[Response], Dict]):
    logger.debug("Pooling...")
    response = client.get_request(endpoint)

    while response.status_code == 202:
        sleep(1.0)
        logger.debug("Pooling...")
        response = client.get_request(endpoint)

    logger.debug("Got response.")
    return response_collector(response)


def copy_workspace_pooling(client, collection, copy_id):
    logger.debug("Pooling copy {} {}...".format(collection, copy_id))

    response = _get_content(client.get_request(f"/{{tenant}}/{collection}/assets/copy/{copy_id}"))
    while response['state'] == "processing":
        response = _get_content(client.get_request(f"/{{tenant}}/{collection}/assets/copy/{copy_id}"))
        sleep(1.0)
        logger.debug("Pooling {} {}...".format(collection, copy_id))
    logger.info("Copying finished.")
    return response
