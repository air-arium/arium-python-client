import time
from datetime import datetime, timedelta
from enum import Enum
from io import BytesIO
from types import MethodType
from typing import List

import requests

from api_call.arium.api.request import get_content
from api_call.arium.model.activity import ActivityList, Activity, ActivitySubmitRequest, ActivityStatus, Report
from config.get_logger import get_logger

logger = get_logger(__name__)


class Order(Enum):
    Ascending = 1
    Descending = -1


class Sort(Enum):
    StartTime = "startTime"


class ReportsClient:

    def __init__(self, client: "APIClient", activity_id: str):
        self._client = client
        self._activity_id = activity_id

    def list(self) -> List[Report]:
        endpoint = f"/{{tenant}}/calculations/assets/{self._activity_id}/reports"
        response = self._client.get_request(endpoint=endpoint)
        content = get_content(response=response, get_from_location=False)
        # Convert each item to Report
        reports = []

        for item in content:
            report = Report.from_dict(item)
            report._fetch = MethodType(self.fetch, report.file)
            reports.append(report)
        return reports

    def fetch(self, file_name: str) -> BytesIO:
        endpoint = f"/{{tenant}}/calculations/assets/{self._activity_id}/reports/{file_name}"
        response = self._client.get_request(endpoint=endpoint)
        content = get_content(response=response, get_from_location=False)

        link = content.get("link")
        link_response = requests.get(link, allow_redirects=True)
        return BytesIO(link_response.content)


class ActivityClient:
    def __init__(self, client: "APIClient"):
        self._client = client

    def list(self,
             limit: int = 100,
             page: int = 1,
             order: Order = Order.Descending,
             sort: Sort = Sort.StartTime
             ) -> ActivityList:
        endpoint = f"/{{tenant}}/activity?limit={limit}&page={page}&order={order.value}&sort={sort.value}"
        response = self._client.get_request(endpoint=endpoint)
        content: dict = get_content(response=response, get_from_location=False)
        activity_list = ActivityList.from_dict(content)
        for activity in activity_list.list:
            reports_client = ReportsClient(self._client, activity.activityId)
            activity._fetch_reports = reports_client.list
        return activity_list

    def submit(self, activity_submit_request: ActivitySubmitRequest, wait: bool = False,
               timeout_minutes: int = 60) -> Activity:
        endpoint = f"/{{tenant}}/activity"
        data = activity_submit_request.to_dict()
        print(data)
        response = self._client.post_request(endpoint=endpoint, json=data)
        content: dict = get_content(response=response, get_from_location=False)

        if not (activity_id := content.get("data", {}).get("activityId")):
            raise ValueError("Activity ID is not returned. Response is missing 'activityId' field.")

        if not wait:
            return self.get(activity_id=activity_id)

        return self.wait(activity_id=activity_id, timeout_minutes=timeout_minutes)

    def wait(self, activity_id: str, timeout_minutes: int = 60) -> Activity:
        get_logger().info(f"Waiting for activity completion, start time: {datetime.now()}")
        startTime = datetime.now()

        timeout_limit = datetime.now() + timedelta(minutes=timeout_minutes)
        while True:
            if datetime.now() > timeout_limit:
                raise TimeoutError(f"Activity polling timed out after {timeout_minutes} minutes")

            activity = self.get(activity_id=activity_id)

            activity_status = activity.status

            if not isinstance(activity_status, ActivityStatus):
                activity_status = ActivityStatus(activity_status)

            match activity_status:
                case ActivityStatus.FAILED:
                    return activity
                case ActivityStatus.CANCELED:
                    return activity
                case ActivityStatus.COMPLETED:
                    return activity
                case _:
                    # Continue polling for other statuses (QUEUED, RUNNING, etc.)
                    time.sleep(15)
                    elapsed = datetime.now() - startTime
                    elapsed_str = str(elapsed).split(".", 1)[0]  # HH:MM:SS
                    get_logger().info(f"Activity status: {activity_status}, time elapsed: {elapsed_str}. Sleeping for 15 seconds.")

    def get(self, activity_id: str) -> Activity:
        endpoint = f"/{{tenant}}/activity/{activity_id}"
        response = self._client.get_request(endpoint=endpoint, retry=1)
        content = get_content(response=response, get_from_location=False)
        activity = Activity.from_dict(content)
        reports_client = ReportsClient(self._client, activity.activityId)
        activity._fetch_reports = reports_client.list
        return activity

    def cancel(self, activity_id: str) -> str:
        endpoint = f"/{{tenant}}/activity/{activity_id}/cancel"
        response = self._client.post_request(endpoint=endpoint)
        if not response.status_code == 200:
            raise Exception(f"Activity cancel failed with status: {response.status_code}")

    def reports(self, activity_id: str) -> List[Report]:
        return ReportsClient(self._client, activity_id=activity_id).list()

    def report(self, activity_id: str) -> Report | None:
        reports = self.reports(activity_id=activity_id)
        if len(reports) > 0:
            return reports[0]
        return None

    def resubmit(self, activity_id: str) -> str:
        endpoint = f"/{{tenant}}/activity/{activity_id}/resubmit"
        response = self._client.post_request(endpoint=endpoint)
        if not response.status_code == 200:
            raise Exception(f"Activity cancel failed with status: {response.status_code}")

        response_body = get_content(response=response, get_from_location=False)
        return response_body.get("data", {}).get("activityId")
