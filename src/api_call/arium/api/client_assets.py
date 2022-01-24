from typing import Optional, List, Dict, TYPE_CHECKING
from uuid import UUID

from api_call.arium.api.request import asset_list, asset_get, asset_versions, asset_post, asset_rename, asset_copy, \
    asset_lock, asset_delete, asset_get_payload_description, asset_update_payload_description, asset_get_data, \
    asset_set_description, asset_get_description, asset_is_empty, asset_copy_workspace
from constants import COLLECTION_PORTFOLIOS, COLLECTION_SCENARIOS, COLLECTION_SIZES, COLLECTION_PROGRAMMES, \
    COLLECTION_LAS, COLLECTION_CURRENCY_TABLES

if TYPE_CHECKING:
    from api_call.client import APIClient


class AssetsClient:

    def __init__(self, client: 'APIClient', collection: str):
        self.client = client
        self.collection = collection

    def list(self, latest: bool = True) -> Optional[List]:
        return asset_list(client=self.client,
                          collection=self.collection,
                          latest=latest)

    def get(self, asset_id: UUID) -> Optional[Dict]:
        return asset_get(client=self.client,
                         collection=self.collection,
                         asset_id=asset_id)

    def versions(self, asset_id: UUID) -> Optional[List]:
        return asset_versions(client=self.client,
                              collection=self.collection,
                              asset_id=asset_id)

    def create(self, name, data: Dict, wait=True) -> Optional[Dict]:
        return asset_post(client=self.client,
                          collection=self.collection,
                          name=name,
                          data=data,
                          params=None,
                          wait=True)

    def delete(self, asset_id: UUID) -> Optional[Dict]:
        return asset_delete(client=self.client,
                            collection=self.collection,
                            asset_id=asset_id)

    def rename(self, asset_id: UUID, name: str) -> Optional[Dict]:
        return asset_rename(client=self.client,
                            collection=self.collection,
                            asset_id=asset_id,
                            name=name)

    def set_description(self, asset_id: UUID, description: str) -> Optional[str]:
        return asset_set_description(client=self.client,
                                     collection=self.collection,
                                     asset_id=asset_id,
                                     description=description)

    def get_description(self, asset_id: UUID) -> Optional[str]:
        return asset_get_description(client=self.client,
                                     collection=self.collection,
                                     asset_id=asset_id)

    def get_data(self, asset_id: UUID) -> Optional[bytes]:
        return asset_get_data(client=self.client,
                              collection=self.collection,
                              asset_id=asset_id)

    def copy(self, asset_id: UUID, name: str) -> Optional[Dict]:
        return asset_copy(client=self.client,
                          collection=self.collection,
                          asset_id=asset_id,
                          name=name)

    def lock(self, asset_id: UUID) -> bool:
        asset = asset_lock(client=self.client,
                           collection=self.collection,
                           asset_id=asset_id,
                           locked=True)
        return asset["locked"]

    def unlock(self, asset_id: UUID) -> bool:
        asset = asset_lock(client=self.client,
                           collection=self.collection,
                           asset_id=asset_id,
                           locked=False)
        return asset["locked"]

    def is_locked(self, asset_id: UUID) -> bool:
        asset = asset_get(client=self.client,
                          collection=self.collection,
                          asset_id=asset_id)
        return asset["locked"]

    def is_empty(self) -> bool:
        response = asset_is_empty(client=self.client,
                                  collection=self.collection)
        return response["empty"]

    def copy_workspace(self, from_tenant: str, to_tenant: str, asset_ids: List[str] = None) -> Dict:
        response = asset_copy_workspace(client=self.client,
                                        collection=self.collection,
                                        from_tenant=from_tenant,
                                        to_tenant=to_tenant,
                                        asset_ids=asset_ids,
                                        wait=True)
        return response


class PortfoliosClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_PORTFOLIOS)

    def create(self, name: str, data: str = None, file: str = None, csv_date_format: str = None,
               has_header=True) -> Optional[Dict]:
        if data is None:
            if file is None:
                raise Exception("'data' of 'file' parameter is required.")
            with open(file) as f:
                data = f.read()

        csv_date_format = "dd/mm/yyyy" if csv_date_format is None else csv_date_format
        return asset_post(client=self.client,
                          collection=self.collection,
                          name=name,
                          data=data,
                          params={"csv_date_format": csv_date_format, "csv_has_header": has_header},
                          presigned=True,
                          wait=True)


class ScenariosClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_SCENARIOS)

    def update_payload_description(self, asset_id: UUID, description: str) -> Optional[str]:
        return asset_update_payload_description(client=self.client,
                                                collection=self.collection,
                                                asset_id=asset_id,
                                                description=description)

    def get_payload_description(self, asset_id: UUID) -> Optional[str]:
        return asset_get_payload_description(client=self.client,
                                             collection=self.collection,
                                             asset_id=asset_id)


class SizesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client, COLLECTION_SIZES)

    def create(self, name, data: str = None, file: str = None, has_header=True) -> Optional[Dict]:
        if data is None:
            if file is None:
                raise Exception("'data' of 'file' parameter is required.")
            with open(file) as f:
                data = f.read()

        return asset_post(client=self.client,
                          collection=self.collection,
                          name=name,
                          data=data,
                          params={"csv_has_header": has_header},
                          presigned=True,
                          wait=True)


class ProgrammesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_PROGRAMMES)


class LAsClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_LAS)


class CurrencyTablesClient(AssetsClient):

    def __init__(self, client: 'APIClient'):
        super().__init__(client=client, collection=COLLECTION_CURRENCY_TABLES)
