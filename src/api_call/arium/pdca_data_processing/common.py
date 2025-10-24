import os
from typing import Dict, List, Any

import pandas as pd
import base64
import json
from io import StringIO
from api_call.arium.api.exceptions import ExceptionHandlerDecorator
from api_call.arium.pdca_data_processing.constants import ERROR_FILEPATH
from config.get_logger import get_logger

logger = get_logger(__name__)


@ExceptionHandlerDecorator("Cannot validate secret code.")
def validate_secret() -> bool:
    """
    Checks validity of a secret code required to decode files.
    """
    with open("data/secret.json") as secret_json:
        secret_data = json.load(secret_json)

    coded_secret = base64.b64encode(secret_data["purpose"][::-1].encode()).decode()
    return secret_data["secret_code"] == coded_secret


def get_dataframe_from_encoded(filename: str) -> pd.DataFrame:
    if not validate_secret():
        print("Missing or invalid secret file.")
        return
    try:
        # Read the content of the CSV file
        with open(filename, "r") as f:
            content = f.read()

        return decode_base64_object(content)

    except FileNotFoundError as e:
        raise e


def decode_base64_object(encoded_object: str) -> pd.DataFrame:
    e_object = base64.b64decode(encoded_object.encode()).decode()
    csv_data = StringIO(e_object)
    return pd.read_csv(csv_data)


@ExceptionHandlerDecorator("Cannot load file={filepath}.")
def load(filepath: str):
    logger.debug(f"Load file {filepath} as DataFrame.")
    if "txt" in filepath:
        return get_dataframe_from_encoded(filepath)
    return pd.read_csv(filepath, encoding="utf8")


@ExceptionHandlerDecorator("Remove records failed.")
def remove_records(
    data: pd.DataFrame, records: Dict, filepath: str, module: str, mode="w"
):
    """
    Removes records and saves removed data to file.
    :param data: data from which records should be removed
    :param records: dicts of bool masks, where key is a error code and value is a mask
    :param filepath: output filepath
    :param module: module name
    :param mode: file mode ('w' - write, 'a' - append)
    :return:
    """
    logger.debug("Remove records.")

    removed = []
    remove_indexes = None
    for reason, indexes in records.items():
        removed.append(data[indexes].assign(Comment=reason, Module=module))
        remove_indexes = indexes if remove_indexes is None else remove_indexes | indexes
    data.drop(data.index[remove_indexes], inplace=True)

    if any([len(r) for r in removed]):
        removed = pd.concat(removed)
        write_csv(removed, filepath, mode=mode)
        return removed


@ExceptionHandlerDecorator("Failed to write csv {filepath}.")
def write_csv(data: pd.DataFrame, filepath: str, mode="w", columns: List = None):
    if columns is None:
        columns = data.columns
    with open(filepath, mode, newline="", encoding="utf-8") as f:
        f.write(data.to_csv(index=False, encoding="utf-8", mode="a", columns=columns))
        logger.info(f"Created output file: {filepath}")


@ExceptionHandlerDecorator(
    "Cannot create output folders in localization: {output_folder}, sub-folders: {sub_folders}."
)
def create_output_folders(output_folder: str, sub_folders=None):
    """
    Creates output folder with sub-folders.
    """
    if sub_folders is None:
        sub_folders = [""]

    for _folder in sub_folders:
        folder = output_folder + _folder
        if not os.path.exists(folder):
            os.makedirs(folder)


def get_error_message(data: pd.DataFrame, column: str, items: Any, message: str):
    error = {
        "Message": message,
        "AccountName": data.loc[items, "AccountName"].tolist(),
        "CompanyId": data.loc[items, "__company_id"].tolist(),
        "Value": data.loc[items, column].tolist(),
    }
    logger.error(error)
    return error


def camel_case(s):
    if s.startswith("__"):
        return s
    return "".join(x[0].upper() + x[1:] for x in s.split("_") if x.isalnum())


def save_errors(errors: List, output_folder: str):
    logger.info("Save errors.")

    df_data = []
    for error in errors:
        index = 0
        for account_name in error["AccountName"]:
            error_obj = {"Message": error["Message"], "AccountName": account_name}
            if index < len(error["CompanyId"]):
                error_obj["CompanyId"] = str(error["CompanyId"][index])[:-2]
            else:
                error_obj["CompanyId"] = ""

            if index < len(error["Value"]):
                error_obj["Value"] = error["Value"][index]
            else:
                error_obj["Value"] = ""
            df_data.append(error_obj)
            index += 1

    df_error_list = pd.DataFrame(
        df_data, columns=["Message", "AccountName", "CompanyId", "Value"]
    )

    write_csv(df_error_list, output_folder + ERROR_FILEPATH)
