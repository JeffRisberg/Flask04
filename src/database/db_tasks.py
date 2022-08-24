import datetime

from pytz import timezone
from sqlalchemy import and_, insert
from sqlalchemy.sql import select, update, delete

from src import engine, metadata

categories = metadata.tables['categories']
users = metadata.tables['users']
top_goals = metadata.tables['top_goals']
monthly_goals = metadata.tables['monthly_goals']
daily_tasks = metadata.tables['daily_tasks']
weekly_tasks = metadata.tables['weekly_tasks']
events = metadata.tables['events']


def nowString():
	now = datetime.datetime.now()
	nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
	return nowStr


def get_localDate(timezoneU):
	now = datetime.datetime.now()
	nowU = now.astimezone(timezone(timezoneU))
	date_local = nowU.strftime('%Y-%m-%d')
	return date_local


def this_Monday(timezoneU):
	now = datetime.datetime.now()
	nowU = now.astimezone(timezone(timezoneU))
	todayIndex = nowU.weekday()  # Monday index is 0
	this_Monday = nowU - datetime.timedelta(days=todayIndex)  # this returns seconds
	this_MondayStr = this_Monday.strftime('%Y-%m-%d')
	return this_MondayStr


def get_year_month(dateStr):
	dateArray = dateStr.split('-')
	year = dateArray[0]
	month = dateArray[1]
	return int(year), int(month)


def get_categories():
	with engine.connect() as conn:
		stmt = select([categories])
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'name': t['name'], 'created': t['created'], 'updated': t['updated']} for t in
				   resultSet]
		return results


def update_top_goal(content):
	with engine.connect() as conn:
		stmt = update(top_goals).where(top_goals.c.id == content['id']).values(**content)
		conn.execute(stmt)

		results = {}
		return results


def get_top_goals(user_id, request):
	with engine.connect() as conn:
		done = request.args.get('done')

		stmt = select([top_goals]).filter(top_goals.c.user_id == user_id)
		if done != None:
			stmt = stmt.filter(top_goals.c.done == done)

		stmt = stmt.order_by(top_goals.c.priority)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'category_id': t['category_id'], 'name': t['name'], 'why': t['why'],
					'priority': t['priority'], 'duration': t['duration'], 'start_date': t['start_date'],
					'due_date': t['due_date'], 'done': t['done']}
				   for t in resultSet]
		return results


def get_monthly_goals(user_id, request):
	with engine.connect() as conn:
		done = request.args.get('done')

		# using today's month
		timezone = 'US/Pacific'  # update with user time zone
		date = get_localDate(timezone)
		year, month = get_year_month(date)
		firstDay_month = datetime.datetime(year, month, 1)
		stmt = select([monthly_goals]).filter(
			and_(monthly_goals.c.user_id == user_id, monthly_goals.c.firstDay_month == str(firstDay_month)))
		if done != None:
			stmt = stmt.filter(monthly_goals.c.done == done)

		stmt = stmt.order_by(monthly_goals.c.priority)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'name': t['name'], 'why': t['why'],
					'firstDay_month': t['firstDay_month'],
					'priority': t['priority'], 'duration': t['duration'], 'start_date': t['start_date'],
					'due_date': t['due_date'], 'done': t['done'],
					'start': (t['firstDay_month'] - datetime.timedelta(days=0)).isoformat(),
					'end': (t['firstDay_month'] - datetime.timedelta(days=0)).isoformat()}
				   for t in resultSet]
		return results


def get_weekly_tasks(user_id, request):
	with engine.connect() as conn:
		done = request.args.get('done')
		all = request.args.get('all')
		parent_ids = request.args.get('parent_ids')

		# using today's date
		timezone = 'US/Pacific'  # update with user time zone
		monday = this_Monday(timezone)
		date = str(monday)
		stmt = select([weekly_tasks]).filter(weekly_tasks.c.user_id == user_id)

		if all == None and parent_ids == None:
			stmt = stmt.filter(weekly_tasks.c.Monday == date)
		if done != None:
			stmt = stmt.filter(weekly_tasks.c.done == done)
		if parent_ids != None:
			stmt = stmt.filter(weekly_tasks.c.parent_id.in_(parent_ids.split(",")))

		stmt = stmt.order_by(weekly_tasks.c.priority)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'name': t['name'], 'why': t['why'], 'priority': t['priority'],
					'Monday': t['Monday'], 'start_date': t['start_date'], 'duration': t['duration'],
					'due_date': t['due_date'], 'done': t['done'],
					'parent_id': t['parent_id'], 'parent_table': t['parent_table'],
					'start': (t['Monday'] - datetime.timedelta(days=1)).isoformat(),
					'end': (t['Monday'] - datetime.timedelta(days=1)).isoformat()}
				   for t in resultSet]
		return results


def get_daily_tasks(user_id, request):
	with engine.connect() as conn:
		done = request.args.get('done')
		all = request.args.get('all')
		parent_ids = request.args.get('parent_ids')

		# using today's date
		timezoneU = 'US/Pacific'
		today = get_localDate(timezoneU)
		date = str(today)
		stmt = select([daily_tasks]).filter(daily_tasks.c.user_id == user_id)

		if all == None and parent_ids == None:
			stmt = stmt.filter(daily_tasks.c.date_local == date)
		if done != None:
			stmt = stmt.filter(daily_tasks.c.done == done)
		if parent_ids != None:
			stmt = stmt.filter(daily_tasks.c.parent_id.in_(parent_ids.split(",")))

		stmt = stmt.order_by(daily_tasks.c.priority)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		r = []
		for t in resultSet:
			dct = {}
			for key in daily_tasks.c.keys():
				dct[key] = getattr(t, key)

			if dct['start_time'] is None:
				dct['start_time'] = datetime.datetime(2000, 1, 1)
			r.append(dct)

		results = [{'id': t['id'], 'name': t['name'], 'why': t['why'], 'priority': t['priority'],
					'date_local': t['date_local'], 'duration': t['duration'], 'done': t['done'],
					'parent_id': t['parent_id'],
					'start': (t['start_time'] - datetime.timedelta(hours=0)).isoformat(),
					'end': (t['start_time'] + datetime.timedelta(hours=1)).isoformat()}
				   for t in r]
		return results


def get_tasks_daily_summary(user_id, request):
	with engine.connect() as conn:
		timezoneU = 'US/Pacific'
		local_date = get_localDate(timezoneU)

		stmt = select([daily_tasks]).filter(
			and_(daily_tasks.c.user_id == user_id, daily_tasks.c.date_local < local_date))

		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'name': t['name'], 'date': t['date_local'], 'why': t['why'],
					'priority': t['priority'], 'done': t['done'], 'type': 'Daily'}
				   for t in resultSet]

		return sorted(results, key=lambda item: (item['date'], -item['priority']), reverse=True)


def get_tasks_weekly_summary(user_id, request):
	with engine.connect() as conn:
		monday = this_Monday()
		Monday = str(monday)

		stmt = select([weekly_tasks]).filter(
			and_(weekly_tasks.c.user_id == user_id, weekly_tasks.c.Mondayof_week < Monday))

		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'name': t['name'], 'date': t['Mondayof_week'], 'why': t['why'],
					'priority': t['priority'], 'done': t['done'], 'type': 'Weekly'}
				   for t in resultSet]

		return sorted(results, key=lambda item: (item['date'], -item['priority']), reverse=True)


def update_task(content):
	with engine.connect() as conn:
		task_id = content['id']
		table = daily_tasks
		if content['table'] == 'weekly':
			table = weekly_tasks
		if content['table'] == 'monthly':
			table = monthly_goals
		content.pop('table')
		stmt = update(table).where(table.c.id == task_id).values(**content)
		conn.execute(stmt)

		results = {'task_id': task_id}
		return results


def delete_task(task_id, table_name):
	with engine.connect() as conn:
		table = daily_tasks
		if table_name == 'weekly':
			table = weekly_tasks
		if table_name == 'monthly':
			table = monthly_goals
		stmt = delete(table).where(table.c.id == task_id)
		conn.execute(stmt)

		results = {'task_id': task_id}
		return results


def get_taskName(task_id, table):
	with engine.connect() as conn:
		task_name = ''
		query = 'SELECT name FROM ' + table + ' where id=' + str(task_id)
		results = conn.execute(query)
		resultSet = results.fetchall()
		if resultSet:
			task_name = resultSet[0][0]
		return task_name


def add_task_priority(coach, userIn, priority):
	table = coach.table
	user_id = coach.user_id
	task=userIn.replace("I want to ", "")
	task=task.replace("i want to ", "")
	task=task.replace("I need to ", "")
	if table == "daily_tasks":
		coach.task_id = add_task(user_id, task, priority, table, coach.date)
	elif table == "weekly_tasks":
		coach.task_id = add_task(user_id, task, priority, table, coach.Monday)
	elif table == "monthly_goals":
		coach.task_id = add_task(user_id, task, priority, table, coach.firstDay_month)
	coach.task_ids[coach.interval][priority-1] = coach.task_id


def update_priority(id, priority, table):
	with engine.connect() as conn:
		query = 'UPDATE ' + table + ' SET priority =' + str(priority) + ' WHERE id =' + str(id) + ';'
		conn.execute(query)


def get_task(user_id, date, priority, table):
	with engine.connect() as conn:
		query = 'SELECT id, name, priority FROM ' + table + ' where user_id=' + str(user_id) + \
				' and priority=' + str(priority)
		if (table == "daily_tasks"):
			query = query + ' and date_local="' + str(date) + '";'
		elif (table == "weekly_tasks"):
			query = query + ' and Monday="' + str(date) + '";'
		elif (table == "monthly_goals"):
			query = query + ' and firstDay_month="' + str(date) + '" order by priority' + ';'
		# print("in get_task, query=", query)
		results = conn.execute(query)
		resultSet = results.fetchall()
		return resultSet


def get_tasks(user_id, date, table):
	with engine.connect() as conn:
		query = 'SELECT id, name, priority FROM ' + table + ' where user_id=' + str(user_id)
		if (table == "daily_tasks"):
			query = query + ' and date_local="' + str(date) + '" order by priority' + ';'
		elif (table == "weekly_tasks"):
			query = query + ' and Monday="' + str(date) + '" order by priority' + ';'
		elif (table == "monthly_goals"):
			query = query + ' and firstDay_month="' + str(date) + '" order by priority' + ';'
		# print("in get_tasks, query=", query)
		results = conn.execute(query)
		resultSet = results.fetchall()
		return resultSet

def get_tasks_notDone(user_id, date, table):
	done=0
	with engine.connect() as conn:
		query = 'SELECT id, name, priority FROM ' + table + ' where user_id=' + str(user_id)+' and done='+ str(done)
		if (table == "daily_tasks"):
			query = query + ' and date_local="' + str(date) + '"'
		elif (table == "weekly_tasks"):
			query = query + ' and Monday="' + str(date) + '"'
		elif (table == "monthly_goals"):
			query = query + ' and firstDay_month="' + str(date) + '"'
		query = query +' order by priority;'
		# print("in get_tasks, query=", query)
		results = conn.execute(query)
		resultSet = results.fetchall()
		return resultSet


def add_childTask(user_id, parent_id, parentTable, task, priority, child_table, startingDate):
	table=child_table
	with engine.connect() as conn:
		taskSQL = '"' + task + '"'
		parentTableSQL='"' + parentTable+ '"'

		query = 'insert into ' + child_table
		cols=' (user_id, parent_id, parent_table, name, priority, created, updated,'
		values = ' values (' + str(user_id) + ', '+ str(parent_id)  + ', ' + parentTableSQL+ ', ' + taskSQL + ', ' + str(priority) + ', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), '
		if table == "daily_tasks":
			cols=cols + ' date_local)'
		elif table == "weekly_tasks":
			cols=cols + ' Monday)'
		elif table == "monthly_goals":
			cols=cols + ' firstDay_month)'
		else:
			return 0
		values=values+ '"'+str(startingDate)+'")'
		query = query + cols + values
		query = query + " RETURNING " + table + ".id"+ ';'
		results = conn.execute(query)
		resultSet = results.fetchall()
		id = resultSet[0][0]
		print("added child task, id=", id)
		return id
#add_childTask(4,31,"monthly_goals", "child_task2", 2, "weekly_tasks","2022-07-10")


def add_task(user_id, task, priority, table, startingDate):
	#print ("Begin add task",task, "to table ",table)
	with engine.connect() as conn:
		taskSQL = '"' + task + '"'

		query = 'insert into ' + table
		cols=' (user_id, name, priority, created, updated, '
		values = ' values (' + str(user_id) + ', ' + taskSQL + ', ' + str(priority) + ', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), '
		if table == "daily_tasks":
			cols=cols + ' date_local)'
		elif table == "weekly_tasks":
			cols=cols + ' Monday)'
		elif table == "monthly_goals":
			cols=cols + ' firstDay_month)'
		values=values+ '"'+str(startingDate)+'")'
		query = query + cols + values
		query = query + " RETURNING " + table + ".id"+ ';'
		results = conn.execute(query)
		resultSet = results.fetchall()
		id = resultSet[0][0]
		print("added task id=", id)
		return id
#add_task(4, "Test add_task", 2, "weekly_tasks")
#add_task(4, "Test add_task1", 2, "monthly_goals","2022-07-10")
#add_task(4, "Test add_task", 2, "daily_tasks")


def update_why(task_id, priority, why, table):
	with engine.connect() as conn:
		query = 'UPDATE ' + table + ' SET why ="' + why + '" WHERE id =' + str(task_id)
		conn.execute(query)


def update_column(task_id, col_name, col_value, table):
	with engine.connect() as conn:
		query = 'UPDATE ' + table + ' SET ' + col_name + '=' + str(col_value) + ' WHERE id =' + str(task_id)
		conn.execute(query)


def update_due_date(task_id, due_date, table):
	with engine.connect() as conn:
		query = 'UPDATE ' + table + ' SET due_date ="' + str(due_date) + '" WHERE id =' + str(task_id)
		conn.execute(query)


def reset_task_table(user_id, theDate, table):
	with engine.connect() as conn:
		print("Reset_table: user_id", user_id, "theDate", theDate, "table", table)
		query = 'delete from ' + table + ' where user_id=' + str(user_id)
		if table == "daily_tasks":
			dateSQL = '"' + str(theDate) + '"'
			query += ' and date_local=' + dateSQL
		else:
			# query += ' and date_local=' + dateSQL
			pass
		query += ';'
		conn.execute(query)


def get_events(user_id):
	with engine.connect() as conn:
		stmt = select([events]).filter(events.c.user_id == user_id)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'title': t['title'], 'description': t['description'],
					'daily_task_id': t['daily_task_id'], 'weekly_task_id': t['weekly_task_id'],
					'monthly_goal_id': t['monthly_goal_id'], 'color': t['color'],
					'start': t['start_time'].isoformat(), 'end': t['end_time'].isoformat()}
				   for t in resultSet]
		return results


def delete_event(event_external_id):
	with engine.connect() as conn:
		stmt = "delete from events where event_external_id='" + str(event_external_id) + "'"
		conn.execute(stmt)


def add_event(event_content):
	with engine.connect() as conn:
		event_content['created'] = nowString()
		event_content['updated'] = nowString()
		stmt = insert(events).values(**event_content)
		result = conn.execute(stmt)
		id = result.lastrowid

		results = id
		return results


def get_event_by_external_id(event_external_id):
	with engine.connect() as conn:
		stmt = select([events]).filter(events.c.event_external_id == event_external_id)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': t['id'], 'title': t['title'], 'description': t['description'],
					'daily_task_id': t['daily_task_id'], 'weekly_task_id': t['weekly_task_id'],
					'monthly_goal_id': t['monthly_goal_id'], 'color': t['color'],
					'start_time': t['start_time'], 'end_time': t['end_time'],
					'start': t['start_time'].isoformat(), 'end': t['end_time'].isoformat()}
				   for t in resultSet]
		return results


def update_event(content):
	with engine.connect() as conn:
		stmt = update(events).where(events.c.id == content['id']).values(**content)
		conn.execute(stmt)

		results = {}
		return results


def remove_event(event_id):
	with engine.connect() as conn:
		stmt = delete(events).where(events.c.id == event_id)
		conn.execute(stmt)
