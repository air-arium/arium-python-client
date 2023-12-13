OUTPUT_FOLDER = "output/{calc_id}/"
FOLDER_MAP = "map/"
FOLDER_MATCH = "match/"
FOLDER_MERGE = "merge/"
INTERMEDIATE_FOLDER = FOLDER_MAP + "Intermediate/"
STATUS_FOLDER = FOLDER_MAP + "BatchStatus/"

REJECTED_DATA_FILEPATH = INTERMEDIATE_FOLDER + "Rejected_Data.csv"
NAICS_FILEPATH = INTERMEDIATE_FOLDER + "toNAICS.csv"
ERROR_FILEPATH = STATUS_FOLDER + "Error_List.csv"
MASTER_FILEPATH = "masterfile.csv"
API_INPUT_FILEPATH_RAW = INTERMEDIATE_FOLDER + "api_input_raw.csv"

API_INPUT_FILEPATH = "api_input.csv"
API_OUTPUT_FILENAME_RAW = "Match_api_output_raw.csv"
API_OUTPUT_FILENAME = "Match_api_output.csv"

MERGING_REMOVED_DATA_FILEPATH = FOLDER_MERGE + "Merging_Removed_Data_raw.csv"
MERGING_REMOVED_DATA_MASTER_FILEPATH = FOLDER_MERGE + "Merging_Removed_Data.csv"
MERGING_DUPLICATED_FILEPATH = FOLDER_MERGE + "Augmented_Duplicated.csv"

# Ref data (input) files
NAICS_MAPPINGS_FILENAME = "naics_mappings_v4.csv"
INDUSTRY_SIZES_FILENAME = "industry_sizes_naics2012_completed.csv"
COUNTRIES_FILENAME = "countries.csv"
EXTENSIONS_FILENAME = "corporate_ext.csv"
STATES_FILENAME = "states.csv"
CURRENCIES_FILENAME = "currencies.csv"
FILENAME_NAICS_TEMPLATE = "naics_template.csv"
JURISDICTION_FILENAME = "jurisdiction.csv"
ARIUM_TEMPLATE_FILENAME = "AriumTemplate.csv"
NAICS_2012_FILENAME = "naics_2012.csv"
NAICS_2017_FILENAME = "naics_2017.csv"


# PROPERTIES USED IN PDCA (other columns will be ignored!)
PROPERTIES = [
    "stockTicker",
    "employees",
    "companyName",
    "city",
    "recordId",
    "phone",
    "state",
    "primaryAddress",
    "country",
    "stockExchange",
    "industryCodeSystem",
    "revenue",
    "postal",
    "industryCode",
]
