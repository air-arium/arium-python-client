import unittest

import pandas as pd

from api_call.arium.pdca_data_processing.merge import merge_pdca_result
from api_call.arium.pdca_data_processing.merge import transform_company_into_naics_rows


class MyTestCase(unittest.TestCase):
    def test_create_naics_and_merge_subs(self):
        """
        This tests function create_naics_and_merge_subs which name is misleading.
        In reality it doesn't merge anything, it's multiplies the output based on
        columns industrycode1-6. If any value is provided in these columns, it should
        create row in the output structure.
        e.g
        input data: { __company_id: 1, duns: 1, industrycode1: 1, industrycode2: 2, industrycode3: "",  industrycode4: ""..}
        result:  { __company_id: 1, duns 1, industrycode1: 1}
                 { __company_id: 1, duns 1, industrycode2:2}
        There is no row for industrycode3,4,5,6 as their value is empty

        Main key in output structure is __company_id and duns
        """
        DUNS_HQ = 100
        DUNS_SUB_1 = 123
        COMPANY_ID = 555

        # given
        data: pd.DataFrame = pd.json_normalize(
            [
                {
                    "original_duns": DUNS_HQ,
                    "duns": DUNS_SUB_1,
                    "companyName": "SUB1 - HOLLINGSWORTH & VOSE (INDIA) PRIVATE LIMITED",
                    "industrycode1": 334416,
                    "industrycode2": 335314,
                    "industrycode3": "",
                    "industrycode4": "",
                    "industrycode5": "",
                    "industrycode6": "",
                    "record_id": 1,
                    "sequence_id": 1,
                    "confidence": 8,
                    "matchgrade": "AZZZZZZ",
                    "duns_match": 100,
                    "__company_id": COMPANY_ID,
                },
                {
                    "original_duns": DUNS_HQ,
                    "duns": DUNS_HQ,
                    "companyName": "HQ - HOLLINGSWORTH & VOSE COMPANY",
                    "industrycode1": 322121,
                    "industrycode2": 339991,
                    "industrycode3": 313230,
                    "industrycode4": 321999,
                    "industrycode5": "",
                    "industrycode6": "",
                    "record_id": 1,
                    "sequence_id": 1,
                    "confidence": 8,
                    "matchgrade": "AZZZZZZ",
                    "duns_match": 100,
                    "__company_id": COMPANY_ID,
                },
            ]
        )
        ref_data_folder = "../examples/pdca/data/refdata/"
        errors = []

        # when
        result: pd.DataFrame = transform_company_into_naics_rows(
            pdca_result=data, ref_data_folder=ref_data_folder, errors=errors
        )

        # then
        self.assertEqual(
            6, len(result), "Merge result should have 6 rows: 4 for HQ, 2 for Sub1"
        )
        sub_industry_codes_rows: pd.DataFrame = result[
            (result["__company_id"] == COMPANY_ID) & (result["duns"] == DUNS_SUB_1)
        ]
        self.assertEqual(
            2,
            len(sub_industry_codes_rows),
            "Sub should have 2 rows - 1 for each naics->industrycode",
        )
        hq_industry_codes_rows: pd.DataFrame = result[
            (result["__company_id"] == COMPANY_ID) & (result["duns"] == DUNS_HQ)
        ]
        self.assertEqual(
            4,
            len(hq_industry_codes_rows),
            "HQ should have 2 rows - 1 for each naics->industrycode",
        )

    def test_merge_conglomerate(self):
        """
        Given:
        api_input_df - 1 record was provided as input to match process. It has properties:
          - '__company_id' which joins it with companies in input data (input policies).
          - 'record_id' which joins it with input csv data (input policies) - it's just line number in this file
        match_df - 1 record was returned. it's 'connected' to api_input with property 'record_id'
        augment_df - 2 records was returned from data augmentation process:
          - HQ. It might be recognized because of duns == original_duns
          - 1 subsidiary
        System should merge the data so eventually there are 2 records: 1 for HQ and 1 for sub.
        They both should have column '__company_id' pointing the the same value and 'record_id'
        also set to same value
        """
        # given
        RECORD_ID = 1
        DUNS_HQ = 100
        DUNS_SUB_1 = 123
        COMPANY_ID = 555
        match_df = pd.json_normalize(
            [
                {
                    "record_id": RECORD_ID,
                    "sequence_id": 1,
                    "confidence": 8,
                    "matchgrade": "AZZZZZZ",
                    "duns": DUNS_HQ,
                    "companyName": "HQ - HOLLINGSWORTH & VOSE COMPANY",
                }
            ]
        )

        augment_df = pd.json_normalize(
            [
                {
                    "original_duns": DUNS_HQ,
                    "duns": DUNS_SUB_1,
                    "companyName": "SUB1 - HOLLINGSWORTH & VOSE (INDIA) PRIVATE LIMITED",
                    "naic1": 334416,
                    "naic2": 335314,
                    "naic3": "",
                    "naic4": "",
                    "naic5": "",
                    "naic6": "",
                },
                {
                    "original_duns": DUNS_HQ,
                    "duns": DUNS_HQ,
                    "companyName": "HQ - HOLLINGSWORTH & VOSE COMPANY",
                    "naic1": 322121,
                    "naic2": 339991,
                    "naic3": 313230,
                    "naic4": 321999,
                    "naic5": "",
                    "naic6": "",
                },
            ]
        )

        api_input_df = pd.json_normalize(
            [
                {
                    "__company_id": COMPANY_ID,
                    "companyName": "HOLLINGSWORTH & VOSE COMPANY",
                    "record_id": RECORD_ID,
                }
            ]
        )
        # when
        mresult: pd.DataFrame = merge_pdca_result(match_df, augment_df, api_input_df)

        # then
        self.assertEqual(
            2, len(mresult), "Merge result should have 2 rows: 1 for HQ, 1 for Sub1"
        )

        self.assertEqual(
            1,
            len(
                mresult[
                    (mresult["__company_id"] == COMPANY_ID)
                    & (mresult["duns"] == DUNS_HQ)
                    & (mresult["record_id"] == RECORD_ID)
                ]
            ),
            "There should be HQ row with COMPANY_ID, DUNS_HQ and RECORD_ID",
        )

        self.assertEqual(
            1,
            len(
                mresult[
                    (mresult["__company_id"] == COMPANY_ID)
                    & (mresult["duns"] == DUNS_SUB_1)
                    & (mresult["record_id"] == RECORD_ID)
                ]
            ),
            "There should be Sub1 row with COMPANY_ID, DUNS_SUB_1 and RECORD_ID",
        )


if __name__ == "__main__":
    unittest.main()
