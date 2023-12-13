import unittest
import api_call.arium.pdca_data_processing.batch_records_updater as updater
import json
import copy
from unittest.mock import patch, MagicMock


class MergeTestCase(unittest.TestCase):
    # Nothing should change for the first batch which has index 0
    def test_update_data_first_batch(self):
        # given
        batch_index = 0
        data = {
            "masterData": [
                {
                    "record_id": 1,
                    "sequence_id": 10,
                    "businessname": "ALFA",
                },
                {
                    "record_id": 2,
                    "sequence_id": 20,
                    "businessname": "BETA",
                },
            ]
        }
        data1 = copy.deepcopy(data)
        # when
        updater.update_data(batch_index, 100, data)
        # then, let's see if nothing has really changed
        a, b = json.dumps(data1, sort_keys=True), json.dumps(data, sort_keys=True)
        assert a == b

    def test_update_data_not_first_batch(self):
        # Record id should be updated: increased by batch_index * batch size
        # given
        batch_index = 3
        batch_size = 100
        data = {
            "masterData": [
                {
                    "record_id": 1,
                    "sequence_id": 10,
                    "businessname": "ALFA",
                },
                {
                    "record_id": 2,
                    "sequence_id": 20,
                    "businessname": "BETA",
                },
            ]
        }

        expect = {
            "masterData": [
                {
                    "record_id": 1 + batch_index * batch_size,
                    "sequence_id": 10,
                    "businessname": "ALFA",
                },
                {
                    "record_id": 2 + batch_index * batch_size,
                    "sequence_id": 20,
                    "businessname": "BETA",
                },
            ]
        }

        # when
        updater.update_data(batch_index, 100, data)

        # then
        a, b = json.dumps(data, sort_keys=True), json.dumps(expect, sort_keys=True)
        assert a == b

    @patch("api_call.arium.pdca_data_processing.batch_records_updater.update_data")
    @patch(
        "api_call.arium.pdca_data_processing.batch_records_updater.save_json_to_file"
    )
    @patch(
        "api_call.arium.pdca_data_processing.batch_records_updater.load_json_from_file"
    )
    @patch(
        "api_call.arium.pdca_data_processing.batch_records_updater.list_files_in_folder"
    )
    def test_update_batch_record_ids(
        self, list_files_mock, load_json_mock, save_json_to_file_mock, update_data_mock
    ):
        list_files_mock.return_value = ["match_2-1.json", "match_2-2.json"]
        updater.update_batch_record_ids("/portfolio/", "1", 1)

        self.assertEqual(
            save_json_to_file_mock.call_count,
            2,
            "Amount of calls for save_json_to_file",
        )

        call1: MagicMock = save_json_to_file_mock.mock_calls[0]

        self.assertEqual("/portfolio/match/match_1/match_2-1.json", call1.args[1])

        call2 = save_json_to_file_mock.mock_calls[1]
        self.assertEqual("/portfolio/match/match_1/match_2-2.json", call2.args[1])
