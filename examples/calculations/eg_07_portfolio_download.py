import json

from api_call.client import APIClient
from auth.okta_auth import Auth

request = [
    {
        "scenario": {
            "tab": 1,
            "linkSetId": 1,
            "linkMode": 1,
            "portfolio": {
                "enabled": True,
                "ref": "",
            },
            "selectedNodeId": "4",
            "multiSelectedNodeId": [],
            "mapExpandedNaics": [],
            "buildExpandedNaics": [],
            "filters": [
                {
                    "type": 4,
                    "key": "link",
                    "mapping": "vro",
                    "domainBounds": [0, 1],
                    "domain": [0.03, 1],
                    "domainStep": 0.001,
                    "formatType": "percent",
                },
                {"type": 2, "key": None, "id": "FU"},
                {"type": 2, "key": None, "id": "F06"},
                {"type": 2, "key": None, "id": "F067"},
                {"type": 2, "key": None, "id": "F0700"},
                {"type": 2, "key": None, "id": "F07E00"},
                {"type": 2, "key": None, "id": "F07S00"},
                {"type": 2, "key": None, "id": "F07N00"},
                {"type": 2, "key": None, "id": "F0600"},
                {"type": 2, "key": None, "id": "F06N00"},
                {"type": 2, "key": None, "id": "F06S00"},
                {"type": 2, "key": None, "id": "F06E00"},
                {"type": 2, "key": None, "id": "F1000"},
                {"type": 2, "key": None, "id": "F10S00"},
                {"type": 2, "key": None, "id": "F10E00"},
                {"type": 2, "key": None, "id": "F10N00"},
                {"type": 2, "key": None, "id": "F12"},
                {"type": 2, "key": None, "id": "F120"},
                {"type": 2, "key": None, "id": "F1200"},
                {"type": 2, "key": None, "id": "F01000"},
                {"type": 2, "key": None, "id": "F02R00"},
                {"type": 2, "key": None, "id": "F23"},
                {"type": 2, "key": None, "id": "F230"},
                {"type": 2, "key": None, "id": "F2300"},
                {"type": 2, "key": None, "id": "F02S00"},
                {"type": 2, "key": None, "id": "F02N00"},
                {"type": 2, "key": None, "id": "F03000"},
                {"type": 2, "key": None, "id": "F02E00"},
                {"type": 2, "key": None, "id": "F45"},
                {"type": 2, "key": None, "id": "F450"},
                {"type": 2, "key": None, "id": "F4500"},
                {"type": 2, "key": None, "id": "F04000"},
                {"type": 2, "key": None, "id": "F05000"},
                {"type": 2, "key": None, "id": "FC6"},
                {"type": 2, "key": None, "id": "FC67"},
                {"type": 2, "key": None, "id": "FC670"},
                {"type": 2, "key": None, "id": "F06C00"},
                {"type": 2, "key": None, "id": "F07C00"},
                {"type": 2, "key": None, "id": "F10C00"},
            ],
            "portfolioFilters": [],
            "scenarioFilters": [],
            "buildModel": {},
            "settings": {
                "defenseCosts": {},
                "nodes": {},
                "eco": {"range": [0, 10000000000], "value": 0},
                "noneco": {"range": [0, 10000000000], "value": 0},
                "proRateCulpableAccounts": 1,
                "multiYear": {
                    "activated": False,
                    "calendarYear": [
                        {"year": 1999, "value": 10},
                        {"year": 2000, "value": 90},
                    ],
                    "accountYear": [
                        {"year": 1991, "value": 10},
                        {"year": 1992, "value": 10},
                        {"year": 1993, "value": 20},
                        {"year": 1994, "value": 60},
                    ],
                },
            },
        },
        "metrics": [
            "scenario.total_exposure",
            "scenario.premium",
            "scenario.number_of_policies",
            "node.total_exposure",
            "node.premium",
            "node.number_of_policies",
            "node.number_of_accounts",
        ],
        "reinsurances": [],
        "contracts": [],
        "currency": [{"code": "usd", "rate": 1}],
        "labelType": None,
    }
]

a = json.dumps(request)

prefix = ""
settings = {}

# Create new client
auth = Auth(
    tenant="workspace1",
    role="basic",
    settings=settings,
    prefix=prefix,
    verify=False,
)
client = APIClient(auth=auth)

rows = client.calculations().portfolio_download(request)
for row in rows:
    print(row)
