from typing import List, Dict


class PerturbationsParameters:
    def __init__(
        self,
        shape: str,
        subshape: str,
        description: str,
        total_loss: float,
        accounts: int,
        simulation: str,
        title: str,
        upper: float,
        lower: float,
        truncation: bool,
        bankruptcy: str = None,
        events: List[str] = None,
    ):
        self.shape = shape
        self.subshape = subshape
        self.description = description
        self.totalLoss = total_loss
        self.accounts = accounts
        self.simulation = simulation
        self.title = title
        self.upper = upper
        self.lower = lower
        self.truncation = truncation
        self.bankruptcy = bankruptcy
        self.events = events

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if value is not None}


def add_perturbations_parameters_to_event(
    parameters: PerturbationsParameters, event: Dict
):
    event["event"]["perturbations"] = parameters.to_dict()
    return event


def get_perturbations_parameters(parameters: Dict):
    return PerturbationsParameters(
        shape=parameters["Shape"],
        subshape=parameters["Subshape"],
        description=parameters["Description"],
        total_loss=parameters["TotalLoss"],
        accounts=parameters["Accounts"],
        simulation=parameters["Simulation"],
        title=parameters["Title"],
        upper=parameters["Upper"],
        lower=parameters["Lower"],
        truncation=parameters["Truncation"],
        bankruptcy=parameters.get("Bankruptcy", None),
        events=parameters.get("Events", None),
    )
