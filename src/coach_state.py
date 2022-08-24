from .util import *
from .database.db_user import *
from .database.db_goals import *

def add_task1(coach, userIn):
	# print("begin add_tasks3")
	priority = 1
	add_task_priority(coach, userIn, priority)


def add_task2(coach, userIn):
	# print("begin add_tasks3")
	priority = 2
	add_task_priority(coach, userIn, priority)


def add_task3(coach, userIn):
	# print("begin add_tasks3")
	priority = 3
	add_task_priority(coach, userIn, priority)

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
	task_id = coach.task_id
	if task_id == 0:
		return 0 # ok to proceed

	with engine.connect() as conn:
		userIn = userIn.lower()
		startingTime = get_timeFormat(userIn)
		if startingTime:  # if it is not empty
			today = datetime.date.today()
			startingTime = str(today) + ' ' + startingTime
			query = 'UPDATE ' + coach.table + ' SET start_time="' + startingTime + '" WHERE id =' + str(task_id) + ';'
			conn.execute(query)

	for i in [0,1]:
		if coach.task_ids['daily'][i] == task_id:
			coach.task_id = coach.task_ids['daily'][i+1]
			break
	if coach.task_id != 0:
		return 0 # ok to proceed
	return 1 # take error path


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

"""
# Each state has 3 elements: response, action, next state List
planMonth_states = {
	"ask_week1": [
		"Excellent. Now let's create a plan for *current_task*. What do you need to do in the first week of *this_month*?",
		no_action,
		["ask_week2"]
	],
	"ask_week2": [
		"What do you have to do in the second week of *this_month* in order to complete *current_task*?",
		add_week1,
		["ask_week3"]
	],
	"ask_week3": [
		"What do you need to get done in the third week of *this_month* for *current_task*? There is only 1 more week left in the month.",
		add_week2,
		["ask_week3"]
	],
	"ask_week4": [
		"What is your goal in the fourth and also last week of *this_month* in order to complete *current_task*?",
		add_week3,
		["confirm"]
	],
	"confirm": [
		"Here are your weekly goals in *this_month* in order to complete *current_task*?",
		add_week4,
		["end"]
	],
}
"""

stateResponse = {
"daily": {
	"greet": [
		"Hi *user_name*. I am Dara. I will help you to plan your day today. Shall we start?",
		no_action,
		["review_3Tasks", "review_2Tasks", "ask_1Task"] #check existing tasks
	],
	"review_3Tasks": [
		"You have the following pending tasks for today. Which one is the most important for today? Please indicate by its number: *choices*",
		no_action,
		["ask_hours_1"]
	],
	"review_2Tasks": [
		"You have 2 pending tasks for today. What is the third important thing you want to get done today?",
		no_action,
		["confirm_tasks"]
	],
	"review_1Task": [
		"You have 1 pending task for today. What else do you want to get done today?",
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
		"Great. Here are your top pending tasks for today. ",
		add_task3,
		["ask_hours_1"]
	],
	"done_entering_tasks": [
		"Great. Here are your top pending tasks for today. ",
		no_action,
		["ask_hours_1"]
	],
	"confirm_priority": [
		"Here are your three most important tasks today, in order of importance. Do they look good? ",
		no_action,
		["ask_hours_1"]
	],
	"ask_hours_1": [
		"How much time (in hours or minutes) can you spend on *task_1* today?",
		select_task_1,  # "get_hours",
		["ask_startingTime1", "schedule"] #check how many tasks
	],
	"ask_startingTime1": [
		"What time are you going to start on *task_1* today? ",
		get_hours,
		["ask_hours_2"]
	],
	"ask_hours_2": [
		"How much time (in hours or minutes) can you spend on *task_2* today?",
		get_startingTime,  # "get_hours",
		["ask_startingTime2", "schedule"] #check how many tasks
	],
	"ask_startingTime2": [
		"What time are you going to start on *task_2* today? ",
		get_hours,
		["ask_hours_3"]
	],
	"ask_hours_3": [
		"How much time (in hours or minutes) can you spend on *task_3* today?",
		get_startingTime,  # "get_hours",
		["ask_startingTime3", "schedule"] #check how many tasks
	],
	"ask_startingTime3": [
		"What time are you going to start on *task_3* today? ",
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
		["review_3Tasks", "review_2Tasks","ask_1Task"]
	],
	"review_3Tasks": [
		"You have the following tasks planned for this week. Do they look good?",
		no_action,
		["plan_week"]
	],
	"review_2Tasks": [
		"You have set 2 goals for the week. What is your third most important goal for this week?",
		no_action,
		["confirm_tasks"]
	],
	"review_1Task": [
		"You have planned 1 task for this week. What else do you want to get done this week?",
		no_action,
		["ask_task3"]
	],
	"update_priority1": [
		"You selected *task_1*. Is this correct?",
		update_priority1,
		["done_entering_tasks"]
	],
	"ask_task1": [
		"What is the most important thing you want to get done this week?",
		no_action,
		["ask_task2", "rephrase_task1"]
	],
	"rephrase_task1": [
		"Let me rephrase it. What's your top task for the week?",
		no_action,
		["ask_task2"]
	],
	"ask_task2": [
		"What is the second most important goal this week?",
		add_task1,
		["ask_task3"]
	],
	"ask_task3": [
		"What's the third thing you want to get done this week?",
		add_task2,
		["confirm_tasks"]
	],
	"confirm_tasks": [
		"Great. Here are your top tasks for this week.  Do they look good?",
		add_task3,
		["plan_week"]
	],
	"done_entering_tasks": [
		"Great. Here are your tasks for this week, in the order of importance. Do they look good?",
		no_action,
		["plan_week"]
	],
	"plan_week": [
		"",
		no_action,
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
	"greet": ["Hi *user_name*, I am Dara. I will help you plan for this month. Shall we start?",
				no_action,
				["review_3Tasks", "review_2Tasks","review_1Task", "ask_task1"]],
	"review_3Tasks": ["You have the following goals for the month of *this_month*. Do they look good?",
					no_action,["plan_month"]],
	"review_2Tasks": ["You have set 2 goals for the month of *this_month*. What is your third most important goal for this month?",
					no_action,["confirm_tasks"]],
	"review_1Task": ["You have set 1 goal for the month of *this_month*. What else do you want to get done this month?",
					no_action,
					["ask_task3"]],
	"ask_task1": ["What is the most important thing you want to get done in *this_month*?",
					no_action,
					["ask_task2", "rephrase_task1"]],
	"rephrase_task1": ["Let me rephrase it. What's your top goal for this month?",
					no_action,["ask_task2"]],
	"ask_task2": ["What is the second most important goal in *this_month*?",
					add_task1, #get_due_date
					["ask_task3"]],
	"ask_task3": ["What's the third thing you want to get done in *this_month*?",
					add_task2,["confirm_tasks"]],
	"confirm_tasks": ["Great. Here are your goals for *this_month* in the order of importance. Do they look good?",
						add_task3,["plan_month"]],
	"done_entering_tasks": ["Great. Here are your top goals for *this_month*. Do they look good?",
							no_action,["plan_month"]],
	"plan_month": ["",
					no_action,["schedule"]],
	"schedule": ["Wonderful. Now I will add these goals and create a schedule for you, does that sound good?",
					no_action,["show_schedule"]],
	"show_schedule": ["Here is the schedule for your goals. Are we good to go?",
						show_schedule,["try_end_conversation"]],
	"try_end_conversation": ["I am glad I can be of help. Have a wonderful day",
							no_action,["end_conversation"]],
	"end_conversation": ["Bye now.",
						no_action,["end"]],
	"end": ["",
			no_action,["end"]]
}
}
