import codecs
import csv
import json
import logging.config
import os
from http import HTTPStatus
from time import sleep
from typing import List, Optional, Dict, Union, Generator, Any
from typing import TYPE_CHECKING

import requests
from requests import Response

from config.constants import LOGGING_CONFIG

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
                content = json.loads(e.response.content)
                content_message = content.get('message', content.get('error', content.get('errors', content)))
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


@exception_handler
def get_content(client: 'APIClient', response, accept=None, load=True,
                get_from_location=True) -> Union[bytes, str, Dict]:
    client.logger.debug("Getting content... Status code: {}, Content type: {}"
                        .format(response.status_code, response.headers['Content-Type']))
    if accept is None:
        accept = [HTTPStatus.OK]

    if response.status_code in accept:
        if get_from_location:
            location_header = response.headers.get("Location", None)
            if location_header:
                response = requests.get(url=location_header)
        content = response.content
        if not load:
            return content
        try:
            content = json.loads(response.content)
        except Exception as e:
            logger.debug(e)
            return response.content.decode("utf-8")
        return content
    else:
        raise AriumException(response)


def upload(client: 'APIClient', url: str, data: Dict, request_file: str = None, request: Dict = None) -> Response:
    response = get_content(client, client.put_request(url, json=data), get_from_location=False)
    upload_url = response['url']
    status_location = '/' + response['location']
    request = get_request_data(request_file, request)

    upload_response = requests.put(url=upload_url,
                                   data=request,
                                   headers={'Content-Type': ''})

    logger.debug("Upload response code: {}".format(upload_response.status_code))
    return calc_polling(client, status_location)


def get_request_data(request_file: str = None, request: Dict = None, read_json=False) -> Union[Dict, bytes]:
    if request is not None:
        if read_json:
            return request
        request = json.dumps(request)
    elif request_file is not None:
        if read_json:
            with open(request_file) as f:
                request = json.load(f)
        else:
            with open(request_file, 'rb') as f:
                request = f.read()
    else:
        raise Exception("'request_file' or 'request' argument is required!")
    return request


def get_content_from_urls(client: 'APIClient', response: Response,
                          csv_output=False, raw=False) -> Generator[Any, None, None]:
    content = get_content(client, response)
    urls = content['urls'] if 'urls' in response else [content['url']]
    for url in urls:
        if csv_output:
            with requests.get(url) as resp:
                reader = csv.reader(codecs.iterdecode(resp.content.splitlines(), 'utf-8'))
                for row in reader:
                    yield row
        else:
            with requests.get(url) as resp:
                yield resp if raw else get_content(client, resp)

        if len(urls) > 1:
            yield []


def asynchronous_endpoint(client: 'APIClient', endpoint: str, request_file: str = None, request: Dict = None,
                          raw=False) -> Union[Response, Dict]:
    url = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
    response = upload(client, url, {}, request_file=request_file, request=request)
    return next(get_content_from_urls(client, response, raw=raw))


def asynchronous_endpoint_csv(client: 'APIClient', endpoint: str, request_file: str = None,
                              request: Dict = None) -> Generator[Any, None, None]:
    url = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
    response = upload(client, url, {}, request_file=request_file, request=request)
    yield from get_content_from_urls(client, response, True)


def synchronous_endpoint_put(client: 'APIClient', endpoint: str,
                             request_file: str = None, request: Dict = None, raw=False) -> Union[Response, Dict]:
    endpoint = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
    request = get_request_data(request_file, request, read_json=True)
    result = client.put_request(endpoint, json=request)
    return result if raw else json.loads(result.content)


def synchronous_endpoint_get(client: 'APIClient', endpoint: str, raw=False) -> Union[Response, Dict]:
    endpoint = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
    result = client.get_request(endpoint)
    return result if raw else json.loads(result.content)


@exception_handler
def asset_get(client: 'APIClient', collection: str, asset_id: str) -> Optional[Dict]:
    logger.debug(f"getting {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"status: {response.status_code}, found {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_set_description(client: 'APIClient', collection: str, asset_id: str, description: str) -> Optional[str]:
    logger.debug(f"setting description {collection}/{asset_id}... to {description}")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/description",
                                  data=description)
    logger.info(f"asset: {response.status_code}, found {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_rename(client: 'APIClient', collection: str, asset_id: str, asset_name: str) -> Optional[Dict]:
    logger.debug(f"moving {collection}/{asset_id} to {asset_name}...")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/move?assetName={asset_name}")
    logger.info(f"status: {response.status_code}, renamed {collection}/{asset_id}")
    return list(get_content(client, response)).pop()


@exception_handler
def asset_list(client: 'APIClient', collection: str, latest: bool = True) -> Optional[List]:
    logger.debug("collecting {}...".format(collection))
    latest_param = str(latest).lower()
    response = client.get_request(f"/{{tenant}}/{collection}/assets?latest={latest_param}")
    payload = get_content(client, response)
    if isinstance(payload, dict):
        logger.info(f"status: {response.status_code}, Found {payload['count']} of {payload['total']} {collection}")
        return payload['content']
    else:
        raise Exception('Unexpected content type: {}.'.format(type(payload)))


@exception_handler
def asset_versions(client: 'APIClient', collection: str, asset_id: str) -> Optional[List]:
    logger.debug(f"versions {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/versions")
    payload = get_content(client, response)
    if isinstance(payload, list):
        logger.info(f"status: {response.status_code}, versions {len(payload)} {collection}{asset_id}")
        return payload
    else:
        raise Exception('Unexpected content type: {}.'.format(type(payload)))


@exception_handler
def asset_get_description(client: 'APIClient', collection: str, asset_id: str) -> Optional[str]:
    logger.info(f"getting description {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"description: {response.status_code}, found {collection}/{asset_id}")
    return get_content(client, response)["description"]


@exception_handler
def asset_get_payload_description(client: 'APIClient', collection: str, asset_id: str) -> Optional[str]:
    logger.info(f"getting payload description {collection}/{asset_id}...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description")
    logger.info(f"status: {response.status_code}, received payload description {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_update_payload_description(client: 'APIClient', collection: str, asset_id: str,
                                     payload_description: str) -> Optional[str]:
    logger.info(f"updating payload description {collection}/{asset_id} to {payload_description}...")
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description",
                                  data=payload_description)
    logger.info(f"status: {response.status_code}, updated payload description {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_delete(client: 'APIClient', collection: str, asset_id: str) -> Optional[Dict]:
    logger.debug(f"removing {collection}/{asset_id} ...")
    response = client.delete_request(f"/{{tenant}}/{collection}/assets/{asset_id}")
    logger.info(f"status: {response.status_code}, removed {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_copy(client: 'APIClient', collection: str, asset_id: str, asset_name: str) -> Optional[Dict]:
    logger.debug(f"copying {collection}/{asset_id} to {asset_name}...")
    response = client.post_request(f"/{{tenant}}/{collection}/assets/{asset_id}/copy?assetName={asset_name}")
    logger.info(f"status: {response.status_code}, copied {collection}/{asset_id} to {asset_name}")
    return get_content(client, response)


@exception_handler
def asset_lock(client: 'APIClient', collection: str, asset_id: str, locked: bool) -> Optional[Dict]:
    logger.debug(f"locking {collection}/{asset_id} to {locked}...")
    url_locked = "lock" if locked else "unlock"
    response = client.put_request(f"/{{tenant}}/{collection}/assets/{asset_id}/{url_locked}")
    logger.info(f"status: {response.status_code}, locked {collection}/{asset_id}")
    return get_content(client, response)


@exception_handler
def asset_is_empty(client: 'APIClient', collection: str) -> Optional[bool]:
    logger.debug(f"checking if {collection} is empty...")
    response = client.get_request(f"/{{tenant}}/{collection}/assets/empty")
    logger.info(f"status: {response.status_code}, {collection}/empty")
    return get_content(client, response)["empty"]


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
    logger.info(f"status: {response.status_code}")
    if wait:
        return copy_workspace_polling(client, collection, get_content(client, response)['id'])
    else:
        return get_content(client, response)


@exception_handler
def asset_export(client: 'APIClient', collection: str, asset_ids: List[str],
                 export_name: str = None, output_folder: str = "") -> Optional[str]:
    logger.debug(f"Export {collection} {asset_ids}...")
    response = client.post_request(f"/{{tenant}}/{collection}/assets/export", json=asset_ids)
    logger.info(f"status: {response.status_code}")
    data = get_content(client, response, load=False)
    export_name = export_name if export_name is not None else "export_" + collection
    with open(os.path.join(output_folder, export_name), "wb") as file:
        file.write(data)
    return export_name


@exception_handler
def asset_import(client: 'APIClient', collection: str, path: str, wait: bool = True) -> Optional[str]:
    logger.debug(f"Import {collection} {path}...")
    response = client.post_request(f"/{{tenant}}/{collection}/assets/import")
    logger.info(f"status: {response.status_code}")
    location_header = response.headers.get("Location", None)
    logger.debug(f"importing: {response.status_code}, {collection}, location_header: {location_header} ")
    content = get_content(client, response, get_from_location=False)
    with open(path) as file:
        requests.put(url=location_header,
                     data=file.read().encode('utf-8').strip())
    if wait:
        return import_polling(client, collection, content["id"])['ids']
    return content


@exception_handler
def asset_get_data(client: 'APIClient', collection: str, asset_id: str, presigned: bool = False) -> Optional[bytes]:
    logger.debug(f"getting data payload {collection}/{asset_id}...")
    url_mode = 'presigned' if presigned else 'auto'
    response = client.get_request(f"/{{tenant}}/{collection}/assets/{asset_id}/payload?assetPayloadMode={url_mode}")

    if "Location" in response.headers:
        content = get_content(client, response, load=False)
        logger.info(f"status: {response.status_code}, received DIRECT data payload  {collection}/{asset_id} "
                    f"of length: {len(content)}, headers: {response.headers}")
        return content
    else:
        content = get_content(client, response, load=False)
        logger.info(f"status: {response.status_code}, received PRESIGNED data payload  {collection}/{asset_id} "
                    f"of length: {len(content)}, headers: {response.headers}")
        return content


@exception_handler
def asset_post(client: 'APIClient', collection, asset_name, data: Union[str, Dict], params: Dict = None,
               presigned: bool = False, wait=True) -> Optional[Dict]:
    logger.debug(f"creating {collection}/{asset_name}...")

    url_params = f"assetName={asset_name}"
    url_params = url_params + f"&assetPayloadMode=presigned" if presigned else url_params

    if params is not None:
        for key, value in params.items():
            url_params = url_params + f"&{key}={value}"

    logger.debug(f"url_params {url_params}")
    response = client.post_request(f"/{{tenant}}/{collection}/assets?{url_params}",
                                   json=data if not presigned else None)
    location_header = response.headers.get("Location", None)

    content = get_content(client, response, get_from_location=False)
    if location_header is None:
        dump = json.dumps(content, sort_keys=True, indent=4)
        logger.info(f"created: {response.status_code}, {collection}/{asset_name}: {dump} .")
        return content
    else:
        logger.debug(
            f"uploading: {response.status_code}, {collection}/{asset_name}, location_header: {location_header} ")
        requests.put(url=location_header,
                     data=data.encode('utf-8').strip())
        if wait:
            asset_polling(client, collection, content["id"])
        return asset_get(client, collection, content["id"])


def asset_polling(client, collection, asset_id):
    logger.debug("Polling {} {}...".format(collection, asset_id))

    status = asset_get(client, collection, asset_id)["status"]
    while status in ("uploading", "processing"):
        status = asset_get(client, collection, asset_id)["status"]
        sleep(1.0)
        logger.debug("Polling {} {}...".format(collection, asset_id))
    logger.info("Upload finished.")


def calc_polling(client, endpoint: str):
    logger.debug("Polling...")
    response = client.get_request(endpoint)

    while response.status_code == HTTPStatus.ACCEPTED:
        sleep(1.0)
        logger.debug("Polling...")
        response = client.get_request(endpoint)

    logger.debug("Got response.")
    return response


def _assets_db_polling(client: 'APIClient', db: str, collection: str, copy_id: str):
    logger.debug("Polling copy {} {}...".format(collection, copy_id))

    response = client.get_request(f"/{{tenant}}/{collection}/assets/{db}/{copy_id}")
    accept = [HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.PROCESSING]
    content = get_content(client, response, accept)
    while content['state'] in ("uploading", "processing"):
        response = client.get_request(f"/{{tenant}}/{collection}/assets/{db}/{copy_id}")
        content = get_content(client, response, accept)
        sleep(1.0)
        logger.debug("Polling {} {}...".format(collection, copy_id))
    logger.info("Finished.")
    return content


def copy_workspace_polling(client: 'APIClient', collection: str, copy_id: str):
    return _assets_db_polling(client, "copy", collection, copy_id)


def import_polling(client: 'APIClient', collection: str, copy_id: str):
    return _assets_db_polling(client, "import", collection, copy_id)
