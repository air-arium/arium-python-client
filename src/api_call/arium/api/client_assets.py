import json
from typing import Optional, List, Dict, TYPE_CHECKING, Union

from api_call.arium.api import request
from api_call.arium.util.perturbations import PerturbationsParameters, add_perturbations_parameters_to_scenario
from config.constants import COLLECTION_PORTFOLIOS, COLLECTION_SCENARIOS, COLLECTION_SIZES, COLLECTION_PROGRAMMES, \
    COLLECTION_LAS, COLLECTION_CURRENCY_TABLES

if TYPE_CHECKING:
    from api_call.client import APIClient


class AssetsClient:

    def __init__(self, client: 'APIClient', collection: str):
        self.client = client
        self.collection = collection
        self.this_list = None

    def list(self, latest: bool = True) -> Optional[List]:
        return request.asset_list(
            client=self.client,
            collection=self.collection,
            latest=latest
        )

    def get(self, asset_id: str) -> Optional[Dict]:
        return request.asset_get(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def get_by_name(self, asset_name: str, exact=True, refresh=True):
        if self.this_list is None or refresh:
            self.this_list = self.list()
        if exact:
            return [item for item in self.this_list if asset_name == item['name']]
        return [item for item in self.this_list if asset_name in item['name']]

    def versions(self, asset_id: str) -> Optional[List]:
        return request.asset_versions(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def create(self, asset_name: str, data: Union[Dict, str], wait=True, presigned=False) -> Optional[Dict]:
        return request.asset_post(
            client=self.client,
            collection=self.collection,
            asset_name=asset_name,
            data=data,
            presigned=presigned
        )

    def delete(self, asset_id: str) -> Optional[Dict]:
        return request.asset_delete(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def rename(self, asset_id: str, asset_name: str):
        return request.asset_rename(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            asset_name=asset_name
        )

    def set_description(self, asset_id: str, description: str):
        return request.asset_set_description(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            description=description
        )

    def get_description(self, asset_id: str) -> Optional[str]:
        return request.asset_get_description(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def get_data(self, asset_id: str) -> Optional[bytes]:
        return request.asset_get_data(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def copy(self, asset_id: str, asset_name: str) -> Optional[Dict]:
        return request.asset_copy(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            asset_name=asset_name
        )

    def lock(self, asset_id: str):
        return request.asset_lock(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            locked=True
        )

    def unlock(self, asset_id: str):
        return request.asset_lock(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            locked=False
        )

    def is_locked(self, asset_id: str) -> bool:
        return request.asset_get(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )["locked"]

    def is_empty(self) -> bool:
        return request.asset_is_empty(
            client=self.client,
            collection=self.collection
        )

    def copy_workspace(self, from_tenant: str, to_tenant: str, asset_ids: List[str] = None) -> Optional[Dict]:
        return request.asset_copy_workspace(
            client=self.client,
            collection=self.collection,
            from_tenant=from_tenant,
            to_tenant=to_tenant,
            asset_ids=asset_ids
        )

    def export_data(self, asset_ids: List[str], export_name: str = None, output_folder: str = "") -> Optional[Dict]:
        return request.asset_export(
            client=self.client,
            collection=self.collection,
            asset_ids=asset_ids,
            export_name=export_name,
            output_folder=output_folder
        )

    def import_data(self, path: str) -> Optional[Dict]:
        return request.asset_import(
            client=self.client,
            collection=self.collection,
            path=path
        )


class PortfoliosClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_PORTFOLIOS)

    def create(self, asset_name: str, data: str = None, file: str = None, csv_date_format: str = None,
               has_header: bool = True, wait: bool = True) -> Optional[Dict]:
        if data is None:
            if file is None:
                raise Exception("'data' of 'file' parameter is required.")
            with open(file, encoding="utf8") as f:
                data = f.read()

        csv_date_format = "dd/mm/yyyy" if csv_date_format is None else csv_date_format
        return request.asset_post(
            client=self.client,
            collection=self.collection,
            asset_name=asset_name,
            data=data,
            params={"csv_date_format": csv_date_format, "csv_has_header": has_header},
            presigned=True,
            wait=wait
        )


class ScenariosClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_SCENARIOS)

    def set_payload_description(self, asset_id: str, payload_description: str):
        return request.asset_update_payload_description(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            payload_description=payload_description
        )

    def get_payload_description(self, asset_id: str) -> Optional[str]:
        return request.asset_get_payload_description(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id
        )

    def update_perturbations(self, parameters: PerturbationsParameters, asset_name: str = None, asset_id: str = None):
        if asset_id is None and asset_name is None:
            raise AttributeError("Please define asset_id or asset_name!")

        if asset_id is None:
            asset_info = self.get_by_name(asset_name).pop()
            asset_id = asset_info['id']
        else:
            asset_info = self.get(asset_id)
            asset_name = asset_info['name']

        scenario = json.loads(self.get_data(asset_id))
        add_perturbations_parameters_to_scenario(parameters, scenario)
        return self.create(asset_name, scenario)


class SizesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client, COLLECTION_SIZES)

    def create(self, asset_name: str, data: str = None, file: str = None,
               has_header: bool = True, wait: bool = True) -> Optional[Dict]:
        if data is None:
            if file is None:
                raise Exception("'data' of 'file' parameter is required.")
            with open(file) as f:
                data = f.read()

        return request.asset_post(
            client=self.client,
            collection=self.collection,
            asset_name=asset_name,
            data=data,
            params={"csv_has_header": has_header},
            presigned=True
        )


class ProgrammesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_PROGRAMMES)


class LAsClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_LAS)


class CurrencyTablesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_CURRENCY_TABLES)
