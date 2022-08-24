import os

import pandas as pd
import torch
import json

from datasets import Dataset
from transformers import AutoTokenizer, AutoModel

from src.util import *
from ..database import *


os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# return a dataframe that we can use later
def load_pathways():
	df = pd.read_csv('./data/pathways.csv', sep='|')
	df['description'] = df['short_description'] + df['long_description']
	return df


df = load_pathways()
pathData = Dataset.from_pandas(df)
# print(pathData)

preTrained = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
tokenizer = AutoTokenizer.from_pretrained(preTrained)
model = AutoModel.from_pretrained(preTrained)

device = torch.device("cpu")
model.to(device)


# get embedding of the first token, the output is a Torch tensor
def get_embeddings(text_list):
	encoded_input = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt")
	encoded_input = {k: v.to(device) for k, v in encoded_input.items()}
	output = model(**encoded_input)
	clsEmbedding = output.last_hidden_state[:, 0]
	return clsEmbedding


# embedding = get_embeddings(pathData['description'][0])
# print(embedding.shape)
# add "embedding" column to the data
pathDataset = pathData.map(lambda x: {"embeddings": get_embeddings(x["description"]).detach().cpu().numpy()[0]})
pathDataset.add_faiss_index(column="embeddings")


def find_suggested_pathway(pathDataset, userIn):
	embeddingQ = get_embeddings([userIn]).cpu().detach().numpy()
	scores, samples = pathDataset.get_nearest_examples("embeddings", embeddingQ, k=1)
	result = str(samples['path_name'][0]) + ': ' + str(samples['short_description'][0])
	return result


"""
userIns = ["I want to have more humor.", "I want to become more confident in front of a large audience.", "I want to be more confident.", "I want to be more humorous."]
for userIn in userIns:
	print(userIn)
	print(get_pathway(userIn))
"""


def get_pathway(coach, userIn):
	suggested_path = find_suggested_pathway(pathDataset, userIn)
	coach.suggested_path = suggested_path
	return {}


def record_score(coach, userIn):
	if (userIn.isdigit()):
		coach.levelSum += int(userIn)
		coach.levelCount += 1
	return {}


def schedule(coach, userIn):
	create_schedule(coach.user_id)
	return {}


def show_schedule(coach, userIn):
	response = "text"
	return {'text': response, 'widget': 'schedule'}


def update_content(coach, userIn):
	result = {'widget': 'text_with_content_update', 'content': coach.content_version_count}
	coach.content_version_count += 1
	return result


def default_action(coach, userIn):
	return {}


def no_action(coach, userIn):
	return {}


stateResponse = {
	"standard": {
		"greet": [
			"Welcome! I'll help you to find the best pathway to achieve your goal. Should we start?",
			no_action,
			"Ok, let me know when you are ready.",
			"ask_goal"
		],
		"ask_goal": [
			"What is your goal of learning public speaking?",
			no_action,
			"I can best help you when I understand what you want to achieve. What's your ideal outcome for public speaking?",
			"get_pathway"
		],
		"get_pathway": [
			"Here is the recommended pathway: *suggested_path*",
			get_pathway,
			"Sorry that I didn't get the right pathway for you. Now tell me about your goal again.",
			"assess_Q1"
		],
		"assess_Q1": [
			"Let’s start with some assessment to see where you are. " +
			"From scale 1 to 5, with 5 the most strongly agree, what's your level for the following: " +
			"I am confident and calm when speaking in front of groups.",
			no_action,
			"",
			"assess_Q2"
		],
		"assess_Q2": [
			"From scale 1 to 5, rate the following: " +
			"I understand the structure of a basic speech.",
			record_score,
			"",
			"assess_Q3"
		],
		"assess_Q3": [
			"From scale 1 to 5, rate for the following: " +
			"I am aware of my strengths as a communicator and leader.",
			record_score,
			"",
			"get_level"
		],
		"get_level": [
			"Based on your answers, you are currently at Level *level*",
			record_score,
			"",
			"schedule"
		],
		"schedule": [
			"Wonderful. Now I will add these courses and build a plan for you for the next 6 months. Shall I proceed?",
			schedule,
			"",
			"show_dashboard"
		],
		"show_dashboard": [
			"Here is the dashboard for the next few months. ",
			show_schedule,
			"Ok, let's review the courses again. Would you like to see the dashboard?",
			"ask_obstacle"
		],
		"ask_obstacle": [
			"While it's easy to get start, but things can get in our way. What would prevent you from following this plan?",
			no_action,
			"Things can be complicated. What would be in your way?",
			"ask_solution"
		],
		"ask_solution": [
			"What would be your solution for handling these obstacles? ",
			no_action,
			"Let's brainstorm about the solutions",
			"end_conversation"
		],
		"end_conversation": [
			"Are you ready to start your course? If you do, we can end this session.",
			no_action,
			"let's restart",
			"greet"
		]
	}
}


def user_name(coach):
	user_id = coach.user_id
	return get_userName(user_id)


def today_date(coach):
	return coach.date


def suggested_path(coach):
	return coach.suggested_path


def level(coach):
	print("levelSum=" + str(coach.levelSum))
	print("levelCount=" + str(coach.levelCount))
	response = str(coach.levelSum // coach.levelCount) +\
			   ". I will recommend some courses based on your level. Does that sound good?"
	return response


variables = {
	"user_name": user_name,
	"today_date": today_date,
	"suggested_path": suggested_path,
	"level": level
}


class Coach:
	def __init__(self, user_id, screen_name):
		self.user_id = user_id
		self.change_screen(screen_name)
		self.history = []
		self.levelSum = 0
		self.levelCount = 0
		self.prior_question = ""
		self.suggested_path = "";
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
			entity = entity.strip()  # remove white space
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
	bot = Coach(3, "standard")
	bot.state = "greet"
	while True:
		print("User:")
		userIn = input()
		if (userIn == "bye"):
			quit()
		else:
			print("current state:" + bot.state)
			coachR = bot.get_response(userIn)
			print(coachR)
