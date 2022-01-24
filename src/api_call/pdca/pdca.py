import csv
import json

from api_call.client import APIClient


def replace_duns(item):
    if item == "dunsnumber":
        return "duns"
    return item


def get_data(input_file):
    with open(input_file) as f:
        reader = csv.reader(f)
        header = [replace_duns(" ".join(item.split())) for item in next(reader)]
        data = []
        for line in reader:
            data.append({header[i]: " ".join(item.split()) for i, item in enumerate(line)})
    return data


def get_pdca_result(response):
    return json.loads(response.content)


def pdca_async_helper(client: APIClient, input_data, request_input_token, endpoint, schema=1,
                      estimate_only=False, tags=None):
    request = {request_input_token: input_data}
    if tags is not None:
        request["tags"] = tags
    response = client.post_request(endpoint,
                                   json=request,
                                   params={'schema': schema, 'estimate_only': int(estimate_only)})

    if response.status_code != 201:
        raise Exception("ERROR: failed submitting to {}".format(endpoint))

    location = response.headers['location']
    return client.pooling(location, get_pdca_result)


def match_api_call(client: APIClient, input_data, schema=1, tags=None, estimate_only=False):
    return pdca_async_helper(client=client,
                             input_data=input_data,
                             request_input_token="matchInputs",
                             endpoint="/match",
                             schema=schema,
                             estimate_only=estimate_only,
                             tags=tags)


def augment_api_call(client: APIClient, input_data, schema=1, tags=None, estimate_only=False):
    return (pdca_async_helper(client=client,
                              input_data=input_data,
                              request_input_token="augmentInputs",
                              endpoint="/augment",
                              schema=schema,
                              estimate_only=estimate_only,
                              tags=tags))
