import datetime
import os.path

from pytz import timezone
from typing import List, Union

from dateutil.parser import parse
import dateutil.parser as dt

from tzlocal import get_localzone_name

from flask import current_app, redirect, url_for, flash
from flask import request, session, jsonify, send_from_directory
from flask_cors import cross_origin
from sendgrid import Mail
from sendgrid.helpers import mail
from ua_parser import user_agent_parser
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from src import mail as mail_service

from . import database
from .coach import Coach
from .coach_state import stateResponse

from .google import get_google_token, get_google_profile, get_google_credential, get_google_calendar_events, \
	get_google_calendar_color, add_google_calendar_event, get_google_calendar_event_colors, update_google_calendar_event
from .template.email import get_password_reset_email_template


def log_request(request, user_id, type, question, response):
	ip_address = request.remote_addr
	parsed_user_agent_info = user_agent_parser.Parse(request.user_agent.string)
	user_agent = parsed_user_agent_info['user_agent']
	device_type = parsed_user_agent_info['device']
	device_type = str(device_type['family'] or '') + ":" + str(device_type['brand'] or '') + ":" + \
				  str(device_type['model'] or '') + ":" + str(user_agent['family'] or '')
	session_id = request.cookies.get('session')
	database.save_conversation(
		{
			'user_id': user_id,
			'session_id': session_id,
			'type': type,
			'question': question,
			'response': response,
			'ip_address': ip_address,
			'device_type': device_type,
		}
	)


def create_email(
	subject: str,
	to_emails: List[Union[str, mail.To]],
	html_content: str,
	*,
	from_email: Union[str, mail.From] = None,
) -> Mail:
	from_email = from_email or mail.From(
		email=current_app.config["sendgrid_sender_email"],
		name=current_app.config["sendgrid_sender_name"],
	)
	message = Mail(
		from_email=from_email,
		to_emails=to_emails,
		subject=subject,
		html_content=html_content,
	)
	message.tracking_settings = mail.TrackingSettings(click_tracking=mail.ClickTracking(enable=False))

	message.reply_to = mail.ReplyTo(
		email=current_app.config["sendgrid_sender_email"],
		name=current_app.config["sendgrid_sender_name"],
	)
	return message


def _sync_google_event(credentials, user_id):
	source = 'google'
	try:
		user = database.get_user_by_id(user_id)
		today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		start_date = today - datetime.timedelta(hours=9)
		end_date = today + datetime.timedelta(days=30, hours=9)

		results = get_google_calendar_events(credentials, start_date, end_date)
		event_colors = get_google_calendar_event_colors(credentials)

		checked_events = []

		for result in results:
			event_external_id = result["id"]
			start = result['start']
			end = result['end']

			start_time = None
			end_time = None
			if start.get('dateTime', None) != None:
				start_time = datetime.datetime.strptime(start["dateTime"], "%Y-%m-%dT%H:%M:%S%z").astimezone(
					timezone("UTC")
				)
				end_time = datetime.datetime.strptime(end["dateTime"], "%Y-%m-%dT%H:%M:%S%z").astimezone(
					timezone("UTC")
				)
			if start.get('date', None) != None:
				start_time = datetime.datetime.strptime(start["date"], "%Y-%m-%d")
				end_time = datetime.datetime.strptime(end["date"], "%Y-%m-%d")

			if start_time == None or end_time == None:
				continue

			if "summary" in result:
				title = result["summary"]
			else:
				title = '(No Title)'

			if "colorId" in result and result["colorId"] in event_colors:
				color = event_colors[result["colorId"]]
			else:
				color = "#4285f4"

			event = {
				"user_id": user[0]["id"],
				"title": title,
				"start_time": start_time,
				"end_time": end_time,
				"color": color,
				"source": source,
				"event_external_id": result["id"],
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

		database.remove_unchecked_events(user_id, checked_events, start_date, end_date, source)

	except BaseException as err:
		print(f"Unexpected {err=}, {type(err)=}")

@current_app.route('/inquiry', methods=['POST'])
@cross_origin()
def inquiry():
	inquiry = request.args['inquiry'].strip()

	if session.get('coach'):
		coach = session['coach']
		response = coach.respond(inquiry)
		log_request(request, coach.user_id, 'inquiry', coach.prior_question, inquiry)
		coach.prior_question = response['text']
		return jsonify(response)
	else:
		print('invalid session - no Coach object')
		return jsonify('')


@current_app.route("/api/companies")
def api_companies():
	response = database.get_companies()
	return jsonify(response)


@current_app.route("/api/teams")
def api_teams():
	args = request.args
	name = args.get('name')
	if name is not None:
		response = database.get_team_by_name(name)
	else:
		response = database.get_teams()
	return jsonify(response)


@current_app.route("/api/teams/<int:team_id>")
def api_teams_by_id(team_id):
	response = database.get_team_by_id(team_id)
	return jsonify(response)


@current_app.route("/api/jobs/<int:company_id>")
@cross_origin()
def api_jobs(company_id):
	response = database.get_jobs(company_id)
	return jsonify(response)


@current_app.route("/api/users")
@cross_origin()
def api_users():
	args = request.args
	email = args.get('email')
	if email is not None:
		response = database.get_user_by_email(email)
	else:
		response = database.get_users()
	return jsonify(response)


@current_app.route("/api/users/<int:user_id>")
@cross_origin()
def api_user_by_id(user_id):
	response = database.get_user_by_id(user_id)
	return jsonify(response)


@current_app.route("/api/users", methods=['PUT'])
@cross_origin()
def api_update_user():
	content = request.json
	response = database.update_user(content)
	return jsonify(response)


@current_app.route("/api/users", methods=['POST'])
@cross_origin()
def api_create_user():
	content = request.json
	response = database.create_user(content)
	return jsonify(response)


@current_app.route("/api/top_goals/<int:user_id>")
def api_get_top_goals(user_id):
	goals = database.get_top_goals(user_id, request)
	return jsonify(goals)


@current_app.route("/api/top_goals", methods=['PUT'])
@cross_origin()
def api_update_top_goal():
	content = request.json
	response = database.update_top_goal(content)
	return jsonify(response)


@current_app.route("/api/weekly_tasks/<int:user_id>")
def api_weekly_tasks(user_id):
	response = database.get_weekly_tasks(user_id, request)
	return jsonify(response)


@current_app.route("/api/daily_tasks/<int:user_id>")
def api_daily_tasks(user_id):
	response = database.get_daily_tasks(user_id, request)
	return jsonify(response)


@current_app.route("/api/monthly_goals/<int:user_id>")
def api_get_monthly_goals(user_id):
	monthly_goals = database.get_monthly_goals(user_id, request)
	return jsonify(monthly_goals)


@current_app.route("/api/yearly_goals/<int:user_id>")
def api_get_yearly_goals(user_id):
	try:
		yearly_goals = database.get_yearly_goals(user_id, request)
		return jsonify(yearly_goals)
	except Exception as e:
		print(e)


@current_app.route("/api/daily_tasks_summary/<int:user_id>")
def api_daily_tasks_summary(user_id):
	response = database.get_tasks_daily_summary(user_id, request)
	return jsonify(response)


@current_app.route("/api/weekly_tasks_summary/<int:user_id>")
def api_weeklytasks_summary(user_id):
	response = database.get_tasks_weekly_summary(user_id, request)
	return jsonify(response)


@current_app.route("/api/tasks", methods=['PUT'])
def api_update_task():
	content = request.json

	response = database.update_task(content)
	if session.get('coach'):
		coach = session['coach']
		coach.find_task_ids(coach.user_id)
	return jsonify(response)


@current_app.route("/api/tasks/<int:task_id>", methods=['DELETE'])
def api_delete_task(task_id):
	args = request.args
	table_name = args['table']

	response = database.delete_task(task_id, table_name)
	if session.get('coach'):
		coach = session['coach']
		coach.find_task_ids(coach.user_id)
	return jsonify(response)


@current_app.route("/api/daily_tasks/<int:user_id>", methods=['POST'])
def api_add_today_task(user_id):
	content = request.json
	response = database.add_task(user_id, content["name"], 1, "daily_tasks", content["date"])
	return jsonify(response)


@current_app.route("/api/events/<int:user_id>", methods=['POST', 'GET'])
def api_events(user_id):
	if request.method == 'GET':
		response = database.get_events(user_id)
		return jsonify(response)
	else:
		content = request.json
		if "start" not in content:
			now = datetime.datetime.utcnow()
			local_timezone = get_localzone_name()
			start_time = now.replace(minute=0, second=0, microsecond=0)
			end_time = start_time + datetime.timedelta(hours=1)
		else:
			start_time = dt.parse(content["start"])
			end_time = dt.parse(content["end"])

		event = {
			"user_id": user_id,
			"title": content['title'],
			"start_time": start_time,
			"end_time": end_time,
			"color": "#308446",

		}

		event_id = database.add_event(event)

		if "token" in session:
			credentials = session['token']

			event_external_id = add_google_calendar_event(credentials, event["title"], start_time, end_time)

			event_data = {
				"id": event_id,
				"event_external_id": event_external_id
			}

			database.update_event(event_data)

		return jsonify({
			"event_id": event_id
		})


@current_app.route("/api/events", methods=['PATCH'])
def api_update_event():
	content = request.json
	if "start" in content:
		content["start_time"] = dt.parse(content["start"])
		content.pop("start")
	if "end" in content:
		content["end_time"] = dt.parse(content["end"])
		content.pop("end")
	database.update_event(content)

	event = database.get_event_by_id(content["id"])[0]
	if event['event_external_id'] and "token" in session:
		credentials = session['token']
		update_google_calendar_event(
			credentials,
			event['event_external_id'],
			event["title"],
			event["start_time"],
			event["end_time"],
		)

	return jsonify({
		"event_id": content["id"]
	})


@current_app.route("/api/event/<int:event_id>", methods=['DELETE'])
def api_delete_event(event_id):
	try:
		database.remove_event(event_id)
	except Exception as e:
		print(e)
	return jsonify({
		"event_id": event_id
	})


@current_app.route("/api/today_events/", methods=['GET'])
def api_get_events():
	today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

	start_date = today - datetime.timedelta(hours=9)
	end_date = today + datetime.timedelta(days=1, hours=9)

	credentials = session['token']

	result = get_google_calendar_events(credentials, start_date, end_date)

	return jsonify(result)


@current_app.route("/api/set_goal", methods=['POST'])
def api_set_goal():
	content = request.json
	user_id = content['user_id']
	priority = content['priority']
	date = content['date']
	if content['table'] == 'daily':
		table = "daily_tasks"
	elif content['table'] == 'weekly':
		table = "weekly_tasks"
	elif content['table'] == 'monthly':
		table = "monthly_goals"
	else:
		table = "yearly_goals"
	task = database.get_task(user_id, date, priority, table)

	if task and len(task) > 0:
		update_content = {
			"id": task[0]['id'],
			"table": content["table"]
		}

		if "name" in content:
			update_content["name"] = content["name"]
		if "done" in content:
			update_content["done"] = content["done"]
		result = database.update_task(update_content)
	else:
		task_id = database.add_task(
			user_id,
			content["name"],
			priority,
			table,
			content['date'],
		)
		result = {
			"task_id": task_id
		}

	return jsonify(result)


@current_app.route("/login", methods=['POST'])
def login():
	content = request.json
	source = None

	if content.get("source", None) == "google":
		source = "google"
		code = content.get("token", None)
		token = get_google_token(code)

		access_token = token['access_token']
		refresh_token = token['refresh_token']

		user_info = get_google_profile(access_token)

		content["email"] = user_info["email"]
		content["first_name"] = user_info["given_name"]
		content["last_name"] = user_info["family_name"]
		content["google_access_token"] = access_token
		content["google_refresh_token"] = refresh_token

	user = database.get_user_by_email(content['email'])
	user_id = None

	if len(user) > 0:
		user_id = user[0]['id']

		if "google_access_token" in content:
			database.update_user({
				"id": user_id,
				"google_access_token": content["google_access_token"],
				"google_refresh_token": content["google_refresh_token"]
			})

		user = database.get_user_by_id(user_id)
	elif "token" in content:
		new_user_content = {**content}
		new_user_content.pop('token', None)
		new_user_content.pop('source', None)
		user_id = database.create_user(new_user_content)
		if user_id:
			user = database.get_user_by_id(user_id)

	if user and user_id:
		coach = Coach(user_id, "monthly")

		log_request(request, coach.user_id, 'login', '', '')

		session['user_id'] = user_id
		session['coach'] = coach
		session['token'] = get_google_credential(user[0]["google_access_token"], user[0]["google_refresh_token"])

		print("session created for user_id", user_id)

	if user and "token" in content:
		try:
			credentials = session['token']

			_sync_google_event(credentials, user_id)
		except BaseException as err:
			print(f"Unexpected {err=}, {type(err)=}")

	response = user
	return jsonify(response)


@current_app.route("/api/profile", methods=['GET', 'POST'])
def get_user():
	if request.method == 'GET':
		if "user_id" in session:
			user_id = session['user_id']
			user = database.get_user_by_id(user_id)
			return jsonify(user)
		else:
			return jsonify(None)
	else:
		content = request.form.to_dict()
		content["id"] = session['user_id']

		if "avatar" in request.files:
			avatar = request.files["avatar"]
			file_name = secure_filename(avatar.filename)
			avatar.save(os.path.join("upload/avatars", file_name))
			content["profile_image"] = f'/avatar/{file_name}'

		database.update_user(content)
		user = database.get_user_by_id(session['user_id'])

		return jsonify(user)


@current_app.route("/api/goals/<int:user_id>", methods=['GET'])
def get_goals(user_id):
	content = request.args
	goal_type = content.get("type")
	current_date = parse(content.get("date"))

	goals = database.get_set_goal_tasks(user_id, goal_type, current_date)

	return jsonify([
		{
			"id": goal['id'],
			"name": goal['name'],
			"priority": goal["priority"],
			"done": goal["done"]
		} for goal in goals
	])


@current_app.route("/logout", methods=['POST'])
def logout():
	session.pop("user_id", None)
	session.pop("token", None)

	if session.get('coach'):
		coach = session['coach']
		log_request(request, coach.user_id, 'logout', '', '')

		session.pop('coach', None)

		print("logout user_id", coach.user_id)
		return jsonify({})
	else:
		print('invalid session - no Coach object')
		return jsonify('')


@current_app.route("/change_screen/<string:screen_name>", methods=['POST'])
@cross_origin()
def change_screen(screen_name):
	if session.get('coach'):
		coach = session['coach']
		coach.change_screen(screen_name)
		log_request(request, coach.user_id, 'change_screen', screen_name, '')

		state_response = stateResponse[coach.interval][coach.state]
		response_text = state_response[0]  # positive greeting
		response_text = coach.replace_variables(response_text)
		session.modified = True
		return jsonify(response_text)
	else:
		print('invalid session - no Coach object')
		return jsonify('')


@current_app.route("/reset-password", methods=['GET', 'POST'])
def reset_password():
	if request.method == 'POST':
		content = request.json
		email = content.get('email', None)
		user = database.get_user_by_email(email)
		if not user:
			return "Cant find user with this email", 400

		user = user[0]
		token = generate_password_hash(user["email"])
		update_data = {
			"id": user["id"],
			"reset_password_token": token,
			"reset_password_token_expire": datetime.datetime.now() + datetime.timedelta(
				minutes=current_app.config["password_reset_timeout"]
			)
		}

		database.update_user(update_data)

		reset_password_link = current_app.config.get("base_url") + f'/reset-password?token={token}'

		reset_password_body = get_password_reset_email_template().replace("{password_reset_link}", reset_password_link)
		msg = create_email("Reset Password", [user["email"]], reset_password_body)

		try:
			mail_service.send(msg)
		except Exception as e:
			print(e)

		return jsonify({'success': True})

	if request.method == 'GET':
		return send_from_directory("../static/app", "reset-password.html")


@current_app.route("/change_password", methods=['POST'])
def change_password():
	content = request.form
	token = content.get("token")
	users = database.get_user_by_token(token)
	if not users or len(users) == 0:
		flash("Invalid Token!")
		return redirect(request.referrer)
	user = users[0]

	if user["reset_password_token_expire"] < datetime.datetime.now():
		flash("Token Expired!")
		return redirect(request.referrer)

	update_user = {
		"id": user["id"],
		"password": content["password"],
		"reset_password_token": None,
		"reset_password_token_expire": None
	}

	database.update_user(update_user)

	return redirect(url_for("home"))


@current_app.route("/")
def home():
	return send_from_directory("../static/app", "index.html")


@current_app.route("/bundle.js")
def bundle():
	return send_from_directory("../static/dist", "bundle.js")


@current_app.route('/favicon.ico')
def favicon():
	return send_from_directory("../static", "favicon.ico", mimetype='image/vnd.microsoft.icon')


@current_app.route("/public/style.css")
def style():
	return send_from_directory("../static/dist/public", "style.css")


@current_app.route("/images/<string:name>")
def images(name):
	return send_from_directory("../static/images", name)


@current_app.route("/avatar/<string:name>")
def avatars(name):
	return send_from_directory("../upload/avatars", name)


@current_app.route("/api/todos/<int:user_id>", methods=['GET', 'POST', 'PATCH'])
def api_todos(user_id):
	if request.method == 'GET':
		todos = database.get_todos(user_id)

		return jsonify(todos)

	elif request.method == 'POST':
		content = request.json
		content["user_id"] = user_id
		content["start_date"] = dt.parse(content["start_date"])
		content["priority"] = 100
		todo = database.add_todo(content)

		return jsonify(todo)

	else:
		content = request.json
		content["user_id"] = user_id
		todo = database.update_todo(content)

		return jsonify(todo)


@current_app.route("/api/todos/<int:todo_id>", methods=['DELETE'])
def api_delete_todos(todo_id):
	response = database.remove_todo(todo_id)
	return jsonify(response)


@current_app.route("/api/todos_priorities/<int:user_id>", methods=['PATCH'])
def api_update_todo_priorities(user_id):
	content = request.json
	for item in content:
		update_data = {
			"id": item["id"],
			"user_id": user_id,
			"priority": item["priority"]
		}

		database.update_todo(update_data)

	return jsonify("success")


@current_app.route("/api/updateTodos", methods=['POST'])
def api_update_todo():
	content = request.json
	user_id = session['user_id']
	for item in content:
		try:
			if "id" in item:
				update_data = {
					"id": item["id"],
					"name": item["name"],
					"priority": item["priority"],
					"parent_id": item["parent_id"],
					"done": item["done"],
					"start_date": dt.parse(item["start_date"]),
					"user_id": user_id,
				}

				database.update_todo(update_data)
			else:
				create_data = {
					"name": item["name"],
					"priority": item["priority"],
					"parent_id": item["parent_id"],
					"start_date": datetime.datetime.utcnow(),
					"user_id": user_id,
					"done": item["done"],
				}

				database.add_todo(create_data)
		except Exception as e:
			print(e)

	return jsonify("success")


@current_app.route("/api/refresh_event", methods=["GET"])
def resync_events():
	if "token" not in session:
		return jsonify("success")

	try:
		user_id = session['user_id']
		credentials = session['token']
		if credentials.expired:
			credentials.refresh()
		session['token'] = credentials
		_sync_google_event(credentials=credentials, user_id=user_id)
	except BaseException as err:
		print(f"Unexpected {err=}, {type(err)=}")
	return jsonify("success")
