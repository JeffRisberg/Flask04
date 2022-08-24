import json
from flask import current_app

from .util import *
from .database import *
from .coach_state import stateResponse

#++++++++++++++++++++++++++++++++++++

def user_name(coach):
	user_id = coach.user_id
	return get_userName(user_id)


def task_1(coach):
	table = coach.table
	task_id = coach.task_ids[coach.interval][0]
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
	monthName=nowU.strftime('%B')
	return monthName

def choices(coach):
	interval = coach.interval
	a = get_nonzeros(coach.task_ids[interval])
	if len(a) == 3:
		return "1, 2 or 3"
	elif len(a) == 2:
		return "1 or 2"

def current_task(coach):
	table = coach.table
	task_id = coach.task_id
	return get_taskName(task_id, table)


variables = {
	"user_name": user_name,
	"task_1": task_1,
	"task_2": task_2,
	"task_3": task_3,
	"today_day": today_day,
	"today_date": today_date,
	"this_month": this_month,
	"choices": choices,
	"current_task": current_task
}


def show_tasks(coach, response, userIn):
	table = coach.table
	user_id = coach.user_id
	timezoneU = coach.timezone
	date = coach.date
	if table == "weekly_tasks":
		date = coach.Monday
	elif table == "monthly_goals":
		date = coach.firstDay_month

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


def top3_ids(user_id, date, table):
	with engine.connect() as conn:
		ids = [0, 0, 0]
		query = 'SELECT id, priority FROM ' + table + ' where user_id=' + str(user_id)+' and done=0'
		if (table == "daily_tasks"):
			query += ' and date_local="' + str(date) + '"'
		elif (table == "weekly_tasks"):
			query += ' and Monday="' + str(date) + '"'
		else:
			query += ' and firstDay_month="' + str(date) + '"'
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
		self.change_screen(screen_name)

		self.timezone = 'US/Pacific'  # update with user time zone
		tz=timezone(self.timezone)
		nowU = datetime.datetime.now(tz)
		self.year, self.month,self.day=nowU.year, nowU.month, nowU.day
		self.date= nowU.strftime('%Y-%m-%d') #this is a string, not a datetime object

		Monday = nowU - datetime.timedelta(days=nowU.weekday())  #this returns seconds, Monday index is 0
		self.Monday = Monday.strftime('%Y-%m-%d')
		firstDay_month = datetime.date(self.year,self.month,1)
		self.firstDay_month = str(firstDay_month)

		self.find_task_ids(user_id)
		self.task_id = 0  # tracking the current task we are talking about

		self.goalIndex = 0
		self.planStep = 0 # for plan month
		self.goal_id = 0  #for current planning
		self.priority = 0  #for current planning
		self.Monday_toPlan = ''

		self.history = []
		self.prior_question = ""
		self.content_version_count = 0

	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__)

	def find_task_ids(self, user_id):
		self.task_ids = {"daily": top3_ids(user_id, self.date, "daily_tasks"), # current top 3 tasks, index 0=priority 1
						 "weekly": top3_ids(user_id, self.Monday, "weekly_tasks"),
						 "monthly": top3_ids(user_id, self.firstDay_month, "monthly_goals")}
		print("self.task_ids=", self.task_ids)

	def change_screen(self, screen_name):  # weekly, daily, monthly, past_weekly, past_daily
		self.interval = "daily"
		if screen_name in stateResponse:
			self.interval = screen_name

		self.table = "daily_tasks"
		if self.interval == "weekly":
			self.table = "weekly_tasks"
		elif self.interval == "monthly":
			self.table = "monthly_goals"
		print("set interval to", self.interval, "table", self.table)

		self.state = "greet"

	def reset(self):
		self.state = "greet"
		self.history = []
		self.task_id = 0
		self.task_ids[self.interval] = [0, 0, 0]  #delete entered tasks
		if self.interval == "daily":
			reset_task_table(self.user_id, self.date, "daily_tasks")  # clear table of today's tasks
		elif self.interval == "weekly":
			reset_task_table(self.user_id, self.Monday, "weekly_tasks")  # clear table of this week's tasks
		else:
			reset_task_table(self.user_id, self.date, "monthly_goals")  # clear table of this month's tasks
		print("self.task_ids=", self.task_ids)

	def replace_variables(self, text):
		for variable in get_variables(text):
			entity = variables.get(variable)(self)
			if entity != None:
				entity=entity.strip()  #remove white space
				if len(entity) > 0 and entity[-1] == '.':
					entity=entity[:-1]
				text = replace_variable(text, variable, entity)
		return text

	def respond_and_act(self, state, userIn):
		#print("Begin respond_and_act: self.interval=", self.interval, "state=", state, "userIn=", userIn)
		state_response = stateResponse[self.interval][state]
		response_text = state_response[0]  # positive
		action = state_response[1]
		action(self, userIn)  # take action, update tables
		response_text = self.replace_variables(response_text)
		return response_text

	def receive_greet(self, userIn, result):
		a = get_nonzeros(self.task_ids[self.interval])
		if len(a) > 0:
			review=['review_1Task','review_2Tasks','review_3Tasks']
			self.state = review[len(a)-1]
			response_text = self.respond_and_act(self.state, userIn)
			result = show_tasks(self, response_text, userIn)
		else:  # no tasks existing
			self.state = "ask_task1"
			response_text = self.respond_and_act(self.state, userIn)
			result = {'text': response_text, 'widget': 'text_with_content_update','content': self.content_version_count}
		return response_text, result

	#This function plans for all 3 goals in weekly
	def plan_week1(self, userIn, result):
		response_text='plan for a week goal' #place holder
		goal_ids=self.task_ids["weekly"]
		print("goal_ids=",goal_ids)
		ordinal=["first", "second", "third"]
		dates=get_weekDates(self.year, self.month, self.day)
		if (self.goalIndex<3):
			goal_id=goal_ids[self.goalIndex]
			if (self.planStep == 3): #Plan 3 actions for the week
				response_text='Great'
				self.goalIndex +=1
				self.planStep =0  #reset plan

			print("  goal_id=",goal_id)
			if (goal_id>0):
				priority=self.goalIndex+1
				goal=get_taskName(goal_id, "weekly_tasks")
				ordinalName=ordinal[self.planStep]
				response_text="What is your "+ ordinalName+" task for completing '"+ goal +"'?"

				if not (self.goalIndex==0 and self.planStep==0): #in the initial step, no user input
					task=userIn
					date=dates[self.planStep] #use Monday, Tuesday and Wed for the 3 tasks
					#need to get the date for each action, for now just user current date
					add_childTask(user_id, goal_id, "weekly_tasks", task, priority, "daily_tasks", str(date))
				self.planStep +=1
			else: #0 or -1 indicates there is no goal or user are willing to enter more goals
				self.state=stateResponse["plan_week"][2]
		else:
			self.state=stateResponse["plan_week"][2] #in the main dialog, Move to the state after "plan_month"

		result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}
		return response_text, result

	def end_planning_week(self, userIn):
		add_childTask(self.user_id, self.goal_id, "weekly_tasks", userIn, self.priority, "daily_tasks", self.date_toPlan)
		self.goalIndex=0 #reset goalIndex
		self.planStep=0 #reset
		response_text="We have finished planning for all the weekly goals. Congratulations!"
		self.state=stateResponse['weekly']["plan_week"][2][0] #Move back to main dialog state
		return response_text

	#This function plans for all 3 goals for a weekly goal
	def plan_week(self, userIn, result):
		response_text='Place holder' #place holder
		goal_ids=self.task_ids["weekly"]
		print("goal_ids=",goal_ids)
		Monday=self.Monday #Monday of this week
		dates=get_weekDates(self.year, self.month, self.day) #the 7 dates in a week, starting with Monday
		maxDays=3

		print("self.goalIndex=",self.goalIndex)
		if (self.goalIndex<3):
			goal_id=goal_ids[self.goalIndex]
			print("  goal_id=",goal_id)
			goal=get_taskName(goal_id, "weekly_tasks")

			date_toPlan=str(dates[self.planStep])
			priority=self.goalIndex+1
			if (goal_id>0):
				if (self.goalIndex==0 and self.planStep==0): #in the initial step, no user input
					response_text="Excellent. Now let's create a plan for the goal '"+goal+"'."
					response_text=response_text+" What do you have to do first?"
				else:
					add_childTask(self.user_id, self.goal_id, "weekly_tasks", userIn, self.priority, "daily_tasks", date_toPlan)
					step="second"
					if (self.planStep==2):
						step="third"
					elif (self.planStep==0):
						step="first"
					response_text="What is the "+step +" thing you have to do in order to accomplish '" + goal + "'?"

				self.priority=priority
				self.date_toPlan=date_toPlan
				self.goal_id=goal_id #remember previous goal_id
				self.planStep += 1
				if (self.planStep == maxDays): #reaching max index
					self.goalIndex +=1
					self.planStep =0  #reset plan

			else: # goal_id=-1 or 0, user don't have 3 goals
				response_text=self.end_planning_week(userIn)
		else: #elf.goalIndex=3, Finished planning for all 3 goals
			response_text=self.end_planning_week(userIn)

		#print(response_text)
		result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}
		return response_text, result

	def end_planning_month(self, userIn):
		add_childTask(self.user_id, self.goal_id, "monthly_goals", userIn, self.priority, "weekly_tasks", self.Monday_toPlan)
		self.goalIndex=0 #reset goalIndex
		self.planStep=0 #reset
		response_text="We have finished planning for all the monthly goals. Congratulations!"
		self.state=stateResponse['monthly']["plan_month"][2][0] #Move back to main dialog state
		return response_text

	#This function plans for all 3 goals in monthly
	def plan_month(self, userIn, result):
		response_text='Place holder' #place holder
		goal_ids=self.task_ids["monthly"]
		print("goal_ids=",goal_ids)
		Mondays=get_Mondays(self.year, self.month) #return a list of Mondays for that month, datetime objects
		totalWeeks=len(Mondays) #may be 4 or 5

		print("self.goalIndex=",self.goalIndex)
		if (self.goalIndex<3):
			goal_id=goal_ids[self.goalIndex]
			print("  goal_id=",goal_id)
			goal=get_taskName(goal_id, "monthly_goals")

			MondayName=Mondays[self.planStep][1] #the 2nd element of a datetime object
			Monday_toPlan=str(Mondays[self.planStep][0])
			priority=self.goalIndex+1
			if (goal_id>0):
				if (self.goalIndex==0 and self.planStep==0): #in the initial step, no user input
					response_text="Excellent. Now let's create a plan for the goal '"+goal+"'."
					response_text=response_text+"What is your goal for the week of " + MondayName +"?"
				else:
					add_childTask(self.user_id, self.goal_id, "monthly_goals", userIn, self.priority, "weekly_tasks", Monday_toPlan)
					response_text="What is your goal for the week of " + MondayName + " in order to accomplish '" + goal + "'?"

				self.priority=priority
				self.Monday_toPlan=Monday_toPlan
				self.goal_id=goal_id #remember previous goal_id
				self.planStep += 1
				if (self.planStep == totalWeeks): #reaching max index
					self.goalIndex +=1
					self.planStep =0  #reset plan

			else: # goal_id=-1 or 0, user don't have 3 goals
				response_text=self.end_planning_month(userIn)
		else: #elf.goalIndex=3, Finished planning for all 3 goals
			response_text=self.end_planning_month(userIn)

		#print(response_text)
		result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}
		return response_text, result

	def respond(self, userIn):
		result = ""
		if userIn == 'reset':
			self.reset()
			response_text = "Ok, let's start over"
			result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}
		else:
			print("In respond, self.state is:", self.state)
			userIn = userIn.replace('"', '\'')
			if self.state == 'greet':
				#sentiment = get_sentiment(userIn)
				#print(sentiment)
				response_text, result=self.receive_greet(userIn, result)
				self.state = stateResponse[self.interval][self.state][2][0]
			elif self.state == 'plan_month':
				response_text, result=self.plan_month(userIn, result)
				#No state update, this will be controled inside the plan_month function
			elif self.state == 'plan_week':
				response_text, result=self.plan_week(userIn, result)
			else:
				prior_state = self.state
				has_intent = get_intent(userIn, current_app)
				print("User:", userIn, "intent=", has_intent)

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
				elif self.interval == 'weekly':
					if (self.state == 'ask_task2' or self.state == 'ask_why2') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif (self.state == 'ask_task3' or self.state == 'ask_why3') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif self.state == 'confirm_tasks' and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
				else:
					if (self.state == 'ask_task2') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif (self.state == 'ask_task3') and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"
					elif self.state == 'confirm_tasks' and not has_intent:
						self.state = "done_entering_tasks"
						prior_state = "done_entering_tasks"

				state_response = stateResponse[self.interval][self.state]
				action_result = state_response[1](self, userIn)  # take action, update tables

				if action_result == 1:
					self.state = stateResponse[self.interval][self.state][2][1]
					response_text = stateResponse[self.interval][self.state][0]
				else:
					response_text = state_response[0]  # positive

				self.state = stateResponse[self.interval][self.state][2][0]

				response_text = self.replace_variables(response_text)

				if (prior_state in ["confirm_tasks", "done_entering_tasks", "confirm_priority"]):
					result = show_tasks(self, response_text, userIn)
				else:
					result = {'text': response_text, 'widget': 'text_with_content_update', 'content': self.content_version_count}

		self.history.append("User: " + userIn + "<p>" + "Coach: " + str(response_text) + "<p>")
		self.content_version_count += 1
		return result
