import json
import sys

sys.path.append("../../src")

from api_call.arium.pdca_data_processing.common import create_output_folders
from api_call.arium.pdca_data_processing.constants import OUTPUT_FOLDER, PROPERTIES
from api_call.arium.pdca_data_processing.map import map_data, modify_api_input
from api_call.arium.pdca_data_processing.match import match_data
from api_call.arium.pdca_data_processing.merge import merge_data
from api_call.arium.pdca_data_processing.batch_records_updater import (
    update_batch_record_ids,
)
from api_call.client import APIClient
from auth.okta_auth import Auth

import urllib3

urllib3.disable_warnings()

# CONFIGURATION MATCH
match_schema = 1
augment_schema = 1
simultaneous_batches = 10
selected_fields = (
    PROPERTIES  # Select all possible properties (it is possible to define subset here)
)

batch_size = 4
# REQUIRED ACTION: Set test_name
test_name = ""

# BASE CONFIGURATION
ref_data_folder = "data/refdata/"
calc_id = (
    test_name + "-" + str(batch_size)
)  # Used to create output folder
output_folder = OUTPUT_FOLDER.format(calc_id=calc_id)

# CONFIGURATION MAP
# REQUIRED ACTION: Set paths
filepath = "data/" + test_name + ".csv"
filepath_template = ""
config_replace = {
    # "TriggerType": "path",
    # "CoverageType": "path",
    # "Country": "path",
    # "State": "path",
}
date_format = "%d/%m/%Y"

# CONFIGURATION MERGE
confidence = 3
all_naics = True

# CONFIGURATION AUTHORIZATION
# REQUIRED ACTION: Set tenant, role, prefix and settings
tenant = ""
role = ""
prefix = ""
auth_settings = {}
authorization_code = False
verify = False

create_output_folders(output_folder=output_folder)
with open(output_folder + "config.json", "w") as f:
    json.dump(locals(), f, default=repr)

# AUTHORIZATION
auth = Auth(
    tenant=tenant,
    role=role,
    settings=auth_settings,
    authorization_code=authorization_code,
    prefix=prefix,
    verify=verify,
)
client = APIClient(auth=auth)

# MAP
map_data(
    filepath=filepath,
    filepath_template=filepath_template,
    config_replace=config_replace,
    output_folder=output_folder,
    ref_data_folder=ref_data_folder,
    date_format=date_format,
)

modify_api_input(output_folder=output_folder, selected_fields=selected_fields)

# MATCH
match_data(
    client=client,
    match_schema=match_schema,
    augment_schema=augment_schema,
    batch_size=batch_size,
    simultaneous_batches=simultaneous_batches,
    output_folder=output_folder,
)

update_batch_record_ids(
    data_folder=output_folder, match_schema=match_schema, batch_size=batch_size
)

# MERGE
merge_data(
    confidence=confidence,
    output_folder=output_folder,
    match_schema=match_schema,
    augment_schema=augment_schema,
    ref_data_folder=ref_data_folder,
    all_naics=all_naics,
)
