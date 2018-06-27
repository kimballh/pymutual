import requests
import json
import robobrowser
import re

from pymutual.constants import *
from pymutual.models.profile import Profile
from pymutual.errors import *
from werkzeug.exceptions import BadRequestKeyError


class Session:
	def __init__(self, email: str=None, password: str=None, fb_token: str=None, mutual_id: int=None):
		if fb_token:
			self._fb_token = fb_token
		elif email and password:
			self.get_fb_token(email, password)
			if self._fb_token == -1:
				raise InitializationError('Invalid Facebook login information')
		else:
			raise InitializationError('Facebook user email and password must be provided or auth token')
		if not self._fb_token or self._fb_token == '':
			raise InitializationError('User could not be authenticated')
		self._fb_id = self.get_fb_id(self._fb_token)
		self._api = MutualAPI(self._fb_token, int(self._fb_id), mutual_id)

	@property
	def token(self):
		return self._fb_token

	@property
	def mutual_id(self):
		return self._api.id

	def get_fb_token(self, email, password):
		s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
		s.open(MUTUAL_AUTH)
		##submit login form##
		f = s.get_form()
		f["pass"] = password
		f["email"] = email
		s.submit_form(f)
		##click the 'ok' button on the dialog informing you that you have already authenticated with the Tinder app##
		f = s.get_form()
		try:
			s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
			##get access token from the html response##
			access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
			self._fb_token = access_token
		except BadRequestKeyError:
			self._fb_token = -1

	def get_fb_id(self, fb_token) -> str:
		r = requests.get('https://graph.facebook.com/v2.11/me?access_token={}'.format(fb_token))
		if r.status_code != 200:
			raise InitializationError('User could not be authenticated')
		if not r.json() or type(r.json()) is not dict or 'id' not in r.json().keys():
			raise InitializationError('User could not be authenticated')
		return r.json()['id']

	def potential_matches(self, limit=10, import_json: str=None, return_dict: bool=False):
		if import_json:
			data = json.loads(import_json)
		else:
			data = self._api.get_potential_matches(limit)

		# get profile data from each dict and create Profile objects to return as array
		if return_dict:
			profiles = {}
		else:
			profiles = []
		for person in data:
			name = person['first_name']
			age = person['age']
			gender = person['gender']
			mutual_id = person['id']
			distance_mi = person['distance']
			location = person['location']
			position = person['position']
			school = person['school']
			mission = person['mission_location']
			hometown = person['hometown']
			fb_id = person['fb_id']
			dating_interest = person['dating_interest']
			liked_user = person['has_liked']
			height = "{}' {}\"".format(person['height_ft'], person['height_in'])
			photo_urls = []
			for photo in person['photos']:
				photo_urls.append(photo['url_hd'])

			# get bio
			user_prompt_data = self._api.get_user_prompt(mutual_id)
			if user_prompt_data and len(user_prompt_data) > 0:
				item = user_prompt_data[0]
				prompt_id = item['prompt_id']
				bio = item['text']
			else:
				prompt_id = 0
				bio = ''

			# get tags
			tag_data = self._api.get_user_tags(mutual_id)
			tags = []
			for item in tag_data:
				tags.append(item['text'])

			# create Profile object
			profile = Profile(name, age, gender, mutual_id, distance_mi, location, photo_urls, position, school, height,
							  mission, hometown, fb_id, dating_interest, liked_user, prompt_id, bio, tags)
			if return_dict:
				profiles[mutual_id] = profile.serialize()
			else:
				profiles.append(profile)
		return profiles

	def get_auto_matches(self, search_limit: int=10, import_json: str=None):
		profiles = self.potential_matches(limit=search_limit, import_json=import_json)
		auto_matches = []
		for profile in profiles:
			if profile.liked_user:
				auto_matches.append(profile)
		return auto_matches

	def like_user(self, match_id):
		try:
			response = self._api.swipe_user(self.mutual_id, match_id, True)
			return response
		except RequestError as e:
			return {'error': str(e)}

	def dislike_user(self, match_id):
		try:
			response = self._api.swipe_user(self.mutual_id, match_id, False)
			return response
		except RequestError as e:
			return {'error': str(e)}

	def match(self, match_id):
		try:
			response = self._api.match_users(match_id)
			return response
		except RequestError as e:
			return {'error': str(e)}





class MutualAPI:
	def __init__(self, access_token: str, fb_id: int, mutual_id: int=None):
		self._access_token = access_token
		self._url = MUTUAL_URL
		if mutual_id:
			self._id = mutual_id
		else:
			self._id = self.get_id(fb_id)

	@property
	def id(self):
		return self._id

	def get_id(self, fb_id: int):
		url = '{}/user/fb_id/{}'.format(self._url, fb_id)
		try:
			response = self.get(url)['id']
			return response
		except RequestError as e:
			raise InitializationError(e)

	def get(self, url, add_params=None):
		params = {
			'access_token': self._access_token
		}
		if add_params:
			for key in add_params.keys():
				params[key] = add_params[key]
		response = requests.get(url, params=params)
		if response.status_code != 200:
			raise RequestError('URL: {} returned code {}'.format(url, response.status_code))
		return response.json()

	def post(self, url, body, add_params=None):
		params = {
			'access_token': self._access_token
		}
		if add_params:
			for key in add_params.keys():
				params[key] = add_params[key]
		response = requests.post(url, json=body, params=params)
		if response.status_code != 200:
			raise RequestError('URL: {} returned code {}{}'.format(url, response.status_code, response.content))
		return response.json()

	def get_potential_matches(self, limit: int=10):
		params = {
			'count': limit
		}
		url = '{}/user/potential-matches/{}'.format(self._url, self._id)
		response = self.get(url, add_params=params)
		return response

	def swipe_user(self, user_id, match_id, liked):
		body = {
			'user_id': str(user_id),
			'liked': liked,
			'match_user_id': str(match_id),
		}
		url = '{}/connection/'.format(self._url)
		response = self.post(url, body)
		return response

	def match_users(self, match_id):
		url = '{}/match/users/{}/{}'.format(self._url, self._id, match_id)
		return self.get(url)

	def get_user_prompt(self, user_id):
		url = '{}/user-prompt/list/{}'.format(self._url, user_id)
		return self.get(url)

	def get_user_tags(self, user_id):
		url = '{}/tagline/list/{}'.format(self._url, user_id)
		return self.get(url)

	def get_mutual_friends(self, fb_id):
		url = '{}/fb-mutual-friends/{}'.format(self._url, fb_id)
		return self.get(url)

if __name__ == '__main__':
	# session = Session(email='kimball.hill', password='id1080287!')
	session = Session(fb_token='EAAOxRcEGpJMBACfBF6q8nlsl7noosIC0e29AanOWcvT8JjZCRQqZCn0Gw2ZABsdYD2HQhjRedouZBb0SzNclCQdGaPy2tOM0IMYSV4LIpUdzBQDFEX1qW8tS7jOPcAOlmZAhkVwKM0eMiWMXBSswGFFlI8IfsHc6qQTpyVrsZAnN44ohbtqGoUT1qopNqhGOG19FC6nFpZAiQZDZD', mutual_id=302709)
	print(session.like_user(175424))

