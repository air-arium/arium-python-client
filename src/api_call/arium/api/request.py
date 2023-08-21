import codecs
import csv
import json
import os
from http import HTTPStatus
from time import sleep
from typing import List, Optional, Dict, Union, Generator, Any
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import requests

from api_call.arium.api.exceptions import AriumAPACResponseException, exception_handler
from config.get_logger import get_logger

if TYPE_CHECKING:
    from api_call.client import APIClient

logger = get_logger(__name__)


@exception_handler
def get_content(
    response, accept=None, load=True, get_from_location=True, verify=True
) -> Union[bytes, str, Dict]:
    if accept is None:
        accept = [HTTPStatus.OK, HTTPStatus.NO_CONTENT]

    if response.status_code in accept:
        if get_from_location:
            location_header = response.headers.get("Location", None)
            if location_header:
                response = requests.get(url=location_header, verify=verify)
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
        raise AriumAPACResponseException(response)


def get_content_from_url(
    url: str, csv_output: bool = False, raw: bool = False, delimiter: str = ","
) -> Generator[Any, None, None]:
    if csv_output:
        with requests.get(url, verify=False) as resp:
            if raw:
                yield resp
            else:
                reader = csv.reader(
                    codecs.iterdecode(resp.content.splitlines(), "utf-8"),
                    delimiter=delimiter,
                )
                for row in reader:
                    yield row
    else:
        with requests.get(url) as resp:
            yield resp if raw else get_content(resp)


def get_resources(
    client: "APIClient",
    calculations_id: str,
    endpoint: str,
    csv_output: bool = True,
    delimiter: str = ",",
):
    endpoint = f"/{{tenant}}/{endpoint.format(calculations_id=calculations_id)}"
    response = client.get_request(endpoint=endpoint)
    urls = get_content(response=response)
    for resource_url in urls:
        yield get_content_from_url(
            url=resource_url,
            csv_output=csv_output,
            delimiter=delimiter,
        )


def get_request_data(
    request: Union[str, Dict], request_args=None
) -> Union[Dict, bytes]:
    if type(request) not in (dict, list):
        with open(request) as f:
            request = json.load(f)

    if request_args is not None:
        request.update(request_args)

    return request


@exception_handler
def asset_get(
    client: "APIClient", collection: str, asset_id: str, status: bool = True
) -> Optional[Dict]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    if status:
        logger.info(f"Got {collection}/{asset_id}.")
    return content


@exception_handler
def asset_set_description(
    client: "APIClient", collection: str, asset_id: str, description: str
) -> Optional[str]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/description"
    response = client.put_request(endpoint=endpoint, data=description)
    content = get_content(response=response)

    logger.info(f"Updated {collection}/{asset_id}.")
    return content


@exception_handler
def asset_rename(
    client: "APIClient", collection: str, asset_id: str, asset_name: str
) -> Optional[Dict]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/move?assetName={asset_name}"
    response = client.put_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Renamed {collection}/{asset_id}.")
    return list(content).pop()


@exception_handler
def asset_list(
    client: "APIClient", collection: str, latest: bool = True
) -> Optional[List]:
    endpoint = f"/{{tenant}}/{collection}/assets?latest={str(latest).lower()}"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    if isinstance(content, dict):
        logger.info(f"Found {content['count']} of {content['total']} {collection}.")
        return content["content"]
    else:
        raise Exception("Unexpected content type: {}.".format(type(content)))


@exception_handler
def asset_versions(
    client: "APIClient", collection: str, asset_id: str
) -> Optional[List]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/versions"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    if isinstance(content, list):
        logger.info(f"Versions count of {collection}{asset_id}: {len(content)}.")
        return content
    else:
        raise Exception("Unexpected content type: {}.".format(type(content)))


@exception_handler
def asset_get_description(
    client: "APIClient", collection: str, asset_id: str
) -> Optional[str]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Received description of {collection}/{asset_id}.")
    return content["description"]


@exception_handler
def asset_get_payload_description(
    client: "APIClient", collection: str, asset_id: str
) -> Optional[str]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Received payload description of {collection}/{asset_id}.")
    return content


@exception_handler
def asset_update_payload_description(
    client: "APIClient", collection: str, asset_id: str, payload_description: str
) -> Optional[str]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/payload/description"
    response = client.put_request(endpoint=endpoint, data=payload_description)
    content = get_content(response)
    logger.info(f"Updated payload description {collection}/{asset_id}.")
    return content


@exception_handler
def asset_delete(client: "APIClient", collection: str, asset_id: str) -> Optional[Dict]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}"
    response = client.delete_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Removed {collection}/{asset_id}.")
    return content


@exception_handler
def asset_copy(
    client: "APIClient", collection: str, asset_id: str, asset_name: str
) -> Optional[Dict]:
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/copy?assetName={asset_name}"
    response = client.post_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Copied {collection}/{asset_id} to {asset_name}.")
    return content


@exception_handler
def asset_lock(
    client: "APIClient", collection: str, asset_id: str, locked: bool
) -> Optional[Dict]:
    url_locked = "lock" if locked else "unlock"
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/{url_locked}"
    response = client.put_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Locked {collection}/{asset_id}.")
    return content


@exception_handler
def asset_is_empty(client: "APIClient", collection: str) -> Optional[bool]:
    endpoint = f"/{{tenant}}/{collection}/assets/empty"
    response = client.get_request(endpoint=endpoint)
    content = get_content(response=response)

    logger.info(f"Collection is empty: {content['empty']}")
    return content["empty"]


@exception_handler
def asset_copy_workspace(
    client: "APIClient",
    collection: str,
    from_tenant: str,
    to_tenant: str,
    asset_ids: List[str] = None,
    wait: bool = True,
) -> Optional[Dict]:
    request = {
        "from_tenant": from_tenant,
        "to_tenant": to_tenant,
        **({"assets": asset_ids} if asset_ids else {}),
    }
    endpoint = f"/{{tenant}}/{collection}/assets/copy"
    response = client.post_request(endpoint=endpoint, json=request)
    content = get_content(response=response)

    if wait:
        return copy_workspace_polling(
            client=client,
            collection=collection,
            copy_id=content["id"],
        )
    else:
        return content


@exception_handler
def asset_export(
    client: "APIClient",
    collection: str,
    asset_ids: List[str],
    export_name: str = None,
    output_folder: str = "",
) -> Optional[str]:
    export_name = export_name if export_name is not None else "export_" + collection
    endpoint = f"/{{tenant}}/{collection}/assets/export"
    response = client.post_request(endpoint=endpoint, json=asset_ids)
    data = get_content(response=response, load=False)

    with open(os.path.join(output_folder, export_name), "wb") as file:
        file.write(data)

    logger.info(f"Exported to {output_folder}, file {export_name}.")
    return export_name


@exception_handler
def asset_import(
    client: "APIClient", collection: str, path: str, wait: bool = True
) -> Optional[str]:
    endpoint = f"/{{tenant}}/{collection}/assets/import"
    response = client.post_request(endpoint=endpoint)
    location_header = response.headers.get("Location", None)

    content = get_content(response=response, get_from_location=False)

    with open(path) as file:
        requests.put(url=location_header, data=file.read().encode("utf-8").strip())

    logger.info("Import request started.")

    if wait:
        return import_polling(
            client=client, collection=collection, copy_id=content["id"]
        )["ids"]
    return content


@exception_handler
def asset_get_data(
    client: "APIClient",
    collection: str,
    asset_id: str,
    get_from_location: bool = False,
) -> Optional[bytes]:
    url_mode = "presigned" if get_from_location else "auto"
    endpoint = f"/{{tenant}}/{collection}/assets/{asset_id}/payload?assetPayloadMode={url_mode}"
    response = client.get_request(endpoint=endpoint)

    get_from_location = "Location" in response.headers
    content = get_content(
        response=response,
        load=False,
        get_from_location=get_from_location,
        verify=client.verify,
    )

    if not get_from_location:
        logger.info(f"Received DIRECT data payload  {collection}/{asset_id}.")
    else:
        logger.info(f"Received PRESIGNED data payload  {collection}/{asset_id}.")

    return content


@exception_handler
def asset_post(
    client: "APIClient",
    collection,
    asset_name,
    data: Union[str, Dict],
    params: Dict = None,
    presigned: bool = False,
    wait=True,
    verify=True,
) -> Optional[Dict]:
    url_params = {
        "assetName": asset_name,
        **({"assetPayloadMode": presigned} if presigned else {}),
    }
    if params is not None:
        url_params.update(params)
    url_params = urlencode(url_params)

    endpoint = f"/{{tenant}}/{collection}/assets?{url_params}"
    json_data = data if not presigned else None
    response = client.post_request(endpoint=endpoint, json=json_data)

    location_header = response.headers.get("Location", None)
    content = get_content(response, get_from_location=False)

    if location_header is None:
        logger.info(f"Created {content['id']} ({collection}).")
        return content
    else:
        logger.info(f"Uploading {collection}/{asset_name}.")
        data = data.encode("utf-8").strip()
        requests.put(url=location_header, data=data, verify=verify)

        if wait:
            asset_polling(client=client, collection=collection, asset_id=content["id"])
        return asset_get(
            client=client,
            collection=collection,
            asset_id=content["id"],
            status=False,
        )


def asset_polling(client: "APIClient", collection: str, asset_id: str):
    asset = asset_get(
        client=client,
        collection=collection,
        asset_id=asset_id,
        status=False,
    )

    while asset["status"] in ("uploading", "processing"):
        asset = asset_get(
            client=client,
            collection=collection,
            asset_id=asset_id,
            status=False,
        )
        sleep(1.0)
        logger.debug(f"Polling {collection} {asset_id}...")

    logger.info("Upload finished.")
    return asset["status"]


def calc_polling(client: "APIClient", endpoint: str, url=None):
    logger.info(f"Processing {endpoint}...")
    response = client.get_request(endpoint=endpoint, url=url)

    while response.status_code == HTTPStatus.ACCEPTED:
        sleep(1.0)
        logger.debug(f"Polling... {endpoint}")
        response = client.get_request(endpoint=endpoint, url=url)

    logger.info(f"Got response {response.status_code}.")
    return response


def _assets_db_polling(client: "APIClient", db: str, collection: str, copy_id: str):
    logger.info(f"Polling copy {collection} {copy_id}...")

    accept = [HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.PROCESSING]
    response = client.get_request(
        endpoint=f"/{{tenant}}/{collection}/assets/{db}/{copy_id}"
    )
    content = get_content(response=response, accept=accept)

    while content["state"] in ("uploading", "processing"):
        response = client.get_request(
            endpoint=f"/{{tenant}}/{collection}/assets/{db}/{copy_id}"
        )
        content = get_content(response=response, accept=accept)
        sleep(1.0)
        logger.debug("Polling...")

    logger.info("Finished.")
    return content


def copy_workspace_polling(client: "APIClient", collection: str, copy_id: str):
    return _assets_db_polling(
        client=client, db="copy", collection=collection, copy_id=copy_id
    )


def import_polling(client: "APIClient", collection: str, copy_id: str):
    return _assets_db_polling(
        client=client, db="import", collection=collection, copy_id=copy_id
    )
