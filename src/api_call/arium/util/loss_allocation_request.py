from typing import List, Union, Dict

from api_call.arium.util.currency_table import CurrencyTable
from api_call.arium.util.filter import PortfolioFilter


class Asset:
    __slots__ = '_asset', '_type'

    def __init__(self, asset: Union[list, dict, str] = None, asset_type: str = None) -> None:
        self._asset = asset
        self._type = asset_type

    def set_type(self, asset_type: str) -> None:
        if asset_type not in ['value', 'ref']:
            raise ValueError("type '{}' not valid, expecting 'ref' or 'value'.")
        self._type = asset_type

    def set_asset(self, asset: Union[list, dict, str]) -> None:
        self._asset = asset

    def set(self, asset: Union[list, dict, str], asset_type: str) -> None:
        self.set_asset(asset)
        self.set_type(asset_type)

    def __bool__(self):
        return self._asset is not None and self._type is not None

    def get(self) -> Union[list, dict, str]:
        return self._asset


class LossAllocationRequest:
    def __init__(self):
        self.export = None
        self.number_of_runs = None
        self.apply_multi_year = None
        self.random_seed = None
        self.reinsurance = None
        self.loss_allocation = None
        self.currency = None
        self.size_data = None
        self.min_groundup_loss = None

    def set_min_groundup_loss(self, min_groundup_loss: float):
        if min_groundup_loss < 10000:
            raise ValueError('Minimum ground-up loss value should be >= 10000')

        self.min_groundup_loss = min_groundup_loss

    def set_multi_year(self, apply_multiyear: bool):
        self.apply_multi_year = apply_multiyear

    def set_number_of_runs(self, number_of_runs: int):
        self.number_of_runs = number_of_runs

    def set_random_seed(self, random_seed: float):
        self.random_seed = random_seed

    def set_currency_reference(self, reference: str):
        self.currency = {"ref": reference}

    def set_loss_allocation_reference(self, reference: str, portfolio: str):
        self.loss_allocation = {"ref": reference, "portfolio": {"ref": portfolio}}

    def set_reinsurance_reference(self, reference: str):
        self.reinsurance = {"ref": reference}

    def set_currency(self, value: CurrencyTable):
        self.currency = value

    def set_size_data(self, reference: str):
        self.size_data = {"ref": reference}

    def add_csv_export(self, export_type: str, characteristics: List[str], metrics: List[str]):
        if self.export is None:
            self.export = {"csv": []}

        export = {
            "type": export_type,
            "characteristics": characteristics,
            "metrics": metrics
        }

        self.export["csv"].append(export)

    def add_scenario_reference(self, key: int, reference: str, scenario_id: str, portfolio: str,
                               group_name: str = "", la_type: int = 0, occurrence: float = 0):
        if self.loss_allocation is None:
            self.loss_allocation = {}

        if key not in self.loss_allocation:
            self.loss_allocation[key] = {
                "groupName": group_name,
                "type": la_type,
                "occurrence": occurrence,
                "scenarios": [{"ref": reference, "portfolio": {"ref": portfolio}, "id": scenario_id}]
            }
        else:
            self.loss_allocation[key]["scenarios"].append(
                {"ref": reference, "portfolio": {"ref": portfolio}, "id": scenario_id})

    def get(self):
        request = {
            "export": self.export,
            "numberOfRuns": self.number_of_runs,
            "randomSeed": self.random_seed,
            "reinsurance": self.reinsurance,
            "lossAllocation": self.loss_allocation,
            "currency": self._get_currency(),
            "sizeData": self.size_data,
            "multiYear": self.apply_multi_year,
            "minimumGroundup": self.min_groundup_loss
        }
        return {key: value for key, value in request.items() if value is not None}

    def _get_currency(self):
        return self.currency.get()["currencies"] if isinstance(self.currency, CurrencyTable) else self.currency


class Exposures:
    def __init__(self):
        self.currency = Asset()
        self.reinsurance = Asset()
        self.export = Asset()
        self.portfolio = Asset()

        # Filters has a default = no filter
        self.filters = Asset()
        self.filters.set({'values': [], 'currency': 'USD'}, 'value')

    def set_export(self, metrics: List[str], characteristics: List[str], export_type: str = "simulation",
                   export_format: str = 'csv') -> None:
        asset = {
            export_format: [{
                'type': export_type,
                'characteristics': characteristics,
                'metrics': metrics
            }]
        }
        self.export.set(asset=asset, asset_type='value')

    def add_filter(self, portfolio_filter: PortfolioFilter):
        self.filters.get()['values'].append(portfolio_filter.get())

    def set_filter_currency(self, currency: str):
        self.filters.get()['currency'] = currency

    def set_currency_ref(self, reference: str) -> None:
        self.currency.set({'ref': reference}, 'ref')

    def set_currency(self, currency: List[dict]):
        self.currency.set(currency, 'value')

    def set_reinsurance_ref(self, reference: str) -> None:
        self.reinsurance.set({'ref': reference}, 'ref')

    def set_portfolio_refs(self, references: Union[List[str], str]) -> None:
        if isinstance(references, str):
            self.portfolio.set([{'ref': references}], 'ref')
        else:
            self.portfolio.set([{'ref': _} for _ in references], 'ref')

    def get_request_json(self) -> Dict:
        request = {}
        for asset in ["portfolio", "export", "reinsurance", "currency", "filters"]:
            try:
                request[asset] = getattr(self, asset).get()
            except Exception:
                raise ValueError("Missing '{}' object or reference.".format(asset))

        return request
