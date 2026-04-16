from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, config


@dataclass
class CurrencyRef(DataClassJsonMixin):
    ref: str
    name: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))


@dataclass
class CurrencyItem(DataClassJsonMixin):
    code: str
    rate: Optional[float] = field(default=None, metadata=config(exclude=lambda v: v is None))
    base: Optional[bool] = field(default=None, metadata=config(exclude=lambda v: v is None))
    created: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))
    updated: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))


@dataclass
class ExportBoxplot(DataClassJsonMixin):
    boxplot: str


@dataclass
class PortfolioRef(DataClassJsonMixin):
    ref: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))
    reference_year: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))


@dataclass
class LossAllocation(DataClassJsonMixin):
    ref: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))
    portfolio: Optional[PortfolioRef] = field(default=None, metadata=config(exclude=lambda v: v is None))


@dataclass
class SimulationModel(DataClassJsonMixin):
    currency: Optional[List[CurrencyItem] | CurrencyRef] = field(default=None,
                                                                 metadata=config(exclude=lambda v: v is None))
    lossAllocation: Optional[LossAllocation] = field(default=None, metadata=config(exclude=lambda v: v is None))
