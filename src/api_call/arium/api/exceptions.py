import json

from config.get_logger import get_logger

logger = get_logger(__name__)


class AriumAPACException(Exception):
    def __init__(self, response):
        self.response = response


def handle_exception(e):
    status_code = e.response.status_code
    reason = e.response.reason if e.response.reason else 'unknown'

    try:
        content = json.loads(e.response.content)
        content_message = content.get('message', content.get('error', content.get('errors', content)))
        content_details = content.get('details', None)
    except json.decoder.JSONDecodeError:
        content_message = e.response.content
        content_details = None

    message = f"Exception occurred: {reason} - {status_code} - {content_message}"

    if content_details:
        message += f" - {content_details}"

    logger.exception(message)


def exception_handler(fun):
    def wrapper(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except AriumAPACException as e:
            handle_exception(e)
            raise Exception from None
        except Exception as e:
            logger.exception(f"Exception occurred: {e}")
            raise Exception from None

    return wrapper
