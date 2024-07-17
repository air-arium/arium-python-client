from typing import List, Dict, Optional

from api_call.arium.util.currency_table import CurrencyTable


class AnalysisRequest:
    def __init__(self, **kwargs):
        kwargs = {k.lower().replace("_", ""): v for k, v in kwargs.items()}

        self.export = kwargs.get("export".lower())
        self.reinsurance = kwargs.get("reinsurance".lower())
        self.analysis = kwargs.get(
            "lossAllocation".lower()
        )  # LABELS: part of request do not update
        self.currency = kwargs.get("currency".lower())
        self.size_data = kwargs.get("sizeData".lower())
        self.clean = kwargs.get("clean".lower())
        self.debug = kwargs.get("debug".lower())

    def set_debug(self, debug: Dict):
        self.debug = debug

    def set_clean(self, clean: bool):
        self.clean = clean

    def set_currency_reference(self, reference: str):
        self.currency = {"ref": reference}

    def set_analysis_reference(self, reference: str, portfolio: str):
        self.analysis = {"ref": reference, "portfolio": {"ref": portfolio}}

    def set_reinsurance_reference(self, reference: str):
        self.reinsurance = {"ref": reference}

    def set_currency(self, value: CurrencyTable):
        self.currency = value

    def set_size_data(self, reference: str):
        self.size_data = {"ref": reference}

    def add_csv_export(
        self,
        export_type: str,
        characteristics: List[str],
        metrics: List[str],
        export_non_zero_gross_loss: bool = True,
    ):
        if self.export is None:
            self.export = {"csv": []}

        export = {
            "exportNonZeroGrossLoss": export_non_zero_gross_loss,
            "type": export_type,
            "characteristics": characteristics,
            "metrics": metrics,
        }

        self.export["csv"].append(export)

    def get(self):
        request = {
            "export": self.export,
            "reinsurance": self.reinsurance,
            "lossAllocation": self.analysis,  # LABELS: part of request do not update
            "currency": self._get_currency(),
            "sizeData": self.size_data,
            "clean": self.clean,
            "debug": self.debug,
        }
        return {key: value for key, value in request.items() if value is not None}

    def _get_currency(self):
        return (
            self.currency.get()["currencies"]
            if isinstance(self.currency, CurrencyTable)
            else self.currency
        )


class AnalysisAsset:
    def __init__(self, **kwargs):
        settings = {
            k.lower().replace("_", ""): v for k, v in kwargs.get("settings", {}).items()
        }
        self.minimum_groundup = settings.get("minimumGroundup".lower())
        self.number_of_runs = settings.get("numberOfRuns".lower())
        self.random_seed = settings.get("randomSeed".lower())
        self.perturbations = settings.get("perturbations".lower())
        self.loss_by_ay = settings.get("lossByAY".lower())
        self.business_as_usual = settings.get("businessAsUsual".lower())
        self.portfolio_reference_year = settings.get("portfolioReferenceYear".lower())
        self.bulk_set_equal_weighted = settings.get("bulkSetEqualWeighted".lower())

        self.groups = kwargs.get("groups", [])

    def add_event_reference(
        self,
        group_index: int,
        reference: str,
        portfolio: str,
    ):
        event = {
            "ref": reference,
            "portfolio": {"ref": portfolio},
        }
        self.groups[group_index]["events"].append(event)

    def create_group(
        self,
        group_name: str = "",
        events: List[str] = None,
        equal_weighted: Optional[bool] = None,
        freq_param_key: Optional[str] = None,
        frequency: Optional[float] = None,
    ):
        settings = {
            "frequency": frequency,
            "equalWeighted": equal_weighted,
            "freqParamKey": freq_param_key,
        }
        group = {
            "title": group_name,
            "settings": {k: v for k, v in settings.items() if v is not None},
            "scenarios": [] if events is None else [{"ref": e} for e in events],
        }
        self.groups.append(group)
        return len(self.groups) - 1  # new group index

    def set_minimum_groundup(self, minimum_groundup: float):
        self.minimum_groundup = minimum_groundup

    def set_number_of_runs(self, number_of_runs: int):
        self.number_of_runs = number_of_runs

    def set_random_seed(self, random_seed: int):
        self.random_seed = random_seed

    def set_perturbations(self, perturbations: bool = False):
        self.perturbations = perturbations

    def set_loss_by_ay(self, loss_by_ay: bool = False):
        self.loss_by_ay = loss_by_ay

    def set_business_as_usual(self, business_as_usual: bool = False):
        self.business_as_usual = business_as_usual

    def set_portfolio_reference_year(self, portfolio_reference_year: int):
        self.portfolio_reference_year = portfolio_reference_year

    def set_bulk_set_equal_weighted(self, bulk_set_equal_weighted: bool):
        self.bulk_set_equal_weighted = bulk_set_equal_weighted

    def get(self):
        settings = {
            "minimumGroundup": self.minimum_groundup,
            "numberOfRuns": self.number_of_runs,
            "randomSeed": self.random_seed,
            "perturbations": self.perturbations,
            "lossByAY": self.loss_by_ay,
            "businessAsUsual": self.business_as_usual,
            "portfolioReferenceYear": self.portfolio_reference_year,
            "bulkSetEqualWeighted": self.bulk_set_equal_weighted,
        }
        asset = {
            "settings": {
                key: value for key, value in settings.items() if value is not None
            },
            "groups": self.groups,
        }
        return asset
