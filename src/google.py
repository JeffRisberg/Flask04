import json
import os
from datetime import datetime
from typing import List
from urllib.parse import urlencode
from flask import current_app

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tzlocal import get_localzone_name

# CLIENT_ID = '392712472664-gkqit9s9lent7621op0povgs4junkjae.apps.googleusercontent.com'
# CLIENT_SECRET = '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'
ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
REDIRECT_URI = current_app.config.get("base_url", "http://localhost:5000")


def get_google_token(code: str):
	CLIENT_ID = current_app.config['GOOGLE_CLIENT_ID']
	CLIENT_SECRET = current_app.config['GOOGLE_CLIENT_SECRET']

	access_token_req = {
		"code": code,
		"client_id": CLIENT_ID,
		"client_secret": CLIENT_SECRET,
		"redirect_uri": REDIRECT_URI,
		"grant_type": "authorization_code"
	}
	content_length = len(urlencode(access_token_req))
	access_token_req['content-length'] = str(content_length)
	response = requests.post(ACCESS_TOKEN_URI, data=access_token_req)

	credential = json.loads(response.text)
	return credential


def get_google_credential(access_token: str, refresh_token: str):
	if not access_token:
		return False

	CLIENT_ID = current_app.config['GOOGLE_CLIENT_ID']
	CLIENT_SECRET = current_app.config['GOOGLE_CLIENT_SECRET']

	credentials = Credentials(
		access_token,
		token_uri=ACCESS_TOKEN_URI,
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		refresh_token=refresh_token
	)
	return credentials


def get_google_profile(google_access_token: str):
	print("get google profile")
	url = f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
	x = requests.get(url, headers={"Authorization": "Bearer " + google_access_token})
	profile_info = json.loads(x.text)
	return profile_info


def get_google_calendar_event_colors(credentials: Credentials):
	service = build('calendar', 'v3', credentials=credentials)
	colors = service.colors().get().execute()
	result = []
	for id, color in colors['event'].items():
		result.append({
			id: color["background"]
		})

	return result


def get_google_calendar_color(credentials: Credentials, color_id: str):
	service = build('calendar', 'v3', credentials=credentials)
	colors = service.colors().get().execute()
	result = []
	for id, color in colors['event'].items():
		if id == color_id:
			return color["background"]

	return result


def get_google_calendar_events(credentials: Credentials, start_time: datetime, end_time: datetime) -> List:
	print("get calendar events")
	start = start_time.isoformat() + 'Z'
	end = end_time.isoformat() + 'Z'

	page_token = None
	service = build('calendar', 'v3', credentials=credentials)
	results = []

	while True:
		events = service.events().list(
			calendarId='primary',
			timeMin=start,
			timeMax=end,
			singleEvents=True,
			orderBy='startTime',
			pageToken=page_token
		).execute()

		results += events.get('items', [])

		page_token = events.get('nextPageToken')
		if not page_token:
			break

	return results


def add_google_calendar_event(credentials: Credentials, title: str, start_time: datetime, end_time: datetime):
	print("add google calendar event")

	timezone_name = get_localzone_name()

	google_event = {
		'summary': title,
		'start': {
			'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
			'timeZone': timezone_name,
		},
		'end': {
			'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
			'timeZone': timezone_name,
		},
		'recurrence': [
		],
		'attendees': [],
		'reminders': {
			'useDefault': True,
		},
	}

	if credentials:
		service = build('calendar', 'v3', credentials=credentials)

		try:
			event = service.events().insert(calendarId='primary', body=google_event).execute()
			return event['id']
		except Exception as e:
			print(e)


def update_google_calendar_event(credentials: Credentials, event_id: str, title: str, start_time: datetime, end_time: datetime):
	print("update google calendar event")

	timezone_name = 'UTC'

	if credentials:
		service = build('calendar', 'v3', credentials=credentials)

		try:
			event = service.events().get(calendarId='primary', eventId=event_id.split('_')[0]).execute()

			if event:
				event["summary"] = title,
				event['start'] = {
					'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
					'timeZone': timezone_name,
				}
				event['end'] = {
					'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
					'timeZone': timezone_name,
				}

				service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
		except Exception as e:
			print(e)
