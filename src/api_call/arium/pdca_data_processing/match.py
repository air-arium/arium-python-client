from typing import Dict
from api_call.arium.api.exceptions import ExceptionHandlerDecorator
from api_call.arium.pdca_data_processing.constants import API_INPUT_FILEPATH
from api_call.arium.pdca_data_processing.pdca import PDCACalculations
from api_call.client import APIClient


@ExceptionHandlerDecorator("Match step failed.")
def match_data(
    client: APIClient,
    output_folder: str,
    match_schema: int = 1,
    augment_schema: int = 1,
    batch_size: int = 100,
    simultaneous_batches: int = 5,
    match_params: Dict = None,
):
    if match_params is None:
        match_params = {}
    PDCACalculations(
        client=client,
        input_file=output_folder + API_INPUT_FILEPATH,
        match_schema=match_schema,
        augment_schema=augment_schema,
        batch_size=batch_size,
        simultaneous_batches=simultaneous_batches,
        output_folder=output_folder,
        match_params=match_params,
    ).process()
