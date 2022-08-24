import datetime
from src import engine, metadata

from . db_course import get_lessons

courses = metadata.tables['courses']
lessons = metadata.tables['lessons']
users_courses = metadata.tables['users_courses']
users_lessons = metadata.tables['users_lessons']

def nowString():
	now = datetime.datetime.now()
	nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
	return nowStr

def get_selected_courses(user_id):
	conn = engine.connect()
	query = 'SELECT courses.id, courses.name, courses.total_time FROM users_courses INNER JOIN courses ON users_courses.user_id=' +str(user_id)+' and users_courses.course_id=courses.id;'
	results = conn.execute(query)
	resultSet = results.fetchall()
	conn.close()
	return resultSet

def add_course(user_id, course_id):
	with engine.connect() as conn:
		nowStr = nowString ()
		nowStrSQL = '"'+nowStr+'"'
		query = 'insert into users_courses (user_id, course_id,status, created_at, updated_at) values (' \
				+ str(user_id) + ', ' + str(course_id) + ', "requested",'+nowStrSQL+ ', '+nowStrSQL+');'
		conn.execute(query)

def add_selection(user_id, userIn):
	if (userIn.isdigit()):
		course_id = userIn
		add_course(user_id, course_id)
	else:
		userInput = userIn.lower()
		courses=["advanced databases", "natural language processing", "machine learning", "time management", "public speaking"]
		for i in range(len(courses)):
			course = courses[i]
			if (course in userInput):
				course_id = i+1
				add_course(user_id, course_id)

#remove this function after coach_schedule replaces coach.py
def add_choice(user_id, userIn):
	if (userIn.isdigit()):
		course_id = userIn
		add_course(user_id, course_id)
	else:
		userInput = userIn.lower()
		courses=["advanced databases", "natural language processing", "machine learning", "time management", "public speaking"]
		for i in range(len(courses)):
			course = courses[i]
			if (course in userInput):
				course_id = i+1
				add_course(user_id, course_id)

def selected_courses(user_id):
	resultSet = get_selected_courses(user_id)
	choices = []
	for item in resultSet:
		id = item[0]
		name = item[1]
		length = item[2]
		choice = {'id': id, 'name': name, 'length': length}
		choices.append(choice)
	return choices

def schedule_lesson(user_id, course_id, lesson_id, theDay):
	with engine.connect() as conn:
		scheduledStart = str(theDay) # + " 17:00:00"
		scheduledStartSQL = '"' + scheduledStart + '"'
		scheduledEnd = str(theDay) # + " 18:00:00"
		scheduledEndSQL = '"' + scheduledEnd + '"'
		nowSQL = '"' + nowString() + '"'
		query = 'insert into users_lessons (user_id, course_id, lesson_id, scheduled_start, scheduled_end, created_at, updated_at) values (' + str(user_id) + ', ' + str(course_id) + ', ' + str(lesson_id)+ ',' + scheduledStartSQL + ',' + scheduledEndSQL + ', '+nowSQL+ ', '+nowSQL + ');'
		conn.execute(query)

#based on the courses the user currently selected, build a lesson plan,
#insert into users_lessons table
def create_schedule(user_id):
	today = datetime.datetime.now()
	lessonDay = today
	courses = get_selected_courses(user_id)
	for course in courses:
		course_id = course['id']
		lessons = get_lessons(course_id)
		for lesson in lessons:
			lesson_id = lesson['id']
			schedule_lesson(user_id, course_id, lesson_id, lessonDay)
			lessonDay = lessonDay + datetime.timedelta(days=7)

def get_schedule(user_id):
	with engine.connect() as conn:
		results = conn.execute('SELECT users_lessons.*, lessons.*, courses.name as course_name FROM users_lessons '
							   'LEFT JOIN lessons ON lessons.id = users_lessons.lesson_id '
							   'LEFT JOIN courses ON courses.id = lessons.course_id '
							   'WHERE user_id = ' + str(user_id))
		resultSet = results.fetchall()

		schedule_items = [{'id': item['id'], 'courseName': item['course_name'],
						 'lessonName': item['name'], 'description': item['description'],
						 'scheduledStart' : item['scheduled_start']} for item in resultSet]
		return schedule_items

def reset_user_course(user_id):
	with engine.connect() as conn:
		query = 'delete from users_courses where user_id='+str(user_id)+';'
		conn.execute(query)
		query ='delete from users_lessons where user_id='+str(user_id)+';'
		conn.execute(query)
		query ='INSERT INTO users_courses values (2, 1, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());'
		conn.execute(query)
		query ='INSERT INTO users_courses values (2, 2, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());'
		conn.execute(query)
		query ='INSERT INTO users_courses values (2, 3, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());'
		conn.execute(query)
