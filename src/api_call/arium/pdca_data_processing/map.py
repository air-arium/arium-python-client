import csv
import re
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from api_call.arium.api.exceptions import ExceptionHandlerDecorator
from api_call.arium.pdca_data_processing.common import (
    remove_records,
    get_error_message,
    write_csv,
    load,
    create_output_folders,
    save_errors,
)
from api_call.arium.pdca_data_processing.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)


class PortfolioField:
    __slots__ = "name", "customer_name", "required", "default"

    def __init__(self, template_row):
        self.name, self.customer_name, self.required, self.default = template_row
        self.required = bool(int(self.required))

    def __repr__(self):
        return f"{self.name}({self.customer_name})"


@ExceptionHandlerDecorator("Failed to remove chars '{chars}' from column '{column}'.")
def remove_chars_from_str(data: pd.DataFrame, column: str, chars: str = r"\)$"):
    """
    Remove chars from values in column.
    """
    logger.debug(f"Remove '{chars}' from {column}.")
    data[column] = data[column].astype(str).str.replace(chars, "")


@ExceptionHandlerDecorator("Strip data failed.")
def strip(master: pd.DataFrame):
    """
    Strip data - columns and values.
    """
    logger.debug("Strip data.")
    master.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    master.columns = master.columns.str.strip()


@ExceptionHandlerDecorator("Replacing values failed.")
def replace_values(master: pd.DataFrame, config_replace: Dict):
    """
    For each column in config_replace load data and replace all values for which mapping is defined
    (from InputValue to ValueToBeReplaced).
    """

    for column, filename in config_replace.items():
        logger.debug(f"Replace values in column {column}.")
        with open(filename) as f:
            rows = csv.reader(f)
            next(rows)  # Ignore header
            mapping = {_from: _to for (_from, _to) in rows}

        master.replace({column: mapping}, inplace=True)


@ExceptionHandlerDecorator("Cannot collect and remove invalid records.")
def collect_invalid_records_and_remove(master: pd.DataFrame, output_folder: str):
    """
    Remove items:
        - duplicated
        - with invalid CoverageType (DELETE)
    Save removed items to the file with the error message
    """
    duplicate_index = master.duplicated()
    no_lob_index = master["CoverageType"] == "DELETE"

    records_with_messages = {
        "Duplicate records": duplicate_index,
        "No LOB": no_lob_index,
    }

    remove_records(
        data=master,
        records=records_with_messages,
        filepath=output_folder + REJECTED_DATA_FILEPATH,
        module="Mapping",
    )


@ExceptionHandlerDecorator("Unable to validate.")
def validate(master: pd.DataFrame):
    """
    Checks if data exists.
    """
    if len(master) == 0:
        raise Exception("Validation error! No records in Customer Submission file.")


@ExceptionHandlerDecorator(
    "Failed to create record and company id for rank columns: {columns}."
)
def create_company_and_record_id(master: pd.DataFrame, columns: set):
    """
    Create record id - subsequent numbers from 1
    Create company id - rank using columns
    """
    logger.debug("Create __company_id and __record_id.")

    master["__record_id"] = np.arange(1, len(master) + 1)

    master["__company_id"] = ""

    for column in columns:
        master[column] = master[column].replace(r"^\s*$", np.nan, regex=True)
        master[column].fillna("NA", inplace=True)
        master["__company_id"] = (
            master["__company_id"]
            .str.cat(master[column].astype(str), sep=" ")
            .str.lower()
        )

    master["__company_id"] = (
        master["__company_id"].rank(method="min", numeric_only=False).astype(int)
    )


@ExceptionHandlerDecorator("Cannot create api input.")
def get_api_input(master: pd.DataFrame):
    """
    Adds company and record id columns.
    Creates api_input as subset of columns from master data.
    Clears the data.
    """
    logger.debug("Create api_input.")
    columns = get_columns(master)
    create_company_and_record_id(master, columns)
    api_input = master[list(columns)].copy()
    api_input.insert(0, "__company_id", master["__company_id"])
    api_input = api_input.drop_duplicates()

    for col in columns - {"AccountName"}:
        api_input[col] = api_input[col].replace(
            ["", "na", "n/a", "null", "none", "."], None
        )

    return api_input


@ExceptionHandlerDecorator("Unable to get columns.")
def get_columns(master: pd.DataFrame) -> set:
    """
    Returns the intersection of columns from master and predefined set.
    """
    cols_for_coding = {
        "AccountName",
        "StreetName",
        "StreetNumber",
        "City",
        "PostalCode",
        "County",
        "State",
        "Country",
        "LookupYear",
    }
    intersected = cols_for_coding & set(master.columns)
    return intersected


@ExceptionHandlerDecorator("Check for invalid values failed for column '{column}.'")
def check_invalid_values(
    data: pd.DataFrame,
    column: str,
    invalid: Union[str, List] = None,
    allowed: pd.DataFrame = None,
    drop: bool = False,
    accept: Union[None, List] = None,
):
    """
    Validates the values of given columns.
    Check either for invalid or compares values given with allowed values.
    """
    logger.debug(f"Check invalid values in {column}.")
    invalid_items = None

    if invalid is not None and allowed is not None:
        raise Exception(
            "Only one condition is supported. Please call the 'check_invalid_values' twice."
        )

    if invalid is not None:
        if isinstance(invalid, str):
            invalid_items = data[column] == invalid
        else:
            pattern = "|".join(invalid)
            invalid_items = data[column].str.contains(
                pattern, regex=True, flags=re.IGNORECASE
            )

    elif allowed is not None:
        allowed = list(allowed.str.lower()) + (
            [a.lower() for a in accept] if accept is not None else []
        )
        invalid_items = ~data[column].astype(str).str.lower().isin(allowed)

    if invalid_items.any():
        empty = invalid == "" or invalid == " "
        if empty:
            message = f"{column} should not be empty - please investigate/remove."
        else:
            invalid = set(data[invalid_items][column].tolist())
            message = f"{column} contains unexpected data '{invalid}' - please investigate/remove"

        if drop:
            data.drop(invalid_items.index, inplace=True)
        return get_error_message(data, column, invalid_items, message)


@ExceptionHandlerDecorator("Check for missing values in column '{column}' failed.")
def check_missing(data: pd.DataFrame, column: str):
    """
    Check for missing values.
    """
    logger.debug(f"Check missing values in column {column}.")
    missing_items = pd.isna(data[column])

    if missing_items.any():
        message = f"Validation error! Missing {column} information"
        data.drop(missing_items.index, inplace=True)
        return get_error_message(data, column, missing_items, message)


@ExceptionHandlerDecorator("Unable to create condition for column '{column}'.")
def condition(
    data: pd.DataFrame,
    column: str,
    lower: float,
    upper: float,
    lower_inclusive: bool = False,
    upper_inclusive: bool = False,
):
    """
    Creates the condition to check if value is between given range.
    """
    invalid = data[column] != data[column]
    s_l, s_u = None, None

    if lower is not None:
        if not lower_inclusive:
            invalid = invalid | data[column].astype(float) < lower
            s_l = f"< {lower}"
        else:
            invalid = invalid | data[column].astype(float) <= lower
            s_l = f"<= {lower}"

    if upper is not None:
        if not upper_inclusive:
            invalid = invalid | data[column].astype(float) > upper
            s_u = f"> {upper}"
        else:
            invalid = invalid | data[column].astype(float) >= upper
            s_u = f">= {upper}"

    return invalid, (s_l, s_u)


@ExceptionHandlerDecorator("Unable to verify values range for column '{column}'.")
def check_between(
    data: pd.DataFrame,
    column: str,
    lower: float,
    upper: float,
    inclusive: bool = False,
    drop: bool = False,
):
    """
    Verifies the range of values in a column.
    """
    logger.debug(f"Verify values range in column {column}.")
    items = pd.notna(data[column])

    if items.any():
        invalid_items = condition(data, column, lower, upper, inclusive, inclusive)
        if invalid_items[0].any():
            message = f"Validation error! Invalid {column}. Value should be {'and'.join(invalid_items[1])}"
            if drop:
                data.drop(invalid_items.index, inplace=True)
            return get_error_message(data, column, invalid_items, message)


@ExceptionHandlerDecorator(
    "Merging api input with ref data failed for column '{column}'."
)
def merge_with_ref(
    api_input: pd.DataFrame,
    ref: pd.DataFrame,
    column: str,
    add: Union[None, List] = None,
    accept: Union[None, List] = None,
):
    """
    Merges the api_input with ref data.
    """
    logger.debug(f"Merge api_input with reference data: {column}.")

    error = check_invalid_values(
        api_input, column, allowed=ref["input"], drop=True, accept=accept
    )
    if error:
        return error, None

    if add is None:
        add = []

    column_lc = column + "_LC"
    api_input[column_lc] = api_input[column].str.lower()
    ref[column_lc] = ref["input"].str.lower()
    ref.drop(columns=["input"], inplace=True)
    api_input = api_input.merge(ref, how="left", on=add + [column_lc])
    return None, api_input


@ExceptionHandlerDecorator("Unable to validate updated data.")
def validate_updated(api_input: pd.DataFrame, number_of_records: int):
    """
    Check number of rows.
    """
    logger.debug("Validate api_input.")
    if len(api_input) > number_of_records:
        raise Exception("Validation error! 'api_input' has more rows than 'data'.")

    api_input_unique = api_input.drop_duplicates()
    if len(api_input) != len(api_input_unique):
        raise Exception(
            "Validation error! Duplicate records exits in Customer Submission file."
        )


@ExceptionHandlerDecorator("Unable to save api input to {output_folder}.")
def save_api_input(api_input: pd.DataFrame, output_folder: str):
    """
    Saves api_input.
    """
    write_csv(api_input, output_folder + API_INPUT_FILEPATH_RAW)


@ExceptionHandlerDecorator(
    "Removing columns failed for selected fields: {selected_fields}."
)
def remove_api_input_columns(api_input: pd.DataFrame, selected_fields: List):
    for column in api_input.columns:
        if column not in ["__company_id", "companyName", "country"] + selected_fields:
            api_input.drop(column, axis=1, inplace=True)


@ExceptionHandlerDecorator("Renaming columns failed.")
def rename_api_input_columns(api_input: pd.DataFrame):
    api_input.rename(
        columns={
            "AccountName": "companyName",
            "StreetName": "primaryAddress",
            "Country": "country",
            "City": "city",
            "State": "state",
            "PostalCode": "postal",
        },
        inplace=True,
    )


@ExceptionHandlerDecorator(
    "Cannot finalize map process with selected fields: {selected_fields}."
)
def modify_api_input(
    selected_fields: List = None, filepath: str = None, output_folder: str = None
):
    """
    Finalize the map process - use raw api_input to create final version with renamed columns, created csv with
    selected subset of columns.
    """
    if filepath is None:
        filepath = output_folder + API_INPUT_FILEPATH_RAW

    if selected_fields is None:
        selected_fields = []

    api_input = load(filepath)
    rename_api_input_columns(api_input)
    remove_api_input_columns(api_input, selected_fields)

    write_csv(api_input, output_folder + API_INPUT_FILEPATH)


@ExceptionHandlerDecorator("Unable to save master file to {output_folder}.")
def save_master_file(master: pd.DataFrame, output_folder: str):
    """
    Final values replacements and saving file.
    """
    master = master.replace(r"^\s*$", np.nan, regex=True)
    master = master.replace(str(np.nan), "NA")
    master = master.fillna("NA")

    write_csv(master, output_folder + MASTER_FILEPATH)


@ExceptionHandlerDecorator("Unable to save result to {output_folder}.")
def save_result(master: pd.DataFrame, api_input: pd.DataFrame, output_folder: str):
    """
    Saves result files (master, naics, api_input).
    """
    logger.debug("Write output files.")

    save_master_file(master, output_folder)
    save_api_input(api_input, output_folder)


@ExceptionHandlerDecorator("Cannot load template: {filepath_template}.")
def load_template(filepath_template: str):
    """
    Loads template
    """
    with open(filepath_template) as f:
        rows = csv.reader(f)
        next(rows)
        fields = [PortfolioField(row) for row in rows]
        return fields


@ExceptionHandlerDecorator("Unable to map columns from template.")
def map_columns(data: pd.DataFrame, template: List[PortfolioField]):
    """
    Check all required columns (defined in the template).
    Data must contain every required column, but it might have different name (provided).
    We copy all 'provided' (customer_provided) columns with 'required' (input) column name.
    """
    logger.debug("Map columns.")

    errors = []
    for field in template:
        if field.customer_name:
            if field.name != field.customer_name:
                logger.debug(
                    f"Creating column {field.name} from {field.customer_name}."
                )
                data[field.name] = data[field.customer_name]
        elif field.name not in data.columns:
            if field.required:
                error = (
                    f"Customer submission file does not have required column(s) "
                    f"mapped in the template file. Missing column - {field.customer_name} ({field.name})"
                )
                logger.error(error)
                errors.append(error)
            data[field.name] = np.nan

        if field.default != "":
            data[field.name].fillna(field.default, inplace=True)

    if errors:
        raise Exception("\n".join(errors))


@ExceptionHandlerDecorator(
    "Unable to format dates in column '{column}' to format {date_format}."
)
def format_date(
    master: pd.DataFrame,
    column: str,
    date_format: str = "%m/%d/%Y",
    value: datetime.date = None,
):
    """
    Formats date column to required format.
    """
    if value is not None:
        master[column] = value
        return

    if master[column].dtype in ("int64", float):
        master[column] = pd.to_datetime(master[column].astype(str), format="%Y%m%d")
    else:
        master[column] = pd.to_datetime(master[column], format=date_format)
    logger.debug(f"Format date field {column} as {date_format}.")
    master[column] = master[column].dt.strftime(date_format)


@ExceptionHandlerDecorator("Cannot remove missing values.")
def remove_missing_values(master: pd.DataFrame):
    """
    Removes all missing values.
    """
    logger.debug("Remove missing values.")
    master.dropna(how="all", inplace=True)


@ExceptionHandlerDecorator("Error formatting dates.")
def format_dates(master: pd.DataFrame, date_format: str):
    """
    Formats values in columns with dates.
    """
    format_date(master, "InceptionDate", date_format)
    format_date(master, "ExpirationDate", date_format)
    format_date(master, "SubmissionDate", value=datetime.now().strftime(date_format))


@ExceptionHandlerDecorator("Unable to prepare master.")
def prepare(
    master: pd.DataFrame,
    template: List[PortfolioField],
    config_replace: Dict,
    date_format: str,
):
    """
    Remove missing values from master, strip data, map columns to template names, format dates, remove chars,
    replace values.
    """
    remove_missing_values(master)
    strip(master)
    map_columns(master, template)
    format_dates(master, date_format)

    for column in ("AccountName", "City", "StreetName"):
        remove_chars_from_str(master, column)

    replace_values(master, config_replace)

    return master


@ExceptionHandlerDecorator(
    "Unable to load and prepare master from {filepath}, template={filepath_template}."
)
def load_and_and_prepare(
    filepath: str, filepath_template: str, config_replace: Dict, date_format: str
):
    """
    Loads master and template. Prepares the master, cleans the data and validates the columns.
    Then returns the prepared data.
    """
    master = load(filepath)
    template = load_template(filepath_template)

    master = prepare(master, template, config_replace, date_format)
    validate(master)
    return master


@ExceptionHandlerDecorator(
    "Failed at: check fields (invalid/missing AccountName, Country)."
)
def check_fields(api_input: pd.DataFrame):
    """
    Checks AccountName and Country fields.
    """
    invalid_account_name = {("TO BE CONFIRMED", "UNDEFINED", "UNKNOWN"), ".", " ", ""}
    errors = [
        check_invalid_values(api_input, "AccountName", invalid=i)
        for i in invalid_account_name
    ]
    errors.append(check_missing(api_input, "Country"))
    return errors


@ExceptionHandlerDecorator("Failed to load currencies.")
def load_currencies(ref_data_folder: str):
    """
    Get mapping of country-currency for countries for which it is clear (only one country per currency).
    """
    currencies = defaultdict(set)
    with open(ref_data_folder + CURRENCIES_FILENAME) as f:
        rows = csv.DictReader(f)
        for row in rows:
            currencies[row["AlphabeticCode"]].add(row["country_standard_value"])
    return {k: v.pop() for k, v in currencies.items() if len(v) == 1}


@ExceptionHandlerDecorator("Failed to load extensions.")
def load_extensions(ref_data_folder: str):
    """
    Get mapping of country-extension for countries for which it is clear (only one country per extension).
    """
    extensions = defaultdict(set)
    with open(ref_data_folder + EXTENSIONS_FILENAME) as f:
        rows = csv.DictReader(f)
        for row in rows:
            extensions[row["Extension"]].add(row["Country"])
    return {k: v.pop() for k, v in extensions.items() if len(v) == 1}


@ExceptionHandlerDecorator("Unable to get country from value map.")
def get_country_by_map(value_map, value, lower=False):
    country = np.NaN
    if lower:
        value = value.lower()

    for key in value_map:
        k = key.lower() if lower else key
        if k in value:
            country = value_map[key]
            break
    return country


@ExceptionHandlerDecorator("Failed to determine countries by currency.")
def determine_country(master: pd.DataFrame, ref_data_folder: str):
    empty_country = master["Country"].isna()
    count = empty_country.sum()
    if any(empty_country):
        currencies = load_currencies(ref_data_folder)
        currencies.update(
            {
                "USD": "US",
                "CAD": "CA",
                "DKK": "DK",
                "GBP": "GB",
                "RUB": "RU",
                "AUD": "AU",
                "JPY": "JP",
            }
        )
        master.loc[empty_country, "Country"] = master["PolicyCurrency"][
            empty_country
        ].apply(lambda c: get_country_by_map(currencies, c))

    empty_country = master["Country"].isna()
    logger.info(f"Determined {count - empty_country.sum()} countries using currency.")
    count = empty_country.sum()

    if any(empty_country):
        extensions = load_extensions(ref_data_folder)
        master.loc[empty_country, "Country"] = master["AccountName"][
            empty_country
        ].apply(lambda c: get_country_by_map(extensions, c))

    empty_country = master["Country"].isna()
    logger.info(
        f"Determined {count - empty_country.sum()} countries using corporate extension."
    )
    logger.info(f"Number of rows without country: {empty_country.sum()}")

    return master


@ExceptionHandlerDecorator("Failed to create api input.")
def create_api_input(master: pd.DataFrame, ref_data_folder: str, errors: List):
    """
    Create api_input as subset of columns from master. Validate data, merge with countries and states ref data,
    validate number of rows.
    """
    master = determine_country(master, ref_data_folder)
    api_input = get_api_input(master=master)
    errors.extend(check_fields(api_input=api_input))

    countries = load(ref_data_folder + COUNTRIES_FILENAME)
    error, api_input = merge_with_ref(api_input, countries, "Country")
    if error:
        errors.append(error)
        return None

    states = load(ref_data_folder + STATES_FILENAME)
    error, api_input = merge_with_ref(
        api_input, states, "State", add=["country_standard_value"], accept=["NA"]
    )
    if error:
        errors.append(error)
        return None

    validate_updated(api_input, len(master))
    errors.extend(check_values(master=master))
    return api_input


@ExceptionHandlerDecorator("Failed at: check values (range, missing).")
def check_values(master: pd.DataFrame):
    errors = []
    columns_range = {
        "OccurrenceLimit": {"lower": 0, "upper": None},
        "AggLimit": {"lower": 0, "upper": None},
        "AttachmentPoint": {"lower": 0, "upper": None},
        "LineShare": {"lower": 0, "upper": 100.0, "inclusive": True, "drop": True},
    }

    for column in columns_range.keys():
        errors.append(check_missing(master, column))

    for column, values_range in columns_range.items():
        errors.append(check_between(master, column, **values_range))

    return errors


@ExceptionHandlerDecorator("Map step failed.")
def map_data(
    filepath: str,
    filepath_template: str,
    config_replace: Dict,
    ref_data_folder: str,
    output_folder: str,
    date_format: str,
):
    logger.debug("Starting map data.")

    errors = []

    create_output_folders(
        output_folder=output_folder, sub_folders=[INTERMEDIATE_FOLDER, STATUS_FOLDER]
    )
    master = load_and_and_prepare(
        filepath=filepath,
        filepath_template=filepath_template,
        config_replace=config_replace,
        date_format=date_format,
    )
    collect_invalid_records_and_remove(master=master, output_folder=output_folder)
    api_input = create_api_input(
        master=master, ref_data_folder=ref_data_folder, errors=errors
    )

    errors = [e for e in errors if e is not None]

    if errors:
        save_errors(errors=errors, output_folder=output_folder)
        sys.exit(1)
    else:
        save_result(master=master, api_input=api_input, output_folder=output_folder)
