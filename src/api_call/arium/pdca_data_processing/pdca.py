import csv
import json
import math
import os
from collections import defaultdict
from enum import Enum
from http import HTTPStatus
from time import sleep
from typing import Dict

from api_call.arium.api.request import get_content
from api_call.arium.pdca_data_processing.constants import PROPERTIES, FOLDER_MATCH
from config.constants import BASE_URI_PDCA
from config.get_logger import get_logger

logger = get_logger(__name__)


def get_file_size(file):
    return len(list(open(file, encoding="utf-8")))


def generate_batch(rows, batch_size):
    """
    Generates batches with rows (splits rows into batches with batch_size number of items)
    """
    for n, i in enumerate(range(0, len(rows), batch_size)):
        logger.debug(f"Batch {n}: ({i}-{i + batch_size})")
        yield n, rows[i : i + batch_size]


def get_match_inputs(batch, match_params=None):
    if match_params is None:
        match_params = {}

    logger.debug(f"Match params: " + json.dumps(match_params))

    match_inputs = {"matchInputs": []}

    match_inputs.update(match_params)

    for row in batch:
        row = {
            k: v for k, v in row.items() if v != "NA" and v != "" and k in PROPERTIES
        }
        match_inputs["matchInputs"].append(row)
    logger.debug(f"Match inputs size: {len(match_inputs['matchInputs'])}")
    return match_inputs


def get_augment_inputs(result_match):
    d = {
        "augmentInputs": [{"duns": d["dunsnumber"]} for d in result_match["masterData"]]
    }
    logger.debug(f"Augment inputs size: {len(d['augmentInputs'])}")
    return d


def can_start(limit, current):
    if limit is None:
        return True
    if limit == -1:
        return True
    return current < limit


def get_result(client, endpoint):
    return client.get_request(endpoint, url=BASE_URI_PDCA)


def is_ready(response):
    return response.status_code != HTTPStatus.ACCEPTED


class PDCAStage(Enum):
    INITIALIZED = 0
    MATCH = 1
    AUGMENT = 2
    FINISHED = 3


class PDCACalcScheduler:
    def __init__(self, client, batch_size, number_of_batches, simultaneous_batches):
        self.client = client
        self.number_of_batches = number_of_batches
        self.batch_size = batch_size
        self.simultaneous_batches = simultaneous_batches

        self.jobs = []
        self._last_status = None

    def initialized(self):
        return sum(
            [1 for s in self.jobs if not s.processing and s.stage == PDCAStage.MATCH]
        )

    def match(self):
        return sum(
            [1 for s in self.jobs if s.processing and s.stage == PDCAStage.MATCH]
        )

    def augment(self):
        return sum(
            [1 for s in self.jobs if s.processing and s.stage == PDCAStage.AUGMENT]
        )

    def finished_match(self):
        return sum(
            [
                1
                for s in self.jobs
                if s.stage == PDCAStage.AUGMENT or s.stage == PDCAStage.FINISHED
            ]
        )

    def finished(self):
        return sum([1 for s in self.jobs if s.stage == PDCAStage.FINISHED])

    def get_progress(self):
        match_progress = self.finished_match() / self.number_of_batches * 100
        augment_progress = self.finished() / self.number_of_batches * 100

        status = match_progress, augment_progress, self.match(), self.augment()
        if status != self._last_status:
            self._last_status = status
            return status

    def done(self):
        return self.finished() == self.number_of_batches

    def all_started(self):
        return len(self.jobs) >= self.number_of_batches

    def match_done(self):
        return self.match == self.number_of_batches

    def push(self, status):
        self.jobs.append(status)

    def stop(self):
        for status in self.jobs:
            if status.processing:
                if status.stage == PDCAStage.MATCH:
                    response = get_result(self.client, status.location_match)
                    if is_ready(response):
                        # Save match result
                        status.result = get_content(response)
                        with open(status.filename_match, "w") as output_file:
                            json.dump(status.result, output_file)
                        status.stage = PDCAStage.AUGMENT
                        status.processing = False
                        logger.debug(f"Job {status.batch_number} finished match.")
                elif status.stage == PDCAStage.AUGMENT:
                    response = get_result(self.client, status.location_augment)
                    if is_ready(response):
                        # Save augment result
                        result = get_content(response)
                        with open(status.filename_augment, "w") as output_file:
                            json.dump(result, output_file)
                        status.stage = PDCAStage.FINISHED
                        status.processing = False
                        logger.debug(f"Job {status.batch_number} finished augment.")

    def run(self, match_schema, augment_schema, match_params):
        for status in self.jobs:
            if status.stage == PDCAStage.FINISHED or status.processing:
                continue

            if status.stage == PDCAStage.MATCH and self.can_start_match():
                match_inputs = get_match_inputs(status.result, match_params)
                status.location_match = self.client.get_pdca().submit_match(
                    match_inputs, schema=match_schema
                )
                status.processing = True
                logger.debug(f"Job {status.batch_number} started match.")
            elif status.stage == PDCAStage.AUGMENT and self.can_start_augment():
                augment_inputs = get_augment_inputs(status.result)
                status.result = {}
                status.location_augment = self.client.get_pdca().submit_augment(
                    augment_inputs, schema=augment_schema
                )
                status.processing = True
                logger.debug(f"Job {status.batch_number} started augment.")

    def start(self, gen, match_schema, augment_schema, output_folder):
        # Start calculations
        while not self.match_done() and self.can_start_initialize():
            # Start as many jobs as possible (load data, add to jobs, update status)
            if self.all_started():
                return
            self.next(gen, match_schema, augment_schema, output_folder)

    def process(self, gen, match_schema, augment_schema, output_folder, match_params):
        while not self.done():
            yield self.get_progress()
            self.start(gen, match_schema, augment_schema, output_folder)
            # Stop all jobs, which are finished (save results, update status)
            self.stop()
            # Run as many jobs as possible (either match or augment state)
            self.run(match_schema, augment_schema, match_params)
            sleep(5)

    def next(self, gen, match_schema, augment_schema, output_folder):
        batch_number, batch = next(gen)
        match_folder, augment_folder = get_folders(
            output_folder, match_schema, augment_schema
        )

        # this is important to save results in /raw folder as they will be postprocessed (changed record_id) later.
        match_folder = f"{match_folder}raw/"

        if not os.path.exists(augment_folder):
            os.makedirs(augment_folder)

        if not os.path.exists(match_folder):
            os.makedirs(match_folder)

        filename_match = match_folder + f"match_{self.batch_size}-{batch_number}.json"
        filename_augment = (
            augment_folder + f"augment_{self.batch_size}-{batch_number}.json"
        )
        status = PDCAJobStatus(
            batch_number, match_schema, augment_schema, filename_match, filename_augment
        )
        status.result = batch
        self.load(status)
        self.push(status)
        logger.debug(f"Job {status.batch_number} created.")

    @staticmethod
    def load(status):
        if os.path.exists(status.filename_match):
            logger.debug(f"Job {status.batch_number} match result found.")
            status.stage = PDCAStage.AUGMENT
            if os.path.exists(status.filename_augment):
                logger.debug(f"Job {status.batch_number} augment result found.")
                status.stage = PDCAStage.FINISHED
            else:
                with open(status.filename_match) as file:
                    status.result = json.load(file)
        else:
            status.stage = PDCAStage.MATCH

    def can_start_initialize(self):
        return can_start(self.simultaneous_batches, self.initialized())

    def can_start_match(self):
        return can_start(self.simultaneous_batches, self.match())

    def can_start_augment(self):
        return can_start(self.simultaneous_batches, self.augment())


def get_folders(output_folder, match_schema, augment_schema):
    match_folder = f"{output_folder}/match_{match_schema}/"
    augment_folder = match_folder + f"augment_{augment_schema}/"

    return match_folder, augment_folder


class PDCAJobStatus:
    def __init__(
        self,
        batch_number,
        schema_match,
        schema_augment,
        filename_match,
        filename_augment,
    ):
        self.batch_number = batch_number

        self.schema_match = schema_match
        self.filename_match = filename_match
        self.location_match = None

        self.schema_augment = schema_augment
        self.filename_augment = filename_augment
        self.location_augment = None

        self.result = {}
        self.stage = PDCAStage.INITIALIZED
        self.processing = False


class PDCACalculations:
    def __init__(
        self,
        client,
        input_file,
        match_schema=1,
        augment_schema=1,
        output_folder="output/",
        batch_size=100,
        simultaneous_batches=5,
        logger_name=None,
        match_params: Dict = None,
    ):
        self.input_file = input_file
        self.file_size = get_file_size(input_file)

        self.match_schema = match_schema
        self.augment_schema = augment_schema

        self.output_folder = output_folder + FOLDER_MATCH

        self.logger = get_logger(logger_name) if logger_name is not None else logger

        self.match_params = match_params

        number_of_batches = math.ceil((self.file_size - 1) / batch_size)
        self.scheduler = PDCACalcScheduler(
            client, batch_size, number_of_batches, simultaneous_batches
        )

        self.initial_message()

    def initial_message(self):
        self.logger.info(
            f"Processing started. "
            f"\n\tInput file: {self.input_file}"
            f"\n\tNumber of batches: {self.scheduler.number_of_batches}"
            f"\n\tOutput location: {self.output_folder}"
            f"\n\tSchema match: {self.match_schema}"
            f"\n\tSchema augment: {self.augment_schema}"
            f"\n\tMatch params: {self.match_params}"
        )

    def show_progress(self, progress):
        if progress is not None:
            match_progress, augment_progress, match_running, augment_running = progress
            self.logger.info(f"Processing.....")
            self.logger.info(
                f"\tMatch: {match_progress:.2f}%, jobs in progress: "
                f"{match_running}/{self.scheduler.simultaneous_batches}"
            )
            self.logger.info(
                f"\tAugment: {augment_progress:.2f}%, jobs in progress: "
                f"{augment_running}/{self.scheduler.simultaneous_batches}"
            )

    def process(self):
        with open(self.input_file, encoding="utf-8") as input_data:
            # Read rows and create batches generator
            rows = list(csv.DictReader(input_data))
            gen = generate_batch(rows, self.scheduler.batch_size)
            for progress in self.scheduler.process(
                gen,
                self.match_schema,
                self.augment_schema,
                self.output_folder,
                self.match_params,
            ):
                self.show_progress(progress)
        self.show_progress(self.scheduler.get_progress())
        return self.output_folder

    def unique_duns(self):
        match_folder, augment_folder = get_folders(
            self.output_folder, self.match_schema, self.augment_schema
        )

        duns_match = set()
        duns_augment = set()

        for file in os.listdir(match_folder):
            path = os.path.join(match_folder, file)
            if os.path.isdir(path):
                continue
            with open(path) as f:
                result_match = json.load(f)
                duns_match.update({d["dunsnumber"] for d in result_match["masterData"]})

        for file in os.listdir(augment_folder):
            path = os.path.join(augment_folder, file)
            if os.path.isdir(path):
                continue
            with open(path) as f:
                result_augment = json.load(f)
                duns_augment.update(
                    {d["dunsnumber"] for d in result_augment["masterData"]}
                )

        return duns_match, duns_augment

    def merge(self, filename, columns=None):
        match_folder, augment_folder = get_folders(
            self.output_folder, self.match_schema, self.augment_schema
        )

        data = defaultdict(lambda: defaultdict(lambda: ""))

        for file in os.listdir(match_folder):
            path = os.path.join(match_folder, file)
            if os.path.isdir(path):
                continue
            with open(path) as f:
                result_match = json.load(f)
                data.update({d["dunsnumber"]: d for d in result_match["masterData"]})

        for file in os.listdir(augment_folder):
            path = os.path.join(augment_folder, file)
            if os.path.isdir(path):
                continue
            with open(path) as f:
                result_augment = json.load(f)
                for d in result_augment["masterData"]:
                    data[d["dunsnumber"]].update(d)

        if columns is None:
            columns = set().union(*(d.keys() for d in data.values()))

        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for data in data.values():
                writer.writerow(data)
