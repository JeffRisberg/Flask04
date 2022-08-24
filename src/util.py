from typing import Optional
import calendar
import datetime
import numpy as np
import re
import string  # used for user input cleanup
from pytz import timezone
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class UserInputError(Exception):
	"""No input entered error; message can be printed"""


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


def get_weeks(year, month):
	Calendar = calendar.Calendar(firstweekday=0)
	weeksOfMonth = Calendar.monthdatescalendar(year, month)

	firstDayOfMonth = datetime.date(year, month, 1)
	firstWeekday = firstDayOfMonth.weekday()  # weekday of July 1st
	lastDay = calendar.monthrange(year, month)[1]
	lastDayofMonth = datetime.date(year, month, lastDay)
	lastWeekday = lastDayofMonth.weekday()  # Weekday of 7/31

	if (firstWeekday > 3):  # 3 is Thursday, the middle of the week, not planning that week
		weeksOfMonth = weeksOfMonth[1:]
	if (lastWeekday < 3):  # 3 is Thursday, the middle of the week
		weeksOfMonth = weeksOfMonth[:-1]  # remove the last week

	return weeksOfMonth


def get_Mondays(year, month):
	weeks = get_weeks(year, month)
	Mondays = []
	for i in range(len(weeks)):
		Monday = weeks[i][0]
		monthName = Monday.strftime('%B')
		MondayName = monthName + ' ' + str(Monday.day)
		Mondays.append([Monday, MondayName])  # each element is a list of Monday datetime object, and the name
	return Mondays

def get_weekDates(year, month, day):
	weekDates = []
	today = datetime.date(year, month, day)
	Monday = today - datetime.timedelta(days=today.weekday())
	weekDates.append(Monday)
	for i in range(6):
		nextDay = Monday + datetime.timedelta(days=i + 1)
		weekDates.append(nextDay)
	return weekDates


def get_nonzeros(theList):
	return list(filter(lambda x: x > 0, theList))


# get integer year and month from string
def get_year_month(dateStr):
	dateArray = dateStr.split('-')
	year = dateArray[0]
	month = dateArray[1]
	return int(year), int(month)


# return 1 if there is real intent, 0 of no intent (no task)
def get_intent(userIn, app):
	use_hugging_face = app.config['use_hugging_face']
	print("use_hugging_face", use_hugging_face)

	if use_hugging_face:
		preTrained = "bert-base-uncased"
		tokenizer = AutoTokenizer.from_pretrained(preTrained)
		saved_model = AutoModelForSequenceClassification.from_pretrained("../models/intent_model")

		inputs = tokenizer([userIn], padding=True, truncation=True, return_tensors="pt")
		outputs = saved_model(**inputs)
		logits = outputs.logits.detach().numpy()[0]  # take the first argument
		prediction = np.argmax(logits)
		return prediction
	else:
		userIn = userIn.lower()
		result = 1
		if "none" in userIn:
			result = 0
		if "enough" in userIn:
			result = 0
		if "done" in userIn:
			result = 0
		return result


"""
userIn="Create powerpoint slides"
print(userIn, get_intent(userIn))
userIn="None"
print(userIn, get_intent(userIn))

userIn="I want to finish the pitch deck"
print(userIn, " get_intent=", get_intent(userIn))
userIn="nothing"
print(userIn, " get_intent=", get_intent(userIn))
"""


# sentiment_model is trained by the file fineTune_model.py
def get_sentiment(userIn, app):
	use_hugging_face = app.config['use_hugging_face']
	print("use_hugging_face", use_hugging_face)

	if use_hugging_face:
		preTrained = "distilbert-base-uncased-finetuned-sst-2-english"
		tokenizer = AutoTokenizer.from_pretrained(preTrained)
		saved_model = AutoModelForSequenceClassification.from_pretrained("../models/sentiment_model")

		inputs = tokenizer([userIn], padding=True, truncation=True, return_tensors="pt")
		outputs = saved_model(**inputs)
		logits = outputs.logits.detach().numpy()[0]
		prediction = np.argmax(logits)
		if (prediction == 0):
			return "NEGATIVE"
		else:
			return "POSITIVE"
	else:
		if "no" in userIn:
			return "NEGATIVE"
		else:
			return "POSITIVE"


# get a list of variables
def get_variables(text):
	results = []
	index = 0
	while True:
		first_index = text.find('*', index)
		if first_index >= 0:
			last_index = text.find('*', first_index + 1)
			var_name = text[first_index + 1: last_index]
			results.append(var_name)
			index = last_index + 1
		else:
			break
	return results


def replace_variable(text, var_name, entity):
	if ("task" in var_name):
		entity = "'" + entity + "'"
	return text.replace("*" + var_name + "*", entity)


# Assume the user answers "5 am" or "5am", "12 pm", "11pm"
def extract_time(userIn):
	userIn = userIn.lower()
	# print("in extract_time, userIn=",userIn)
	am_pm = ''
	hour, minute = -1, -1
	hours, minutes = '', ''
	words = userIn.split()
	for i in range(len(words)):
		word = words[i].strip()  # remove space at both ends
		if (word.isdigit()):  # there is no ":"
			hour = int(word)
			nextWord = words[i + 1]
			if (nextWord == 'am' or nextWord == 'pm'):
				am_pm = nextWord
		elif (len(word) > 2):  # 7pm or 7:45pm or 7:45
			last2char = word[-2:]
			firstChars = word[:-2]
			if ((last2char in ['am', 'pm']) and ((':' in firstChars) or firstChars.isdigit())):
				am_pm = last2char
				if (firstChars.isdigit()):  # it must be hours
					hour = int(firstChars)
				else:  # (':' in firstChars)
					hours, minutes = firstChars.split(':')
					if (hours.isdigit() and minutes.isdigit()):
						hour = int(hours)  # no need to assign minutes, which is a string
			elif (':' in word):
				hours, minutes = word.split(':')
				if (hours.isdigit() and minutes.isdigit()):
					hour = int(hours)  # no need to assign minutes, which is a string
					nextWord = words[i + 1]
					if (nextWord == 'am' or nextWord == 'pm'):
						am_pm = nextWord
	if (not am_pm):
		am_pm = 'am'
	return hour, minutes, am_pm


def update_time(userIn: str, currentDate: datetime.datetime) -> datetime.datetime:
	"""Interprets userIn as a datetime relative to current date.
    :param userIn: A user-inputted American English string representing a datetime.
    :param currentDate: The datetime representing the current time.
    :return: datetime object representing userIn time.
    """

	userIn = userIn.lower().replace(" ", "")
	atLocation = re.search("at", userIn)
	newHour = 0

	if atLocation:
		userIn = userIn[atLocation.start():]
		timeLocation = re.findall("[0-9]+", userIn)
		suffixLocation = re.search("pm|am", userIn)

		if timeLocation and suffixLocation:
			if userIn[suffixLocation.start():suffixLocation.end()] == "pm":
				newHour += 12
			newHour += int(timeLocation[0])

	if newHour > 23:
		raise UserInputError("Invalid value range for datetime object")

	userInDate = currentDate.replace(hour=newHour, minute=0, second=0, microsecond=0)
	return userInDate


def extract_date_logic(userIn: str, currentDate: datetime.datetime) -> Optional[datetime.datetime]:
	"""Returns the datetime based on user input
	:param userIn: Input entered to parse
	:param currentDate: The current date to update
	:return: The updated date
	:raises: UserInputError: Used when checking if input was entered
	:raises: ValueError: Used when checking the value type
	"""

	if len(userIn) == 0:
		raise UserInputError("No input entered")

	weekDict = {
		"mon": 0,
		"tue": 1,
		"wed": 2,
		"thu": 3,
		"fri": 4,
		"sat": 5,
		"sun": 6,
	}
	monthDict = {
		"jan": 1,
		"feb": 2,
		"mar": 3,
		"apr": 4,
		"may": 5,
		"jun": 6,
		"jul": 7,
		"aug": 8,
		"sep": 9,
		"oct": 10,
		"nov": 11,
		"dec": 12,
	}
	timeZoneU = 'US/Pacific'  # pacific time zone (potentially allow users to pick time zones)
	userIn = userIn.replace(" ", "").lower()  # remove the spaces from the user's input and make it all lower case
	validFormat1 = re.search("(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", userIn)  # check if valid date format
	validFormat2 = re.search("(\d{1,2})[/.-](\d{1,2})[/.-](\d{2})", userIn)  # check if valid date format
	formatOutput1 = "%m/%d/%Y"
	formatOutput2 = "%m/%d/%y"

	if re.search("today", userIn):  # check if user wants to schedule for today
		result = currentDate

	elif re.search("tomorrow", userIn):  # check if the user wants to schedule for tomorrow
		tomorrowDate = currentDate + datetime.timedelta(days=1)
		result = tomorrowDate

	elif re.search("mon|tue|wed|thu|fri|sat|sun", userIn) and not re.search("next", userIn) and not re.search(
		"week|wk|month", userIn):
		dayLocation = re.search("mon|tue|wed|thu|fri|sat|sun", userIn)
		weekDay = currentDate.weekday()  # get the current day of the week
		weekDay -= weekDict.get(userIn[dayLocation.start():dayLocation.end()])
		if weekDay > 0:
			weekDay -= 7
		result = currentDate - datetime.timedelta(days=weekDay)

	elif re.search("next", userIn) and not re.search("week|wk|month", userIn):  # check for next weekday
		weekDayLocation = re.search("mon|tue|wed|thu|fri|sat|sun", userIn)  # check for specified week day name
		if weekDayLocation:
			weekDay = currentDate.weekday()  # get the current day of the week
			weekDay -= weekDict.get(userIn[weekDayLocation.start():weekDayLocation.end()])
			if weekDay > 0:
				weekDay -= 7
			result = currentDate + datetime.timedelta(days=7) - datetime.timedelta(days=weekDay)
		else:
			result = None  # if no week day name was given default to None

	elif not re.search("end", userIn) and re.search("nextweek|nextwk|nxtwk",
													userIn):  # check if user wants to schedule for next week (same day)
		nextWeekDate = currentDate + datetime.timedelta(days=7)
		result = nextWeekDate

	elif re.search("weekafternext|wkafternext|wkafternxt",
				   userIn):  # check if user wants to schedule for the week after next
		followingWeek = currentDate + datetime.timedelta(days=14)
		result = followingWeek

	elif re.search("nextmonth|nxtmnth", userIn):  # check if user wants to schedule for next month
		nextMonth = currentDate + datetime.timedelta(calendar.mdays[currentDate.month])
		result = nextMonth

	elif validFormat1:  # check if the user entered some valid date (06/08/2022)
		userIn = userIn.replace("-", "/")
		userIn = userIn.replace(".", "/")
		digits = userIn[validFormat1.start():validFormat1.end()]
		result = datetime.datetime.strptime(digits, formatOutput1)

	elif validFormat2:  # check if the user entered some valid date (06/08/22)
		userIn = userIn.replace("-", "/")
		userIn = userIn.replace(".", "/")
		digits = userIn[validFormat2.start():validFormat2.end()]
		result = datetime.datetime.strptime(digits, formatOutput2)

	elif re.search("endof", userIn) or re.search("lastday",
												 userIn):  # check if user requested at the end of a specified month
		monthLocation = re.search("jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", userIn)
		weekLocation = re.search("week", userIn)
		thisMonth = re.search("month", userIn)
		year = currentDate.year

		if thisMonth:
			last_day_of_month = calendar.monthrange(year, currentDate.month)
			result = currentDate - datetime.timedelta(days=currentDate.day) + datetime.timedelta(
				days=last_day_of_month[1])

		elif monthLocation:
			monthString = userIn[monthLocation.start():monthLocation.end()]
			if monthDict.get(monthString) < currentDate.month:  # update year if month has past
				year += 1

			last_day_of_month = calendar.monthrange(year, monthDict.get(monthString))[1]
			result = datetime.datetime.strptime(str(last_day_of_month) + monthString + str(year), "%d%b%Y")

		elif weekLocation:
			newDay = weekDict.get('sun')
			result = currentDate - datetime.timedelta(days=currentDate.weekday()) + datetime.timedelta(days=newDay)
			if re.search("next", userIn):
				result += datetime.timedelta(days=7)
		else:
			result = None

	elif re.search("jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", userIn) and re.findall("[0-9]+", userIn):
		year = currentDate.year  # get the current year

		monthLocation = re.search("jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", userIn)
		monthString = userIn[monthLocation.start():monthLocation.end()]  # get the month string

		dayObject = re.findall("[0-9]+", userIn)  # safer to search for first digit set
		day = dayObject[0]  # get the day string

		if monthDict.get(monthString) < currentDate.month:  # update year if month has past
			year += 1

		try:
			datetime.datetime.strptime(day + monthString + str(year), "%d%b%Y")
		except ValueError as e:
			print("ValueError: {}".format(e))
			result = None
		else:
			result = datetime.datetime.strptime(day + monthString + str(year), "%d%b%Y")

	else:  # default check if the user entered a specific month's name
		monthLocation = re.search("jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", userIn)
		year = currentDate.year
		day = "1"

		if monthLocation:
			monthString = userIn[monthLocation.start():monthLocation.end()]

			if monthDict.get(monthString) < currentDate.month:  # update year if month has past
				year += 1

			result = datetime.datetime.strptime(day + monthString + str(year), "%d%b%Y")
		else:
			result = None

	if result is None:
		return result

	try:
		result = update_time(userIn, result)
	except UserInputError as e:
		print("ValueError: {}".format(e))

	return result  # datetime object format: yyyy-mm-dd tt:tt:tt


def extract_date(userIn: str) -> Optional[datetime.datetime]:
	timeZoneU = 'US/Pacific'  # pacific time zone (potentially allow users to pick time zones)
	today = datetime.datetime.today().astimezone(
		timezone(timeZoneU))  # variable to be used for the current date (today)
	currentDate = datetime.datetime(today.year, today.month, today.day)  # default time to 00:00:00
	try:
		return extract_date_logic(userIn, currentDate)
	except UserInputError as e:
		print("UserInputError: {}".format(e))
		return None


def convert_to_Timestamp(hour, minutes, am_pm):
	# print("being convert_to_Timestamp, am_pm=",am_pm)
	timestamp = ''
	if (hour > 0):
		if (not minutes):  # empty string
			minutes = '00'

		if (am_pm == 'pm'):
			if (hour < 12):
				hour = hour + 12

		timestamp = str(hour) + ':' + minutes + ':00'
	# returns an empty string if not detecting any number
	return timestamp


def get_timeFormat(userIn):
	hour, minutes, am_pm = extract_time(userIn)
	return convert_to_Timestamp(hour, minutes, am_pm)


"""
#print(get_timestamp('7:45pm'))
#print(get_timestamp('8pm'))
19:45
20:00
17:00

print(get_timeFormat('4:05 am'))
print(get_timeFormat('5 pm'))
print(get_timeFormat('6:00pm'))
"""

"""
# verifies if it is a valid time (military time)
def validate_time(time):
    hours = int(time.split(':')[0])
    minutes = int(time.split(':')[1])
    if minutes > 59:
        minutes = 59
    return [hours, minutes]
"""


def duration_parser(userInput: str) -> list:
	conversionDictionary = {
		"one": 1,
		"two": 2,
		"three": 3,
		"four": 4,
		"five": 5,
		"six": 6,
		"seven": 7,
		"eight": 8,
		"nine": 9,
		"ten": 10,
		"eleven": 11
	}

	# initialize different variables being used
	hour = 0
	minutes = 0
	time = ""

	# remove starting/leading white spaces
	userInput = userInput.replace(" ", "").lower().lstrip("0")

	hour_exists = re.search("hours|hour|hrs|hr", userInput)
	minute_exists = re.search("minutes|minute|mins|min", userInput)

	if hour_exists and minute_exists:
		loc_hour = [hour_exists.start(), hour_exists.end()]
		loc_min = [minute_exists.start(), minute_exists.end()]

		hour_match = re.findall("\d+", userInput[0:loc_hour[0]])
		minute_match = re.findall("\d+", userInput[loc_hour[1]:loc_min[0]])
		if hour_match:
			hour = int(hour_match[0])
		if minute_match:
			minutes = int(minute_match[0])
		time = str(hour) + ":" + str(minutes)
	elif hour_exists:
		loc_hour = [hour_exists.start(), hour_exists.end()]

		hour_match = re.findall("\d+", userInput[0:loc_hour[0]])
		string_number = re.search("one|two|three|four|five|six|seven|eight|nine|ten|eleven", userInput[0:loc_hour[0]])
		if hour_match:
			hour = int(hour_match[0])
		elif re.search("halfa", userInput[0:loc_hour[0]]):
			minutes = 30
		elif re.search("onehalf", userInput[0:loc_hour[0]]):
			minutes = 30
		elif string_number and re.search("half", userInput):
			hour = conversionDictionary.get(userInput[string_number.start():string_number.end()])
			minutes = 30
		elif re.search("half", userInput):
			minutes = 30
		elif string_number:
			hour = conversionDictionary.get(userInput[string_number.start():string_number.end()])
		time = str(hour) + ":" + str(minutes)
	elif minute_exists:
		loc_min = [minute_exists.start(), minute_exists.end()]
		string_number = re.search("one|two|three|four|five|six|seven|eight|nine|ten|eleven", userInput[0:loc_min[0]])
		minute_match = re.findall("\d+", userInput[0:loc_min[0]])
		if minute_match:
			minutes = int(minute_match[0])
		else:
			minutes = conversionDictionary[userInput[string_number.start():string_number.end()]]
		time = str(hour) + ":" + str(minutes)
	# validate time function to verify if the hours and minutes are within valid boundaries
	# if time:
	#	time = validate_time(time)
	return time


"""
userInput = input("Enter a duration: ")
while userInput != "end":
    print("duration: ", duration_parser(userInput))
    userInput = input("Enter a duration: ")
"""

""" Not used
def this_Monday(timezoneU):
	now = datetime.datetime.now()
	nowU = now.astimezone(timezone(timezoneU))
	todayIndex=nowU.weekday()  # Monday index is 0
	this_Monday = nowU - datetime.timedelta(days=todayIndex)  #this returns seconds
	this_MondayStr=this_Monday.strftime('%Y-%m-%d')
	return this_MondayStr
"""

if __name__ == '__main__':
	year = 2002
	month = 6
	weeks = get_weeks(year, 7)
	print(weeks)
	print(get_Mondays(year, month))
