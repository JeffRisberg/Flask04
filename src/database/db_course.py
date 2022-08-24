import datetime

from src import engine, metadata
from sqlalchemy.sql import select


jobs = metadata.tables['jobs']
courses = metadata.tables['courses']
lessons = metadata.tables['lessons']
users_courses = metadata.tables['users_courses']
users_lessons = metadata.tables['users_lessons']

def nowString():
	now = datetime.now()
	nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
	return nowStr

def get_jobs(company_id):
	with engine.connect() as conn:
		stmt = select([jobs]).filter(jobs.c.company_id == company_id)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'title': item['title'], 'level': item['level']} for item in resultSet]
		return results

def get_courses():
	with engine.connect() as conn:
		stmt = select([courses])
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': c.id, 'name': c.name, 'description': c.description, 'created_at': c.created_at}
				   for c in resultSet]
		return results

def get_lessons(course_id):
	with engine.connect() as conn:
		stmt = select([lessons]).filter(lessons.c.course_id == course_id)
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': c.id, 'name': c.name, 'description': c.description, 'created_at': c.created_at}
				   for c in resultSet]
		return results

def get_popular_courses():
	with engine.connect() as conn:
		stmt = "SELECT id, name, count(*) as count FROM users_courses LEFT JOIN courses on courses.id = users_courses.course_id GROUP BY course_id"
		query = conn.execute(stmt)
		resultSet = query.fetchall()
		results = [{'id': c.id, 'name': c.name, 'count': c['count']} for c in resultSet]
		return results
