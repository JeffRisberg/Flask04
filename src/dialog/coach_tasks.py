import json
import string  # used for user input cleanup

from src.util import *
from ..database import *


def get_overlap(userIn, itemList):  # utility
	for punc in string.punctuation:  # replace all punctuation
		userIn = userIn.replace(punc, '')
	words = userIn.split()
	items = set(itemList).intersection(words)
	return list(items)


def clean(userIn):  # utility
	for punc in string.punctuation:  # replace all punctuation
		userIn = userIn.replace(punc, '')
	words = userIn.split()
	return words


def add_task_priority(coach, userIn, priority):
	table = coach.table
	user_id = coach.user_id
	task = userIn.replace("I want to ", "")
	task = task.replace("i want to ", "")
	task = task.replace("I need to ", "")
	coach.task_id = add_task(user_id, task, priority, table)
	coach.task_ids[coach.interval][priority - 1] = coach.task_id


def add_task1(coach, userIn):
	priority = 1
	add_task_priority(coach, userIn, priority)


def add_task2(coach, userIn):
	priority = 2
	add_task_priority(coach, userIn, priority)


def add_task3(coach, userIn):
	# print("begin add_tasks3")
	priority = 3
	add_task_priority(coach, userIn, priority)


def show_tasks(coach, response, userIn):
	table = coach.table
	user_id = coach.user_id
	timezoneU = coach.timezone
	date = coach.date
	if table == "weekly_tasks":
		date = this_Monday(timezoneU)

	tasks = get_tasks_notDone(user_id, date, table)
	choices = []
	for item in tasks:
		id = item[0]
		name = item[1]
		priority = item[2]
		link = {priority: id}
		if len(name) > 40:
			name = name[:40]
			index = name.rfind(" ")
			if index > 1:
				name = name[:index]
			name += "..."
		taskName = str(priority) + '. ' + name
		choice = {'id': id, 'text': taskName, 'link': link}
		choices.append(choice)
	result = {'text': response, 'widget': 'buttons', 'choices': choices, 'active': False,
			  'content': coach.content_version_count}
	# print("at end of show_tasks, result=", result)
	return result


# this one receives priority No in userIn
def update_priority1(coach, userIn):
	print("begin update_priority1")
	interval = coach.interval
	table = coach.table
	currentPri = 0
	if (userIn.isdigit()):  # user input is priority number
		currentPri = int(userIn)
		coach.task_id = coach.task_ids[interval][currentPri - 1]

	# print("coach.task_id=", coach.task_id)
	update_priority(coach.task_id, 1, table)

	# update other tasks' priority
	if (currentPri == 2):
		id_task1 = coach.task_ids[interval][0]  # current task #1
		coach.task_ids[interval][0] = coach.task_id
		coach.task_ids[interval][1] = id_task1
		update_priority(id_task1, 2, table)
	elif (currentPri == 3):
		id_task1 = coach.task_ids[interval][0]  # current task #1
		id_task2 = coach.task_ids[interval][1]
		coach.task_ids[interval] = [coach.task_id, id_task1, id_task2]  # update

		update_priority(id_task1, 2, table)
		update_priority(id_task2, 3, table)


def update_priority2(coach, userIn):
	print("begin update_priority2")
	table = coach.table
	interval = coach.interval
	currentPri = 0
	# id2Pri, pri2id = id_priority_map(user_id, table)
	if (userIn.isdigit()):  # user input is priority number
		currentPri = int(userIn)
		coach.task_id = coach.task_ids[interval][currentPri - 1]
	update_priority(coach.task_id, 2, table)

	if (currentPri == 3):  # move the 2nd to 3rd
		id_task2 = coach.task_ids[interval][1]
		update_priority(id_task2, 3, table)


# if currentPri=2, do nothing
# if currentPri=1, this is a rare case, as we just set the first priority

def update_why1(coach, userIn):
	priority = 1
	update_why(coach.task_id, priority, userIn, coach.table)


def update_why2(coach, userIn):
	priority = 2
	update_why(coach.task_id, priority, userIn, coach.table)


def update_why3(coach, userIn):
	priority = 3
	update_why(coach.task_id, priority, userIn, coach.table)


def confirm_priority(coach, userIn):
	print(userIn)


def get_hours(coach, userIn):  # used for weekly and daily
	# print("begin get_hours")
	words = clean(userIn)
	hours = 0
	for word in words:
		if (word.isdigit()):
			hours = int(word)
	print("hours=", hours)
	update_column(coach.task_id, "duration", hours, coach.table)
	print("updated column duration for task_id", coach.task_id)


# Assume the user answers "5 am", "5am", "7:45pm"
def get_startingTime(coach, userIn):
	with engine.connect() as conn:
		userIn = userIn.lower()
		startingTime = get_timeFormat(userIn)
		if startingTime:  # if it is not empty
			today = datetime.date.today()
			startingTime = str(today) + ' ' + startingTime
			query = 'UPDATE ' + coach.table + ' SET start_time="' + startingTime + '" WHERE id =' + str(
				coach.task_id) + ';'
			conn.execute(query)


def select_task_1(coach, userIn):
	task_id = coach.task_ids[coach.interval][0]
	coach.task_id = task_id


def get_due_date(coach, userIn):  # used for weekly, monthly
	due_date = extract_date(userIn)
	print("due_date=", due_date)
	if due_date != None:
		update_due_date(coach.task_id, due_date, coach.table)
		print("updated column due_date for task_id", coach.task_id)


def get_dayOfWeek(coach, userIn):
	day_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
	days = get_overlap(userIn, day_of_week)


def get_timeOfDay(coach, userIn):
	timeOfDay = ['morning', 'afternoon', 'evening']
	times = get_overlap(userIn, timeOfDay)


def schedule(coach, userIn):
	print(userIn)


# create_schedule(coach.user_id)

def show_schedule(coach, userIn):
	print(userIn)


def no_action(coach, userIn):
	pass


class DialogStep:
	def __init__(self, name, response, next_step_name):
		self.name = name
		self.response = response
		self.next_step_name = next_step_name
		self.dialog = None

	def execute(self, coach, userIn):
		pass


class DialogStepAction(DialogStep):
	def __init__(self, name, response, action, next_step_name):
		super().__init__(name, response, next_step_name)
		self.action = action

	def execute(self, coach, userIn):
		action = self.action
		if action != None:
			action(coach, userIn)  # take action, update tables
		next_step_name = self.next_step_name

		next_step = self.dialog.steps[next_step_name]
		response_text = self.response
		response_text = coach.replace_variables(response_text)
		result = {'text': response_text, 'widget': 'text_with_content_update',
				  'content': coach.content_version_count}
		return next_step, result


class DialogStepCondition(DialogStep):
	def __init__(self, name, true_step_name, false_step_name):
		super().__init__(name, "", "")
		self.true_step_name = true_step_name
		self.false_step_name = false_step_name

	def execute(self, coach, userIn):
		a = get_nonzeros(coach.task_ids[coach.table])
		if len(a) > 0:
			next_step_name = self.true_step_name
		else:  # no tasks existing
			next_step_name = self.false_step_name

		next_step = self.dialog.steps[next_step_name]
		return self.dialog.execute_step(coach, next_step, "")


class DialogStepSubDialog(DialogStep):
	def __init__(self, name, next_step_name, sub_dialog):
		super().__init__(name, None, next_step_name)
		self.sub_dialog = sub_dialog

	def execute(self, coach, userIn):
		print("executing", self.name)
		coach.active_dialogs.append(self.sub_dialog)
		first_step = self.sub_dialog.get_first_step()

		response_text = first_step.response
		response_text = coach.replace_variables(response_text)
		print(response_text)
		result = {'text': response_text, 'widget': 'text_with_content_update',
				  'content': coach.content_version_count}
		return first_step, result


class Dialog:
	def __init__(self, name, table_name):
		self.steps = {}
		self.table_name = table_name

	def add_step(self, step):
		step.dialog = self
		self.steps[step.name] = step

	def get_first_step(self):
		return self.steps['START']

	def get_second_step(self):
		first_step = self.get_first_step()
		second_step_name = first_step.next_step_name
		return self.steps[second_step_name]

	def execute_step(self, coach, step: DialogStep, userIn):
		return step.execute(coach, userIn)


###################

dialog_add_task = Dialog("add_task", None)

dialog_add_task.add_step(DialogStepAction
						 ("START", "What is the most important thing you want to get done today?",
						  no_action,
						  "ask_why"))
dialog_add_task.add_step(DialogStepAction
						 ("ask_why", "Why must this be done?",
						  no_action,
						  "ask_done_date"))
dialog_add_task.add_step(DialogStepAction
						 ("ask_due_date", "When is this due?",
						  no_action,
						  None))

########

dialog_daily = Dialog("daily", "daily_tasks")

dialog_daily.add_step(DialogStepAction
					  ("START", "Hi *user_name*. I am Dara. I will help you to plan your day today. Shall we start?",
					   no_action,
					   "check_tasks"))
dialog_daily.add_step(DialogStepCondition
					  ("check_tasks",
					   "review_tasks", "add_task"))
dialog_daily.add_step(DialogStepAction
					  ("review_tasks",
					   "You have planned the following tasks for today. Which one is the most important for today? Please indicate by their number: *choices*",
					   no_action,
					   "changepriority"))

dialog_daily.add_step(DialogStepSubDialog("add_task", "task2", dialog_add_task))
dialog_daily.add_step(DialogStepSubDialog("task2", "task3", dialog_add_task))
dialog_daily.add_step(DialogStepSubDialog("task3", "final_step", dialog_add_task))

dialog_daily.add_step(DialogStepAction
					  ("changepriority", "",
					   update_priority1,
					   "final_step"))

dialog_daily.add_step(DialogStepAction
					  ("final_step", "Bye now.",
					   no_action,
					   None))

######

dialog_weekly = Dialog("weekly", "weekly_tasks")

dialog_weekly.add_step(DialogStepAction
					   ("START",
						"Hi *user_name*, welcome to *today_day*. I am Dara. I will help you plan for this week. Shall we start?",
						no_action,
						"check_tasks"))
dialog_weekly.add_step(DialogStepCondition
					   ("check_tasks",
						"review_tasks", "add_task"))
dialog_weekly.add_step(DialogStepAction
					   ("review_tasks",
						"You have planned the following tasks for this week. Which one is the most important? Please indicate by their number: *choices*",
						no_action,
						"changepriority"))

dialog_weekly.add_step(DialogStepSubDialog("add_task", "task2", dialog_add_task))
dialog_weekly.add_step(DialogStepSubDialog("task2", "task3", dialog_add_task))
dialog_weekly.add_step(DialogStepSubDialog("task3", "final_step", dialog_add_task))

dialog_weekly.add_step(DialogStepAction
					   ("changepriority", "",
						update_priority1,
						"final_step"))

dialog_weekly.add_step(DialogStepAction
					   ("final_step", "Bye now.",
						no_action,
						None))

######

dialog_monthly = Dialog("monthly", "monthly_goals")

dialog_monthly.add_step(DialogStepAction
						("START", "Hi *user_name*, I am Dara. I will help you plan for this month. Shall we start?",
						 no_action,
						 "check_tasks"))
dialog_monthly.add_step(DialogStepCondition
						("check_tasks",
						 "review_tasks", "add_task"))
dialog_monthly.add_step(DialogStepAction
						("review_tasks",
						 "You have planned the following tasks for this month. Which one is the most important? Please indicate by their number: *choices*",
						 no_action,
						 "changepriority"))

dialog_monthly.add_step(DialogStepSubDialog("add_task", "task2", dialog_add_task))
dialog_monthly.add_step(DialogStepSubDialog("task2", "task3", dialog_add_task))
dialog_monthly.add_step(DialogStepSubDialog("task3", "final_step", dialog_add_task))

dialog_monthly.add_step(DialogStepAction
					   ("changepriority", "",
						update_priority1,
						"final_step"))

dialog_monthly.add_step(DialogStepAction
						("final_step", "Bye now.",
						 no_action,
						 None))

######

# Each state has 3 elements: response, action, next state List
stateResponse = {
	"daily": {
		"greet": [
			"Hi *user_name*. I am Dara. I will help you to plan your day today. Shall we start?",
			no_action,
			["review_Tasks", "review_Task1", "ask_task1"]  # check existing tasks
		],
		"review_Tasks": [
			"You have planned the following tasks for today. Which one is the most important for today? Please indicate by their number: *choices*",
			no_action,
			["ask_why1"]
		],
		"review_Task1": [
			"You have planned 1 task for today. What else do you want to get done today?",
			no_action,
			["ask_task3"]
		],
		"ask_task1": [
			"What is the most important thing you want to get done today?",
			no_action,
			["ask_task2", "rephrase_task1"]
		],
		"rephrase_task1": [
			"Let me rephrase it. What's your top task for today?",
			no_action,
			["ask_task2"]
		],
		"ask_task2": [
			"What else do you want to get done today?",
			add_task1,
			["ask_task3"]
		],
		"ask_task3": [
			"What's the third thing you want to get done?",
			add_task2,
			["confirm_tasks"]
		],
		"confirm_tasks": [
			"Great. Here are your top tasks for today. Which one is the most important? Please indicate by the item number",
			add_task3,
			["ask_why1"]
		],
		"done_entering_tasks": [
			"Great. Here are your top tasks for today. Which one is the most important? Please indicate by the item number",
			no_action,
			["ask_why1"]
		],
		"ask_why1": [
			"You selected *task_1*. Why is it your most important task?",
			update_priority1,
			["ask_2ndPriority", "ask_hours_1"]
		],
		"ask_2ndPriority": [
			"What's the second most important task for today? Please enter number 1, 2 or 3",
			update_why1,
			["ask_why2"]
		],
		"ask_why2": [
			"Why do you want to get this task done?",
			update_priority2,
			["get_2ndPriority"]
		],
		"get_2ndPriority": [
			"Thank you. I will update your task list.",
			update_why2,
			["confirm_priority"]
		],
		"confirm_priority": [
			"Here are your three most important tasks today, in the order of importance. Do they look good? ",
			update_why2,
			["ask_hours_1"]
		],
		"ask_hours_1": [
			"How much time (indicating hours or minutes) can you spend on *task_1* today?",
			no_action,  # "get_hours",
			["ask_hours_2", "ask_startingTime"]  # check how many tasks
		],
		"ask_hours_2": [
			"How much time (indicating hours or minutes) can you spend on *task_2* today?",
			no_action,  # "get_hours",
			["ask_hours_3", "ask_startingTime"]  # check how many tasks
		],
		"ask_hours_3": [
			"How much time can you spend on *task_3* today?",
			no_action,  # "get_hours",
			["ask_startingTime"]
		],
		"ask_startingTime": [
			"What time are you going to start on *task_1* today? ",
			get_hours,
			["schedule"]
		],
		"schedule": [
			"Wonderful. I have scheduled this in the calendar for you.",
			get_startingTime,  # "schedule",
			["show_schedule"]
		],
		"show_schedule": [
			"I am glad I can be of help. Have a wonderful day",
			schedule,  # "show_schedule",
			["end_conversation"]
		],
		"end_conversation": [
			"Bye now.",
			no_action,
			["end"]
		],
		"end": [
			"",
			no_action,
			["end"]
		]
	},

	"weekly":
		{
			"greet": [
				"Hi *user_name*, welcome to *today_day*. I am Dara. I will help you plan for this week. Shall we start?",
				no_action,
				["review_Tasks", "review_Task1", "ask_task1"]
			],
			"review_Tasks": [
				"You have the following tasks planned for this week. Which one is the most important? Please indicate by their number: *choices*",
				no_action,
				["update_priority1"]
			],
			"update_priority1": [
				"You selected *task_1*. Is this correct?",
				update_priority1,
				["done_entering_tasks"]
			],
			"review_Task1": [
				"You have planned 1 task for this week. What else do you want to get done this week?",
				no_action,
				["ask_why2"]
			],
			"ask_task1": [
				"What is the most important thing you want to get done this week?",
				no_action,
				["ask_why1", "rephrase_task1"]
			],
			"rephrase_task1": [
				"Let me rephrase it. What's your top task for today?",
				no_action,
				["ask_why1"]
			],
			"ask_why1": [
				"Why is it the most important task for you?",
				add_task1,
				["ask_task2"]
			],
			"ask_task2": [
				"What is the second most important goal this week?",
				update_why1,
				["ask_why2"]
			],
			"ask_why2": [
				"Why is *task_2* important for this week?",
				add_task2,
				["ask_task3"]
			],
			"ask_task3": [
				"What's the third thing you want to get done this week?",
				update_why2,
				["ask_why3"]
			],
			"ask_why3": [
				"Why is it important for you?",
				add_task3,
				["confirm_tasks"]
			],
			"confirm_tasks": [
				"Great. Here are your top tasks for this week.  Do they look good?",
				update_why3,
				["ask_hours"]
			],
			"done_entering_tasks": [
				"Great. Here are your tasks for this week, in the order of importance. Do they look good?",
				no_action,
				["ask_hours"]
			],
			"ask_hours": [
				"How many hours do you need in the week to complete this task?",
				get_due_date,
				["ask_startingDate"]
			],
			"ask_startingDate": [
				"What day are you starting on *task_1*?",
				get_hours,
				["ask_timeOfDay"]
			],
			"ask_timeOfDay": [
				"What time in the day works best for you, morning (6am-noon), afternoon (noon-6pm) or evening (after 6pm)?",
				get_timeOfDay,
				["schedule"]
			],
			"schedule": [
				"Wonderful. Now I will add these tasks and create a schedule for you, does that sound good?",
				schedule,
				["show_schedule"]
			],
			"show_schedule": [
				"Here is the schedule for your tasks. Are we good to go?",
				show_schedule,
				["try_end_conversation"]
			],
			"try_end_conversation": [
				"I am glad I can be of help. Have a wonderful day",
				no_action,
				["end_conversation"]
			],
			"end_conversation": [
				"Bye now.",
				no_action,
				["end"]
			],
			"end": [
				"",
				no_action,
				["end"]
			]
		},

	"monthly":
		{
			"greet": [
				"Hi *user_name*, I am Dara. I will help you plan for this month. Shall we start?",
				no_action,
				["review_Tasks", "review_Task1", "ask_task1"]
			],
			"review_Tasks": [
				"You have the following goals for the month of *this_month*. Which one is the most important? Please indicate by their number: *choices*",
				no_action,
				["update_priority1"]
			],
			"update_priority1": [
				"You selected *task_1*. Is this correct?",
				update_priority1,
				["done_entering_tasks"]
			],
			"review_Task1": [
				"You have set 1 goal for the month of *this_month*. What else do you want to get done this month?",
				no_action,
				["ask_why2"]
			],
			"ask_task1": [
				"What is the most important thing you want to get done in *this_month*?",
				no_action,
				["ask_why1", "rephrase_task1"]
			],
			"rephrase_task1": [
				"Let me rephrase it. What's your top goal for this month?",
				no_action,
				["ask_why1"]
			],
			"ask_why1": [
				"Why is it the most important goal for you?",
				add_task1,
				["ask_dueDate1"]
			],
			"ask_dueDate1": [
				"What date is *task_1* due?",
				update_why1,
				["ask_task2"]
			],
			"ask_task2": [
				"What is the second most important goal in *this_month*?",
				get_due_date,
				["ask_why2"]
			],
			"ask_why2": [
				"Why is *task_2* important in *this_month*?",
				add_task2,
				["ask_dueDate2"]
			],
			"ask_dueDate2": [
				"What date is *task_2* due?",
				update_why2,
				["ask_task3"]
			],
			"ask_task3": [
				"What's the third thing you want to get done in *this_month*?",
				get_due_date,
				["ask_why3"]
			],
			"ask_why3": [
				"Why is it important for you?",
				add_task3,
				["ask_dueDate3"]
			],
			"ask_dueDate3": [
				"What date is *task_3* due?",
				update_why3,
				["confirm_tasks"]
			],
			"confirm_tasks": [
				"Great. Here are your goals for *this_month* in the order of importance. Do they look good?",
				get_due_date,
				["ask_hours"]
			],
			"done_entering_tasks": [
				"Great. Here are your top goals for *this_month*. Do they look good?",
				no_action,
				["ask_hours"]
			],
			"ask_hours": [
				"How many hours do you need to complete the goal *task_1*?",
				no_action,
				["ask_startingDate"]
			],
			"ask_startingDate": [
				"What day are you starting on *task_1*?",
				get_hours,
				["schedule"]
			],
			"schedule": [
				"Wonderful. Now I will add these goals and create a schedule for you, does that sound good?",
				schedule,
				["show_schedule"]
			],
			"show_schedule": [
				"Here is the schedule for your goals. Are we good to go?",
				show_schedule,
				["try_end_conversation"]
			],
			"try_end_conversation": [
				"I am glad I can be of help. Have a wonderful day",
				no_action,
				["end_conversation"]
			],
			"end_conversation": [
				"Bye now.",
				no_action,
				["end"]
			],
			"end": [
				"",
				no_action,
				["end"]
			]
		}
}


def user_name(coach):
	user_id = coach.user_id
	return get_userName(user_id)


def task_1(coach):
	table = coach.table
	interval = coach.interval
	task_id = coach.task_ids[interval][0]
	return get_taskName(task_id, table)


def task_2(coach):
	table = coach.table
	task_id = coach.task_ids[coach.interval][1]
	return get_taskName(task_id, table)


def task_3(coach):
	table = coach.table
	task_id = coach.task_ids[coach.interval][2]
	return get_taskName(task_id, table)


def today_day(coach):
	tz = coach.timezone  # tz='Asia/Taipei'
	now = datetime.datetime.now()
	now_local = now.astimezone(timezone(tz))
	day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	return day_of_week[now_local.weekday()]


def today_date(coach):
	return coach.date


def this_month(coach):
	tz = coach.timezone  # tz='Asia/Taipei'
	now = datetime.datetime.now()
	nowU = now.astimezone(timezone(tz))
	monthName = nowU.strftime('%B')
	return monthName


def choices(coach):
	table = coach.table
	a = get_nonzeros(coach.task_ids[table])
	if len(a) == 3:
		return "1, 2 or 3"
	elif len(a) == 2:
		return "1 or 2"


variables = {
	"user_name": user_name,
	"task_1": task_1,
	"task_2": task_2,
	"task_3": task_3,
	"today_day": today_day,
	"today_date": today_date,
	"this_month": this_month,
	"choices": choices
}


def top3_ids(user_id, date, table):
	with engine.connect() as conn:
		ids = [0, 0, 0]
		query = 'SELECT id, priority FROM ' + table + ' where user_id=' + str(user_id) + ' and done=0'
		if (table == "daily_tasks"):
			query += ' and start_date="' + str(date) + '"'
		elif (table == "weekly_tasks"):
			query += ' and start_date="' + str(date) + '"'
		else:
			query += ' and start_date="' + str(date) + '"'
		query += ' order by priority limit 3;'  # limit to 3 in case of duplicates
		results = conn.execute(query)
		resultSet = results.fetchall()  # resultSet=[(90,1),(91,2),(92,3)]
		# print("resultSet=", resultSet)
		if resultSet:
			for i in range(len(resultSet)):
				ids[i] = resultSet[i][0]
		return ids


class Coach:
	def __init__(self, user_id, screen_name):
		print("__init__: screen_name", screen_name)
		self.user_id = user_id
		self.active_dialogs = []  # stack
		self.timezone = 'US/Pacific'  # update with user time zone
		self.date = get_localDate(self.timezone)  # local date for the user
		self.Monday = this_Monday(self.timezone)
		self.task_id = 0  # tracking the current task we are talking about
		self.task_ids = {"daily_tasks": top3_ids(user_id, self.date, "daily_tasks"),
						 "weekly_tasks": top3_ids(user_id, self.Monday, "weekly_tasks"),
						 "monthly_goals": top3_ids(user_id, self.date, "monthly_goals")}
		print("self.task_ids=", self.task_ids)

		self.prior_question = ""
		self.content_version_count = 0
		self.change_screen(screen_name)

	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__)

	def current_dialog(self):
		if len(self.active_dialogs) > 0:
			return self.active_dialogs[len(self.active_dialogs) - 1]
		return None

	def change_screen(self, screen_name):  # weekly, daily, monthly, past_weekly, past_daily
		self.active_dialogs.clear()
		self.table = "daily_tasks"

		if screen_name == "daily":
			self.active_dialogs.append(dialog_daily)
			self.table = "daily_tasks"
		elif screen_name == 'weekly':
			self.active_dialogs.append(dialog_weekly)
			self.table = "weekly_tasks"
		elif screen_name == 'monthly':
			self.active_dialogs.append(dialog_monthly)
			self.table = "monthly_goals"

		print("set dialog to", screen_name, "table", self.table)

		self.state = None
		current_dialog = self.current_dialog()
		if current_dialog != None:
			self.state = current_dialog.get_second_step()

	def reset(self):
		current_dialog = self.current_dialog()

		self.state = None
		if current_dialog != None:
			self.state = current_dialog.get_second_step()

		self.task_id = 0
		self.task_ids[self.table] = [0, 0, 0]  # delete entered tasks

		if self.table == "daily_tasks":
			reset_task_table(self.user_id, self.date, self.table)  # clear table of today's tasks
		elif self.table == "weekly_tasks":
			reset_task_table(self.user_id, self.Monday, self.table)  # clear table of this week's tasks
		else:
			reset_task_table(self.user_id, self.date, self.table)  # clear table of this month's tasks

	def replace_variables(self, text):
		for variable in get_variables(text):
			entity = variables.get(variable)(self)
			if entity != None:
				entity = entity.strip()  # remove white space
				if len(entity) > 0 and entity[-1] == '.':
					entity = entity[:-1]
				text = replace_variable(text, variable, entity)
		return text

	def respond_and_act(self, state, userIn):
		print("Begin respond_and_act: self.interval=", self.interval, "state=", state, "userIn=", userIn)
		state_response = stateResponse[self.interval][state]
		response_text = state_response[0]  # positive
		action = state_response[1]
		action(self, userIn)  # take action, update tables
		response_text = self.replace_variables(response_text)
		return response_text

	def respond(self, userIn):
		prior_state = self.state
		if userIn == 'reset':
			self.reset()
			response_text = "Ok, let's start over"
			result = {'text': response_text, 'widget': 'text_with_content_update',
					  'content': self.content_version_count}
		else:
			userIn = userIn.replace('"', '\'')
			current_dialog = self.current_dialog()

			if current_dialog != None:
				self.state, result = current_dialog.execute_step(self, self.state, userIn)
			else:
				self.state = None
				result = {"text": "no active dialog"}

			"""
			if self.state == 'greet':
				# sentiment = get_sentiment(userIn)
				# print(sentiment)
				a = get_nonzeros(self.task_ids[self.interval])
				if len(a) > 1:
					self.state = 'review_Tasks'
					response_text = self.respond_and_act(self.state, userIn)
					result = show_tasks(self, response_text, userIn)
				elif len(a) == 1:  # len(a)=1
					self.state = "review_Task1"
					response_text = self.respond_and_act(self.state, userIn)
					result = show_tasks(self, response_text, userIn)
				else:  # no tasks existing
					self.state = stateResponse[self.interval][self.state][2][2]  # "ask_task1"
					response_text = self.respond_and_act(self.state, userIn)
					result = {'text': response_text, 'widget': 'text_with_content_update',
							  'content': self.content_version_count}

				self.state = stateResponse[self.interval][self.state][2][0]
			else:
				prior_state = self.state
				has_intent = get_intent(userIn)
				print("User:", userIn, "intent=", has_intent)

				if self.interval != 'daily':
					if (self.state == 'ask_due_date2' or self.state == 'ask_why2') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif (self.state == 'ask_due_date3' or self.state == 'ask_why3') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"

				if self.interval == 'daily':
					if self.state == 'ask_task2' and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif self.state == 'ask_task3' and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif self.state == 'confirm_tasks' and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"

				state_response = stateResponse[self.interval][self.state]
				action = state_response[1]
				action(self, userIn)  # take action, update tables

				state_response = stateResponse[self.interval][self.state]
				response_text = state_response[0]  # positive
				self.state = stateResponse[self.interval][self.state][2][0]
				response_text = self.replace_variables(response_text)

				if (prior_state in ["confirm_tasks", "done_entering_tasks", "confirm_priority"]):
					result = show_tasks(self, response_text, userIn)
				else:
					result = {'text': response_text, 'widget': 'text_with_content_update',
							  'content': self.content_version_count}
			"""

		self.content_version_count += 1
		return result


if __name__ == '__main__':
	user_id = 4
	# coach = Coach(user_id, "daily")
	coach = Coach(4, "weekly")
	print("user_id=", user_id, " today's date is: ", coach.date)
	coach.state = "greet"
	userIn = ""
	while True:
		print("current state:", coach.state)
		coachR = coach.respond(userIn)
		print(coachR)
		print("User:")
		userIn = input()
