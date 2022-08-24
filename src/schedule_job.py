from datetime import datetime, timedelta

from src import database
from src.google import get_google_calendar_events, get_google_calendar_color, get_google_credential


def sync_google_calendar():
	users = database.get_users_with_google_token()
	for user in users:
		user_id = user["id"]
		credentials = get_google_credential(user["google_access_token"], user["google_refresh_token"])
		if credentials.expired:
			credentials.refresh()
		today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		start_date = today - timedelta(hours=9)
		end_date = today + timedelta(days=7, hours=9)

		results = get_google_calendar_events(credentials, start_date, end_date)

		checked_events = []

		for result in results:
			event_external_id = result["id"]
			start = result['start']
			end = result['end']

			start_time = None
			end_time = None
			if start.get('dateTime', None) != None:
				start_time = datetime.strptime(start["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
				end_time = datetime.strptime(end["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
			if start.get('date', None) != None:
				start_time = datetime.strptime(start["date"], "%Y-%m-%d")
				end_time = datetime.strptime(end["date"], "%Y-%m-%d")

			if start_time == None or end_time == None:
				continue

			if "summary" in result:
				title = result["summary"]
			else:
				title = '(No Title)'

			if "colorId" in result:
				color = get_google_calendar_color(credentials, result["colorId"])
			else:
				color = "#4285f4"

			event = {
				"user_id": user[0]["id"],
				"title": title,
				"start_time": start_time,
				"end_time": end_time,
				"color": color,
				"source": "google",
				"event_external_id": result["id"]
			}

			checked_events.append(result["id"])

			events = database.get_event_by_external_id(event_external_id)

			if len(events) == 0:
				database.add_event(event)

			if len(events) > 0 and (
				event['title'] != events[0]['title'] or
				event['start_time'].timestamp() != events[0]['start_time'].timestamp() or
				event['end_time'].timestamp() != events[0]['end_time'].timestamp() or
				event['color'] != events[0]['color']
			):
				database.delete_event_by_external_id(event_external_id)
				database.add_event(event)

		database.remove_unchecked_events(user_id, checked_events, start_date, end_date, "google")
