import json
import os

from config.get_logger import get_logger
from api_call.arium.api.exceptions import ExceptionHandlerDecorator

logger = get_logger(__name__)


@ExceptionHandlerDecorator(
    "Cannot update record_id in master data from {folder} with schema {match_schema}"
)
def update_batch_record_ids(data_folder: str, match_schema: str, batch_size: int):
    match_main_folder = f"{data_folder}match/match_{match_schema}/"
    match_raw_folder = f"{match_main_folder}raw"

    logger.info(
        f"Updating record id in match results. Source folder: {match_raw_folder}. Destination: {match_main_folder}"
    )

    for file in list_files_in_folder(match_raw_folder):
        path = os.path.join(match_raw_folder, file)

        # e.g. we want to get 10 as it is the batch index
        # match_1-10.json -> match_1-10 -> ['match_1', '10'] -> '10' -> 10
        batch_index = int(file[:-5].split("-")[1])

        logger.debug(f"*****  Updating record_id in batch {batch_index}")

        data = load_json_from_file(path)

        update_data(batch_index, batch_size, data)

        output_path = os.path.join(match_main_folder, file)
        save_json_to_file(data, output_path)


def update_data(batch_index, batch_size, data):
    if batch_index > 0:
        batch_offset = batch_index * batch_size
        for row in data["masterData"]:
            row["record_id"] += batch_offset


def load_json_from_file(path):
    with open(path) as f:
        data = json.load(f)
    return data


def save_json_to_file(data, output_path):
    logger.debug(f"*****  Saving results in {output_path}")
    with open(output_path, "w") as f:
        f.write(json.dumps(data, indent=2))


def list_files_in_folder(match_raw_folder):
    return os.listdir(match_raw_folder)
