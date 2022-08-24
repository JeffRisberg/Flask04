import datetime
from sqlalchemy import insert, update
from sqlalchemy.sql import select

from src import engine, metadata

companies = metadata.tables['companies']
teams = metadata.tables['teams']
users = metadata.tables['users']
jobs = metadata.tables['jobs']
conversation_history = metadata.tables['conversation_history']


def nowString():
	now = datetime.datetime.now()
	nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
	return nowStr


def get_companies():
	with engine.connect() as conn:
		stmt = select([companies])
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [{'id': u.id, 'name': u.name, 'created_at': str(u.created_at)}
				   for u in resultSet]
		return results


def get_teams(company_id=1):
	with engine.connect() as conn:
		stmt = select([teams])
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [{'id': u.id, 'name': u.name, 'mascot': u.mascot, 'created_at': str(u.created_at)}
				   for u in resultSet]
		return results


def get_team_by_id(id, company_id=1):
	with engine.connect() as conn:
		stmt = select([teams]).filter(teams.c.id == id)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [{'id': u.id, 'name': u.name, 'mascot': u.mascot, 'created_at': str(u.created_at)}
				   for u in resultSet]
		return results


def get_team_by_name(name, company_id=1):
	with engine.connect() as conn:
		stmt = select([teams]).filter(teams.c.name == name)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [{'id': u.id, 'name': u.name, 'mascot': u.mascot, 'created_at': str(u.created_at)}
				   for u in resultSet]
		return results


def get_jobs(company_id=1):
	with engine.connect() as conn:
		stmt = select([jobs]).filter(jobs.c.company_id == company_id)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [
			{'id': u.id, 'teamName': u.name, 'teamId': u.team_id, 'firstName': u.first_name, 'lastName': u.last_name,
			 'email': u.email, 'title': u.title, 'created_at': str(u.created_at)}
			for u in resultSet]
		return results


def get_users(company_id=1):
	with engine.connect() as conn:
		join = users.join(jobs, users.c.job_id == jobs.c.id) \
			.join(teams, users.c.team_id == teams.c.id)
		stmt = select([users, jobs.c.title, teams.c.id, teams.c.name]).select_from(join).filter(
			users.c.company_id == company_id)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [
			{'id': u.id, 'team_name': u.name, 'team_id': u.team_id, 'first_name': u.first_name,
			 'last_name': u.last_name,
			 'street_address1': u.street_address1, 'street_address2': u.street_address2,
			 'city': u.city, 'state': u.state, 'zip': u.zip,
			 'email': u.email, 'title': u.title, 'status': u.status, 'created_at': str(u.created_at)}
			for u in resultSet]

		return results


def get_user_by_id(id, company_id=1):
	with engine.connect() as conn:
		join = users.join(jobs, users.c.job_id == jobs.c.id) \
			.join(teams, users.c.team_id == teams.c.id)
		stmt = select([users, jobs.c.title, teams.c.id, teams.c.name]).select_from(join) \
			.filter(users.c.id == id)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [
			{'id': u.id, 'team_name': u.name, 'team_id': u.team_id, 'first_name': u.first_name,
			 'last_name': u.last_name,
			 'street_address1': u.street_address1, 'street_address2': u.street_address2,
			 'city': u.city, 'state': u.state, 'zip': u.zip,
			 'email': u.email, 'title': u.title, 'status': u.status, 'created_at': str(u.created_at)}
			for u in resultSet]
		return results


def get_user_by_email(email, company_id=1):
	with engine.connect() as conn:
		join = users.join(jobs, users.c.job_id == jobs.c.id) \
			.join(teams, users.c.team_id == teams.c.id)
		stmt = select([users, jobs.c.title, teams.c.id, teams.c.name]).select_from(join) \
			.filter(users.c.email == email)
		query = conn.execute(stmt)

		resultSet = query.fetchall()
		results = [
			{'id': u.id, 'team_name': u.name, 'team_id': u.team_id, 'first_name': u.first_name,
			 'last_name': u.last_name,
			 'street_address1': u.street_address1, 'street_address2': u.street_address2,
			 'city': u.city, 'state': u.state, 'zip': u.zip,
			 'email': u.email, 'title': u.title, 'status': u.status, 'created_at': str(u.created_at)}
			for u in resultSet]
		return results


def get_userName(user_id):
	with engine.connect() as conn:
		query = 'SELECT first_name, last_name FROM users where id=' + str(user_id)
		results = conn.execute(query)
		resultSet = results.fetchall()
		firstName = resultSet[0][0]
		return firstName


def update_user(content):
	with engine.connect() as conn:
		stmt = update(users).where(users.c.id == content['id']).values(**content)
		conn.execute(stmt)

		results = {}
		return results


def create_user(content):
	with engine.connect() as conn:
		content['company_id'] = 1
		content['team_id'] = 1
		content['job_id'] = 1
		content['timezone'] = "US/Pacific"
		content['created_at'] = nowString()
		content['updated_at'] = nowString()
		stmt = insert(users).values(**content)
		result = conn.execute(stmt)
		id = result.lastrowid

		results = id
		return results


# user_id, question, response, ip_address, device_type
def save_conversation(content):
	with engine.connect() as conn:
		stmt = insert(conversation_history).values(**content)
		conn.execute(stmt)
