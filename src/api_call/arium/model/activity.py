from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from typing import List, Optional, Any, Generator
from zipfile import ZipFile

from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined, config

from api_call.arium.model.simulation import SimulationModel


class ReportType(Enum):
    ZIP = "zip"
    JSON = "json"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Report(DataClassJsonMixin):
    file: str
    size: int
    compressed: bool
    activityId: str = field(
        metadata=config(
            decoder=lambda x: x,
            field_name='calculationId'
        )
    )
    type: ReportType = field(
        default=ReportType.ZIP,
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: ReportType(x)
        )
    )
    _content: Optional[BytesIO] = field(
        init=False,
        default=None,
        metadata=config(
            exclude=lambda x: True,
            encoder=lambda x: None,
            decoder=lambda x: None,
        )
    )

    def _fetch(self) -> Optional[BytesIO]:
        # is replaced in the place in activity client by method injection
        raise Exception("No content found!")

    def bytes(self) -> BytesIO:
        if self._content is None:
            self._content = self._fetch()
        return self._content

    def download(self, file_name):
        with open(file_name, "wb") as f:
            f.write(self.bytes().getbuffer())

    def zip(self) -> ZipFile:
        return ZipFile(self.bytes())

    def files(self) -> Generator[tuple[str, BytesIO], Any, None]:
        with self.zip() as zip_file:
            for file_info in zip_file.filelist:
                filename = file_info.filename
                # Skip directories
                if not filename.endswith('/'):
                    content = BytesIO(zip_file.read(filename))
                    content.seek(0)
                    yield filename, content


class ActivityType(Enum):
    CALCULATION = "calculation"
    LOSS_EXPORT = "lossExport"


class ActivityMode(Enum):
    DETERMINISTIC = "deterministic"
    STOCHASTIC = "stochastic"


class ActivityStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    CANCELING = "canceling"
    CANCELED = "canceled"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputExportType(Enum):
    AAL = "aal"
    EP = "ep"
    YELT = "yelt"
    YLT = "ylt"


class OutputProjection(Enum):
    PORTFOLIO = "portfolio"
    POLICY = "policy"
    LOB = "lob"
    ENTITY = "entity"
    INDUSTRY = "industry"
    JURISDICTION = "jurisdiction"
    NAMED_PERIL = "named_peril"
    CUSTOM_FIELD_1 = "custom_field_1"
    CUSTOM_FIELD_2 = "custom_field_2"
    CUSTOM_FIELD_3 = "custom_field_3"
    CUSTOM_FIELD_4 = "custom_field_4"
    CUSTOM_FIELD_5 = "custom_field_5"


class OutputPerspective(Enum):
    ECONOMIC_LOSS = "economicLoss"
    NON_ECONOMIC_LOSS = "nonEconomicLoss"
    DEFENSE_LOSS = "defenseLoss"
    GROSS_LOSS = "grossLoss"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class OutputItemParameters(DataClassJsonMixin):
    projections: List[OutputProjection] = field(
        metadata=config(
            encoder=lambda xs: [x.value for x in xs],
            decoder=lambda xs: [OutputProjection(x) for x in xs],
        )
    )
    perspectives: Optional[List[OutputPerspective]] = field(
        default=None,
        metadata=config(
            encoder=lambda xs: None if xs is None else [x.value for x in xs],
            decoder=lambda xs: None if xs is None else [OutputPerspective(x) for x in xs],
        ),
    )


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class OutputItem(DataClassJsonMixin):
    parameters: OutputItemParameters
    exportType: OutputExportType = field(
        default=OutputExportType.AAL,
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: OutputExportType(x)
        )
    )


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ActivityPayloadModel(DataClassJsonMixin):
    simulation: Optional[SimulationModel] = None
    references: Optional[List[str]] = field(default_factory=list)
    output: Optional[List[OutputItem]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Activity(DataClassJsonMixin):
    activityId: str
    workspace: str
    name: str
    activityType: ActivityType = field(
        default=ActivityType.CALCULATION,
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: ActivityType(x)
        )
    )
    mode: ActivityMode = field(
        default=ActivityMode.STOCHASTIC,
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: ActivityMode(x)
        )
    )
    status: Optional[ActivityStatus] = field(
        default=None,
        metadata=config(
            encoder=lambda x: x.value if x is not None else None,
            decoder=lambda x: ActivityStatus(x) if x is not None else None
        )
    )
    payload: Optional[ActivityPayloadModel] = field(default=None, metadata=config(exclude=lambda v: v is None))
    errors: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))
    exportType: Optional[str] = None
    lastUpdate: Optional[str] = None
    createdAt: Optional[str] = None
    initiatedBy: Optional[str] = None
    startTime: Optional[str] = None
    progress: Optional[int] = None
    endTime: Optional[str] = None

    def _fetch_reports(self) -> List[Report]:
        # is replaced in the place in activity client by method injection
        raise Exception("No reports found!")

    def report(self) -> Report | None:
        reports = self._fetch_reports()
        if len(reports) > 0:
            return reports[0]
        return None

    def reports(self) -> List[Report]:
        return self._fetch_reports()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ActivityList(DataClassJsonMixin):
    count: int
    list: List[Activity]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ActivitySubmitRequest(DataClassJsonMixin):
    payload: ActivityPayloadModel
    activityType: ActivityType = field(
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: ActivityType(x),
        )
    )
    mode: ActivityMode = field(
        default=ActivityMode.DETERMINISTIC,
        metadata=config(
            encoder=lambda x: x.value,
            decoder=lambda x: ActivityMode(x),
        )
    )
    name: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))

    def validate(self):
        self.__post_init__()

    def __post_init__(self):
        has_simulation = self.payload.simulation is not None
        has_references = bool(self.payload.references)  # len(self.payload.references) > 0
        has_output = bool(self.payload.output)

        if self.activityType not in [ActivityType.LOSS_EXPORT, ActivityType.CALCULATION]:
            raise ValueError(
                f"Unknown activityType: {self.activityType}. It should be one of 'lossExport' or 'calculation'")

        if self.activityType == ActivityType.CALCULATION:

            if not (has_simulation or has_references):
                raise ValueError(
                    "For activityType='calculation', either 'payload.simulation' or a non-empty "
                    "'payload.references' must be provided"
                )
            elif has_simulation:
                if not has_output:
                    self.validate_mandatory_export_output_property(self.payload.output, self.activityType)

                if has_references:
                    # resubmit activity
                    if len(self.payload.references) > 0:
                        raise ValueError(
                            "For activityType='calculation', 'payload.references' should be [] when 'payload.simulation' is provided"
                        )
            elif has_references:
                if len(self.payload.references) != 1:
                    raise ValueError(
                        f"For activityType='calculation', when 'payload.references' is provided, it should contain 1 value instead of {len(self.payload.references)}"
                    )

        if self.activityType == ActivityType.LOSS_EXPORT:
            if has_simulation:
                raise ValueError("For activityType='lossExport', 'payload.simulation' is not allowed")
            self.validate_mandatory_export_output_property(self.payload.output, self.activityType)
            if not has_references:
                raise ValueError("For activityType='lossExport', 'payload.references' is required")

    @staticmethod
    def validate_mandatory_export_output_property(output: List[OutputItem], activity_type: ActivityType):
        if not (bool(output)):
            raise ValueError("'payload.output' is required")
