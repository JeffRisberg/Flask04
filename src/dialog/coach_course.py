import json

from src.util import *
from ..database import *

DayofWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def show_courses(coach, userIn):
	courseList = get_courses()
	choices = list(map(lambda c: {'id': c['id'], 'text': c['name']}, courseList))
	return {'widget': 'buttons', 'choices': choices, 'active': True}


def add_choices(coach, userIn):
	add_choice(coach.user_id, userIn)
	return {}


def show_selected_courses(coach, userIn):
	add_choice(coach.user_id, userIn)
	selections = selected_courses(coach.user_id)
	choices = list(map(lambda c: {'id': c['id'], 'text': c['name']}, selections))
	return {'widget': 'buttons', 'choices': choices, 'active': False}


def schedule(coach, userIn):
	create_schedule(coach.user_id)
	return {}


def show_jobs(coach, action):
	jobs = get_jobs(coach.company_id)
	jobs = jobs[0:4]
	return {'widget': 'chart',
			  'labels': [job['title'] for job in jobs],
			  'series': [job['level'] for job in jobs]}


def update_content(coach, userIn):
	result = {'widget': 'text_with_content_update', 'content': coach.content_version_count}
	coach.content_version_count += 1
	return result


def default_action(coach, userIn):
	return {}


def no_action(coach, userIn):
	return {}


# Each state has 4 elements: positiveResponse, positiveAction, negativeResponse, nextState
stateResponse = {
	"standard": {
		"greet": [
			"Welcome *user_name*, I'm here to help you you on career development. How are you doing today?",
			no_action,
			"",
			"ask_goal"
		],
		"ask_goal": [
			"Good to hear. I am here to help you complete your learning goal. What do you want to achieve in your career?",
			no_action,
			"Let me rephrase it. What's your ideal job after current learning?",
			"ask_benefits"
		],
		"ask_benefits": [
			"What benefits would you get if you reach this goal?",
			no_action,
			"Let me rephrase it. What's your ideal outcome when achieving this goal?",
			"ask_interest"
		],
		"ask_interest": [
			"I see that you are currently a data scientist II. Are you interested in finding out what training you need to become a senior data scientist (Level 3)?",
			no_action,
			"It seems you are hesitating. While you are here, how about we take a look at the courses, then you can decide if you want to take them?",
			"show_course"
		],
		"show_course": [
			"Great. Here are some courses that would help you reach the next level. For each course, there is a link to review their content.",
			show_courses,
			"",
			"add_selection"
		],
		"add_selection": [
			"What's the next course you want to take?",
			add_choices,
			"",
			"confirm_selection"
		],
		"confirm_selection": [
			"You have selected the following courses:",
			show_selected_courses,
			"",
			"schedule"
		],
		"schedule": [
			"Wonderful. Now I will add these courses and build a plan for you for the next 3 months, does that sound good?",
			schedule,
			"",
			"show_schedule"
		],
		"show_schedule": [
			"On the left is the schedule for the next 3 months. Are we good to go?",
			update_content,
			"Ok, let's review the courses again. Would you like to see your selections?",
			"end_conversation"
		],
		"end_conversation": [
			"Bye, glad I could help with your career.",
			no_action,
			"let's restart",
			"end"
		],
		"end": [
			"",
			no_action,
			"",
			"end"
		]
	}
}


def user_name(coach):
	user_id = coach.user_id
	return get_userName(user_id)


def today_date(coach):
	return coach.date


variables = {
	"user_name": user_name,
	"today_date": today_date
}


class Coach:
	def __init__(self, user_id, screen_name):
		print("__init__: screen_name", screen_name)
		self.user_id = user_id
		self.change_screen(screen_name)

		#self.timezone = 'US/Pacific'  # update with user time zone
		#self.date = get_localDate(self.timezone)  # local date for the user
		#self.Monday = this_Monday()
		#self.task_id = 0  # tracking the current task we are talking about
		#self.task_ids = {"daily": top3_ids(user_id, self.date, "daily_tasks"), # track current top 3 tasks, index 0=priority 1
		#				 "weekly": top3_ids(user_id, self.Monday, "weekly_tasks")}  # track current top 3 tasks
		#print("self.task_ids=", self.task_ids)

		self.history = []
		self.prior_question = ""
		self.content_version_count = 0

	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__)

	def change_screen(self, screen_name):  # weekly, daily, monthly, past_weekly, past_daily
		self.interval = "standard"
		if screen_name in stateResponse:
			self.interval = screen_name

		self.state = "greet"

	def reset(self):
		self.state = "greet"
		self.history = []
		reset_user_course(self.user_id)

	def replace_variables(self, text):
		for variable in get_variables(text):
			entity = variables.get(variable)(self)
			entity=entity.strip()  #remove white space
			if len(entity) > 0 and entity[-1] == '.':
				entity=entity[:-1]
			text = replace_variable(text, variable, entity)
		return text

	def respond_and_act(self, state, userIn):
		print("Begin respond_and_act: self.interval=", self.interval, "state=", state, "userIn=", userIn)
		state_response = stateResponse[self.interval][state]
		response_text = state_response[0]  # positive
		action = state_response[1]
		response = action(self, userIn)  # take action, update tables
		response['text'] = self.replace_variables(response_text)
		return response

	def respond(self, userIn):
		result = ""
		if userIn == 'reset':
			self.reset()
			response_text = "Ok, let's start over"
			result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}
		else:
			userIn = userIn.replace('"', '\'')
			if self.state == 'greet':
				sentiment = get_sentiment(userIn)
				print(sentiment)

				self.state = stateResponse[self.interval][self.state][3]
				result = self.respond_and_act(self.state, userIn)
			else:
				result = self.respond_and_act(self.state, userIn)

			# update state
			self.state = stateResponse[self.interval][self.state][3]

		self.content_version_count += 1
		return result


if __name__ == '__main__':
	bot = Coach(1, "standard")
	bot.state = "greet"
	greeting = "Welcome! I'm here to help you find the best pathway to achieve your goal. How are you doing today?"
	print(greeting)
	while True:
		print("User:")
		userIn = input()
		if (userIn == "bye"):
			quit()
		else:
			print("current state:" + bot.state)
			coachR = bot.get_response(userIn)
			print(coachR)
