COLLECTION_PORTFOLIOS = "portfolios"
COLLECTION_PROGRAMMES = "programmes"
COLLECTION_CURRENCY_TABLES = "currencyTables"
COLLECTION_LAS = "lossallocation"
COLLECTION_SCENARIOS = "scenarios"
COLLECTION_SIZES = "sizes"

ENDPOINT_PORTFOLIO_UPLOADS = "portfolio_uploads"
ENDPOINT_CALC_LA = "calculations/la"
ENDPOINT_PERTURBATIONS = "calculations/perturbations"
ENDPOINT_CALC_LA_EXPORT = "calculations/la-export"
ENDPOINT_PORTFOLIO_DOWNLOAD = "calculations/portfoliodownload/{portfolio}"
ENDPOINT_DICTIONARY = "dictionary"
ENDPOINT_NODE_METRICS = "nodemetrics"
ENDPOINT_CALC_NODE_METRICS = "calculations/nodemetrics/{portfolio}"
ENDPOINT_CALC_LA_PARAMETERS = "calculations/laparams/{portfolio}"
ENDPOINT_PROPERTIES = "properties"
ENDPOINT_CALC_CONNECTED_NODES = "calculations/connectednodes/{portfolio}"
ENDPOINT_CALC_EXPOSURES = "calculations/exposures/"
ENDPOINT_PROGRAMMES = "programmes"

PORT = "port"
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
AUTHORIZATION_URL = "authorization_url"
TOKEN_URL = "token_url"
BASE_URI = "base_uri"
REDIRECT_URI = "redirect_uri"

CONNECTIONS_FILE_TEMPLATE = "connections-{}.json"

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'api_call': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'auth': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
ACCOUNT_NAME = 'accountname'
ACCOUNT_NUMBER = 'accountnumber'
HEADOFFICE_NAME = 'headofficename'
HEADOFFICE_NUMBER = 'headofficenumber'
POLICY_NAME = 'policyname'
POLICY_NUMBER = 'policynumber'
INSURER = 'insurername'
POLICY_TYPE = 'policytype'
CITY = 'city'
STATE = 'state'
COUNTY = 'county'
COUNTRY = 'country'
JURISDICTION = 'jurisdiction'
REINSURANCE_PROGRAMME = 'programme'
INCEPTION_DATE = 'inceptiondate'
EXPIRATION_DATE = 'expirationdate'
POSTAL_CODE = 'postalCode'
PAYROLL = 'payroll'
TURNOVER = 'turnover'
EMPLOYEE_COUNT = 'employeecount'
PER_OCCURENCE_LIMIT = 'limit'
AGGREGATE_LIMIT = 'agglimit'
PREMIUM = 'premium'
ATTACHMENT_POINT = 'attachmentpointexcesspoint'
TRIGGER_TYPE = 'typeofcover'
