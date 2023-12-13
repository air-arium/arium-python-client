import json
import os
import sys
from typing import Dict, List

import numpy as np
import pandas as pd

from api_call.arium.api.exceptions import ExceptionHandlerDecorator
from api_call.arium.pdca_data_processing.common import (
    load,
    write_csv,
    get_error_message,
    create_output_folders,
    remove_records,
    save_errors,
    camel_case,
)
from api_call.arium.pdca_data_processing.constants import *
from api_call.arium.pdca_data_processing.pdca import get_folders
from config.get_logger import get_logger

logger = get_logger(__name__)


@ExceptionHandlerDecorator("Cannot load master data from {folder}.")
def load_master_data(folder: str):
    result = []
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            continue
        with open(path) as f:
            result.extend(json.load(f)["masterData"])
    return result


@ExceptionHandlerDecorator(
    "Unable to load pdca results for match={match}, augment={augment}, folder={output_folder}."
)
def load_pdca_results(output_folder: str, match_schema: int, augment_schema: int):
    """
    Loads pdca results from match and augment steps.
    Prepares data.
    """
    match_folder, augment_folder = get_folders(
        output_folder + FOLDER_MATCH, match_schema, augment_schema
    )
    match = pd.json_normalize(load_master_data(match_folder))
    logger.debug(f"Match records loaded. Records: {len(match)}")

    augment = pd.json_normalize(load_master_data(augment_folder))
    logger.debug(f"Augment records loaded. Records: {len(augment)}")
    return match, augment


@ExceptionHandlerDecorator("Update column names in match and augment data.")
def update_column_names(data: pd.DataFrame):
    columns = {"naic" + str(i + 1): "industrycode" + str(i + 1) for i in range(6)}
    columns.update(
        {
            "annualsalesusdollars": "revenue",
            "employeestotal": "employee_count",
            "stateprovince": "state",
            "dunsnumber": "duns",
            "businessname": "companyName",
            "streetaddress": "address",
            "postal": "postalCode"
        }
    )
    data.rename(columns=columns, inplace=True)

    return data


@ExceptionHandlerDecorator("Cannot load api input from {output_folder}.")
def load_api_input(output_folder: str):
    api_input = load(output_folder + API_INPUT_FILEPATH)
    api_input["record_id"] = np.arange(1, len(api_input) + 1)
    return api_input


@ExceptionHandlerDecorator("Unable to merge pdca result.")
def merge_pdca_result(
    match: pd.DataFrame, augment: pd.DataFrame, api_input: pd.DataFrame
):
    """
    We are merging three columns: augment and match results (as result) and then api_input and result.
    If the column exists in more than one tables then suffixes are added
    """
    match = augment.merge(
        match,
        how="outer",
        left_on="original_duns",
        right_on="duns",
        suffixes=("", "_match"),
    )
    return match.merge(
        api_input,
        on=["record_id"],
        how="outer",
        indicator=True,
        suffixes=("", "_input"),
    )


def log_metric(df_name, df: pd.DataFrame):
    logger.debug(f"--- Metric for {df_name}")
    logger.debug(f"Rows: {df.shape[0]}")
    logger.debug(f"Columns: {df.shape[1]}")
    logger.debug("--- Metric end ---")


@ExceptionHandlerDecorator(
    "Cannot load result for match={match}, augment={augment}, folder={output_folder}."
)
def load_data_to_merge(output_folder: str, match: int, augment: int) -> pd.DataFrame:
    """
    Loads and pdca results (match, augment and api returned data)

    :param output_folder: output folder with match step files
    :param match: schema number
    :param augment: schema number
    :return:
    """
    logger.debug(
        f"Load and pdca results (match_schema={match}, augment_schema={augment})."
    )

    match, augment = load_pdca_results(output_folder, match, augment)
    update_column_names(match)
    update_column_names(augment)
    api_input = load_api_input(output_folder)

    return match, augment, api_input


@ExceptionHandlerDecorator(
    "Cannot combine big dumpling out of  match, augment and api data."
)
def merge_all_pdca_results(
    match_data: pd.DataFrame, augment_data: pd.DataFrame, api_data: pd.DataFrame
) -> pd.DataFrame:
    logger.debug(f"Combining match, augment and api data into a giant dumpling")

    pdca_result = merge_pdca_result(match_data, augment_data, api_data)
    pdca_result = pdca_result.drop_duplicates()
    pdca_result.drop(
        pdca_result[pdca_result["__company_id"].isnull()].index, inplace=True
    )
    pdca_result["__company_id"] = pdca_result["__company_id"].astype(int)
    pdca_result = pdca_result.replace(np.nan, "", regex=True)
    pdca_result["SizeMetricCurrency"] = "USD"
    return pdca_result


@ExceptionHandlerDecorator("Unable to remove invalid records.")
def remove_invalid_and_save(
    pdca_result: pd.DataFrame, master: pd.DataFrame, output_folder: str, confidence: int
):
    """
    Merges removed items with master data and saves to the file
    """
    logger.debug("Remove invalid items and save.")

    removed = collect_invalid_records_and_remove(pdca_result, output_folder, confidence)
    if removed is None:
        return

    removed = removed[["__company_id", "Comment"]]
    removed = pd.merge(master, removed, how="outer", indicator=True)
    removed = removed.loc[removed["_merge"] == "both"].drop("_merge", axis=1)
    removed = removed.sort_values(by=["__company_id"], ascending=True)
    removed = removed.replace(np.NaN, "NA")
    first_column = removed.pop("__company_id")
    removed.insert(0, "__company_id", first_column)

    write_csv(removed, output_folder + MERGING_REMOVED_DATA_MASTER_FILEPATH)


@ExceptionHandlerDecorator("Failed to collect and remove invalid records.")
def collect_invalid_records_and_remove(
    data: pd.DataFrame, output_folder: str, confidence: int
):
    """
    Remove items:
        - without duns
        - without industry code
        - with industry code 999990 - unknown/placeholder code
        - with low confidence
    """
    logger.debug("Collect invalid records.")

    #no_duns_index = data["duns"].isnull()
    no_duns_index = data["duns"] == ''
    #no_industry_code = data["industrycode1"].isnull()
    no_industry_code = data["industrycode1"] ==''
    wrong_industry_code = data["industrycode1"] == "999990"
    low_confidence = pd.to_numeric(data["confidence"], errors="coerce") < confidence

    records_with_message = {
        "Not_Matched_no_duns": no_duns_index,
        "Matched_InvalidNAICS_no_naics": no_industry_code,
        "Matched_InvalidNAICS_999990": wrong_industry_code,
        "Matched_ValidNAICS_LowConfidence": low_confidence,
    }

    return remove_records(
        data=data,
        records=records_with_message,
        filepath=output_folder + MERGING_REMOVED_DATA_FILEPATH,
        module="Merging",
    )


@ExceptionHandlerDecorator("Unable to create naics.")
def create_naics(pdca_result: pd.DataFrame, code_value: str):
    """
    Creates a table with __company_id, AccountName, IndustryCodeView and NAICS017, where code_value is a column
    with industry code values.
    """
    logger.debug(f"Create naics: {code_value}")

    naics_ = pd.DataFrame()
    naics_["__company_id"] = pdca_result["__company_id"]
    naics_["duns"] = pdca_result["duns"]
    naics_["AccountName"] = pdca_result["companyName"]
    naics_["NAICS2017"] = pdca_result[code_value].values
    naics_["IndustryCodeView"] = code_value

    pdca_result.drop(
        columns=[
            code_value,
        ],
        axis=1,
        inplace=True,
    )

    return clean_naics(naics_)


@ExceptionHandlerDecorator("Failed to get naics dict.")
def get_naics_dict(pdca_result: pd.DataFrame):
    """
    Gets subset of data related to industrycodes. Removes industrycodes from pdca_result.
    Returns separate dataset for each industrycode column.
    """
    return {
        i + 1: create_naics(pdca_result, "industrycode" + str(i + 1)) for i in range(6)
    }


@ExceptionHandlerDecorator("Cleaning naics failed.")
def clean_naics(naics: pd.DataFrame):
    """
    Removes rows with empty value in NAICS2017.
    """
    no_value = np.logical_or(naics["NAICS2017"].isnull(), naics["NAICS2017"] == "")
    unknown = naics.NAICS2017 == "999990"
    naics.drop(naics[np.logical_or(no_value, unknown)].index, inplace=True)
    return naics


@ExceptionHandlerDecorator("Unable to map naics.")
def map_naics(naics: pd.DataFrame, ref_data_folder: str, errors: List):
    """
    Loads mappings.
    Applies mapping 2017to2012.
    Validates naics.
    """
    logger.debug("Map naics.")

    naics_mappings = load(ref_data_folder + NAICS_MAPPINGS_FILENAME)

    naics_2017_to_2012_mappings = naics_mappings[
        naics_mappings["CodeSource"] == "2017to2012"
    ].copy()
    naics_2017_to_2012_mappings.drop(columns=["CodeSource"], inplace=True)
    naics_2017_to_2012_mappings.rename(columns={"NAICS": "NAICS2017"}, inplace=True)

    naics["NAICS2017"] = naics["NAICS2017"].astype(int)
    naics = pd.merge(naics, naics_2017_to_2012_mappings, on="NAICS2017", how="left")

    naics["IndustryCode"] = naics["Arium_NAICS"].fillna(naics["NAICS2017"])
    naics["IndustryCodeSystem"] = "NAICS2012"

    errors.append(
        validate_naics(naics, load(ref_data_folder + NAICS_2012_FILENAME), "NAICS2012")
    )
    errors.append(
        validate_naics(naics, load(ref_data_folder + NAICS_2017_FILENAME), "NAICS2017")
    )

    return naics


@ExceptionHandlerDecorator("Failed to prepare company naics.")
def get_company_naics(naics: pd.DataFrame):
    """
    Prepares company naics.
    """
    company_naics = naics.copy()
    columns = [
        "__company_id",
        "IndustryCodeView",
        "IndustryCode",
        "IndustryCodeSystem",
        "duns",
    ]
    subset = ["__company_id", "IndustryCode", "IndustryCodeSystem", "duns"]
    company_naics = (
        company_naics[columns]
        .drop_duplicates()
        .drop_duplicates(subset=subset)
        .reset_index(drop=True)
    )

    return company_naics


@ExceptionHandlerDecorator("Unable to validate naics with code system {code_system}.")
def validate_naics(naics: pd.DataFrame, naics_data: pd.DataFrame, code_system: str):
    """
    Selects items with given code system. Checks if all values are included in ref data (naics_data).
    """
    logger.debug(f"Validate naics with code system {code_system}")

    items_to_verify = naics["IndustryCodeSystem"] == code_system
    naics_not_in = (
        ~naics["IndustryCode"].astype(int).astype(str).isin(naics_data[code_system])
    )
    invalid = np.logical_and(items_to_verify, naics_not_in)
    if invalid.any():
        return get_error_message(
            data=naics,
            column="IndustryCode",
            message=f"Validation error in merge program - Not all NAICS codes are valid {code_system}",
            items=invalid,
        )


@ExceptionHandlerDecorator("Unable to verify duplicated records.")
def verify_duplicated(pdca_result: pd.DataFrame, output_folder: str):
    """
    Check for duplicated data.
    """
    logger.debug("Verify duplicated.")

    duplicated = pdca_result.duplicated()
    if duplicated.any():
        remove_records(
            data=pdca_result,
            records={"Duplicated": duplicated},
            filepath=output_folder + MERGING_DUPLICATED_FILEPATH,
            module="Merging",
        )
        logger.error("Validation error in merge program - duplicated records!")


@ExceptionHandlerDecorator("Failed to prepare jurisdiction.")
def prepare_jurisdiction(ref_data_folder: str):
    """
    Prepares jurisdiction data from data about countries and jurisdiction. Uses lower case country names.
    """
    countries = load(ref_data_folder + COUNTRIES_FILENAME)
    jurisdiction = load(ref_data_folder + JURISDICTION_FILENAME)

    jurisdiction = countries.merge(jurisdiction, on="country_standard_value")
    jurisdiction = jurisdiction.drop_duplicates(subset=["input"])
    jurisdiction["CountryLowerCase"] = jurisdiction["input"].str.lower()
    jurisdiction.rename(columns={"MapsToJurisdiction": "Jurisdiction"}, inplace=True)

    return jurisdiction[["CountryLowerCase", "Jurisdiction"]]


@ExceptionHandlerDecorator("Failed to add jurisdiction.")
def add_jurisdiction(pdca_result: pd.DataFrame, ref_data_folder: str):
    """
    Adds 'Jurisdiction' column.
    Prepares jurisdiction. Merges pdca results with jurisdiction. Uses lower case values.
    """
    logger.debug("Add jurisdiction.")

    jurisdiction = prepare_jurisdiction(ref_data_folder)
    pdca_result["CountryLowerCase"] = pdca_result["Country"].map(lambda x: x.lower())
    return pdca_result.merge(jurisdiction, on="CountryLowerCase")


@ExceptionHandlerDecorator("Failed to add industry size.")
def add_industry_size(pdca_result: pd.DataFrame, ref_data_folder: str):
    """
    Adds "AnnualSales" column.
    Merges pdca results with industry size.
    """
    logger.debug("Add industry size.")

    industry_sizes = load(ref_data_folder + INDUSTRY_SIZES_FILENAME)
    industry_sizes.rename(
        columns={
            "NAICS2012": "IndustryCode",
            "jurisdiction": "Jurisdiction",
            "AnnualSalesUSDollars_Millions": "AnnualSales",
        },
        inplace=True,
    )
    pdca_result["IndustryCode"] = pdca_result["IndustryCode"].astype(int).astype(str)
    return pdca_result.merge(
        industry_sizes, how="left", on=["IndustryCode", "Jurisdiction"]
    )


@ExceptionHandlerDecorator("Failed to calculate size metric factor.")
def calculate_size_metric_factor(pdca_result: pd.DataFrame, ref_data_folder: str):
    """
    Calculates size metrics factor.
    """
    pdca_result = add_industry_size(pdca_result, ref_data_folder)
    column = "AnnualSales"
    group_by = ["__company_id", "AccountNumber", "Jurisdiction"]
    pdca_result["SizeMetricFactor"] = pdca_result[column] / (
        pdca_result.groupby(group_by)[column].transform("sum")
    )
    return pdca_result


@ExceptionHandlerDecorator("Unable to update turnover and employee number.")
def update_turnover_and_employee_number(pdca_result: pd.DataFrame):
    """
    Calculates SizeMetricsFactor and updates EmployeeNumber and Turnover
    """
    logger.debug("Update turnover and employee number.")

    pdca_result["Turnover"] = pdca_result["Revenue"] * pdca_result[
        "SizeMetricFactor"
    ].fillna(1)
    pdca_result["EmployeeNumber"] = pdca_result["EmployeeCount"] * pdca_result[
        "SizeMetricFactor"
    ].fillna(1)

    return pdca_result


@ExceptionHandlerDecorator("Old - Unable to update turnover and employee number.")
def old_update_turnover_and_employee_number(pdca_result: pd.DataFrame):
    """
    Updatess columns EmployeeNumber and Turnover to values from EmployeeCount and Revenue as
    as they are retruned as the final result of the whole process.
    """
    logger.debug("Old - Update turnover and employee number.")

    pdca_result["EmployeeNumber"] = pdca_result["EmployeeCount"]
    pdca_result["Turnover"] = pdca_result["Revenue"]


@ExceptionHandlerDecorator("Unable to merge with master.")
def merge_with_master(pdca_results: pd.DataFrame, master: pd.DataFrame):
    """
    Merges pdca results with master table.
    """
    logger.debug("Merge with master.")

    pdca_results = pd.merge(
        master, pdca_results, on="__company_id", how="left", suffixes=("Master", "")
    )

    return pdca_results


@ExceptionHandlerDecorator("Unable to replace values in column '{column}'.")
def replace_values_in_column(pdca_result: pd.DataFrame, column: str, mapping: Dict):
    """
    Replaces value in column.
    """
    logger.debug(f"Replace values in column {column}.")

    for old_value, new_value in mapping.items():
        pdca_result.loc[pdca_result[column] == old_value, column] = new_value


@ExceptionHandlerDecorator("Unable to save results to {output_folder}.")
def save_results(
    pdca_result: pd.DataFrame, output_folder: str, ref_data_folder: str, all_naics: bool
):
    """
    Saves result with all columns (raw).
    In not all_naics select only data related to first industry code.
    Selects only columns from the template and saves again.
    """
    logger.debug("Save results.")

    write_csv(pdca_result, output_folder + API_OUTPUT_FILENAME_RAW)

    template = load(ref_data_folder + ARIUM_TEMPLATE_FILENAME)
    columns = template.columns.to_list()

    if not all_naics:
        # as result copy only rows which contains 'industrycode1' in "IndustryCodeView.
        # it means it ignores other values and rows which don't have it defined!
        pdca_result = pdca_result.loc[
            pdca_result["IndustryCodeView"] == "industrycode1"
        ].copy()

    pdca_result = pdca_result[pdca_result.columns.intersection(columns)]
    write_csv(pdca_result, output_folder + API_OUTPUT_FILENAME, columns=columns)


@ExceptionHandlerDecorator("Unable to create company naics.")
def create_company_naics(pdca_result: pd.DataFrame, ref_data_folder: str, errors: List):
    """
    Creates dictionary with data related to each industry code column.
    Then maps selected naics using naics mapping.
    """
    logger.debug(f"Create naics.")

    naics = get_naics_dict(pdca_result)
    naics_ = []

    for naics_no in range(1, 7):
        naics_.append(map_naics(naics[naics_no], ref_data_folder, errors))

    return get_company_naics(pd.concat(naics_))


@ExceptionHandlerDecorator("Unable to transform company into naics rows.")
def transform_company_into_naics_rows(
    pdca_result: pd.DataFrame, ref_data_folder: str, errors: List
):
    """
    Process naics data pdca_results. Uses naics mapping.
    """
    logger.debug(f"Process naics.")

    naics = create_company_naics(
        pdca_result=pdca_result,
        ref_data_folder=ref_data_folder,
        errors=errors,
    )

    pdca_result = naics.merge(pdca_result, on=["__company_id", "duns"])
    return pdca_result


@ExceptionHandlerDecorator("Failed to rename columns.")
def rename_columns(pdca_result: pd.DataFrame):
    """
    Transforms column names to camelcase. Renames columns.
    """
    logger.debug("Rename columns.")
    pdca_result.columns = pdca_result.columns.map(camel_case)
    pdca_result.rename(
        columns={
            "CompanyName": "AccountName",
            "Duns": "AccountNumber",
            "Address": "StreetNumber",
        },
        inplace=True,
    )


@ExceptionHandlerDecorator("Failed to replace values.")
def replace_values(pdca_result: pd.DataFrame):
    """
    Replaces values in Country and IndustryCode columns.
    """
    replace_values_in_column(
        pdca_result=pdca_result,
        column="Country",
        mapping={
            "ENGLAND": "UNITED KINGDOM",
            "WALES": "UNITED KINGDOM",
            "SCOTLAND": "UNITED KINGDOM",
            "NORTHERN IRELAND": "UNITED KINGDOM",
        },
    )

    replace_values_in_column(
        pdca_result=pdca_result,
        column="IndustryCode",
        mapping={
            443141: 44314,
            443142: 44314,
        },
    )


@ExceptionHandlerDecorator("Merge step failed.")
def merge_data(
    match_schema: int,
    augment_schema: int,
    confidence: int,
    output_folder: str,
    ref_data_folder: str,
    all_naics: bool = True,
):
    logger.debug("Merge data.")

    errors = []

    create_output_folders(output_folder=output_folder, sub_folders=[FOLDER_MERGE])
    match_data, augment_data, api_data = load_data_to_merge(
        output_folder=output_folder, match=match_schema, augment=augment_schema
    )

    pdca_result = merge_all_pdca_results(
        match_data=match_data, augment_data=augment_data, api_data=api_data
    )

    master = load(output_folder + MASTER_FILEPATH)
    remove_invalid_and_save(
        pdca_result=pdca_result,
        master=master,
        output_folder=output_folder,
        confidence=confidence,
    )

    # Each augmented row contains up to 6 naics codes. It means that this company operates in different
    # industries. Below function replaces company row into a few rows - each one reflects 1 company naics code.
    pdca_result = transform_company_into_naics_rows(
        pdca_result=pdca_result, ref_data_folder=ref_data_folder, errors=errors
    )

    verify_duplicated(pdca_result=pdca_result, output_folder=output_folder)

    # this is dangerous. it changes column names to camel_case and a few strange things like
    # duns -> AccountNumber. My head just exploded.
    rename_columns(pdca_result=pdca_result)

    pdca_result = add_jurisdiction(
        pdca_result=pdca_result, ref_data_folder=ref_data_folder
    )

    if all_naics:
        # EmployeeNumber and Turnover will updated according to the size_metric_factor
        # That's why the columns needs to be dropped from master so they appear
        # with the same names once merged pdca_result and master.
        master.drop(columns=["EmployeeNumber", "Turnover"], inplace=True)
        pdca_result = calculate_size_metric_factor(
            pdca_result=pdca_result, ref_data_folder=ref_data_folder
        )
        pdca_result = update_turnover_and_employee_number(pdca_result=pdca_result)
    else:
        pdca_result["EmployeeNumber"] = pdca_result["EmployeeCount"]
        pdca_result["Turnover"] = pdca_result["Revenue"]

    pdca_result = merge_with_master(pdca_results=pdca_result, master=master)

    replace_values(pdca_result)

    errors = [e for e in errors if e is not None]

    if errors:
        save_errors(errors=errors, output_folder=output_folder)
        sys.exit(1)
    else:

        pdca_result["IndustryCode"] = pdca_result["IndustryCode"].fillna(0).astype(int)
        pdca_result = pdca_result.loc[pdca_result["IndustryCode"] != 0]

        save_results(
            pdca_result=pdca_result,
            output_folder=output_folder,
            ref_data_folder=ref_data_folder,
            all_naics=all_naics,
        )
