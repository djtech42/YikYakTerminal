import base64
import hmac
import json
import requests
import time
import datetime
import urllib
import os

from hashlib import sha1
from hashlib import md5

def parse_time(timestr):
	format = "%Y-%m-%d %H:%M:%S"
	return datetime.datetime.fromtimestamp(
		time.mktime(time.strptime(timestr, format))
	).strftime('%Y-%m-%d %H:%M:%S')

class Location:
	def __init__(self, latitude, longitude, delta=None):
		self.latitude = latitude
		self.longitude = longitude
		if delta is None:
			delta = "0.030000"
		self.delta = delta

	def __str__(self):
		return "Location(%s, %s)" % (self.latitude, self.longitude)

class PeekLocation:
	def __init__(self, raw):
		self.id = raw['peekID']
		self.can_submit = bool(raw['canSubmit'])
		self.name = raw['location']
		lat = raw['latitude']
		lon = raw['longitude']
		d = raw['delta']
		self.location = Location(lat, lon, d)

class Comment:
	def __init__(self, raw, message_id, client):
		self.client = client
		self.message_id = message_id
		self.comment_id = raw["commentID"]
		self.comment = raw["comment"]
		self.time = parse_time(raw["time"])
		self.likes = int(raw["numberOfLikes"])
		self.poster_id = raw["posterID"]
		self.liked = int(raw["liked"])

		try:
			self.message_id = self.message_id.replace('\\', '')
		except:
			pass

	def upvote(self):
		if self.liked == 0:
			self.likes += 1
			self.liked += 1
			return self.client.upvote_comment(self.comment_id)

	def downvote(self):
		if self.liked == 0:
			self.likes -= 1
			self.liked -= 1
			return self.client.downvote_comment(self.comment_id)

	def report(self):
		return self.client.report_comment(self.comment_id, self.message_id)

	def delete(self):
		if self.poster_id == self.client.id:
			return self.client.delete_comment(self.comment_id, self.message_id)

	def reply(self, comment):
		return self.client.post_comment(self.message_id, comment)

	def print_comment(self):
		my_action = ""
		if self.liked > 0:
			my_action = "^ "
		elif self.liked < 0:
			my_action = "v "
		print ("\t\t%s(%s) %s \n\n\t\tPosted  %s" % (my_action, self.likes, self.comment, self.time))

class Yak:
	def __init__(self, raw, client):
		self.client = client
		self.poster_id = raw["posterID"]
		self.hide_pin = bool(int(raw["hidePin"]))
		self.message_id = raw["messageID"]
		try:
			self.delivery_id = raw["deliveryID"]
		except KeyError:
			pass
		self.longitude = raw["longitude"]
		self.comments = int(raw["comments"])
		self.time = parse_time(raw["time"])
		self.latitude = raw["latitude"]
		self.likes = int(raw["numberOfLikes"])
		self.message = raw["message"]
		try:
			self.type = raw["type"]
			self.liked = int(raw["liked"])
			self.reyaked = raw["reyaked"]
		except KeyError:
			pass

		#Yaks don't always have a handle
		try:
			self.handle = raw["handle"]
		except KeyError:
			self.handle = None

		#For some reason this seems necessary
		try:
			self.message_id = self.message_id.replace('\\', '')
		except:
			pass

	def upvote(self):
		if self.liked == 0:
			self.liked += 1
			self.likes += 1
			return self.client.upvote_yak(self.message_id)

	def downvote(self):
		if self.liked == 0:
			self.liked -= 1
			self.likes -= 1
			return self.client.downvote_yak(self.message_id)

	def report(self):
		return self.client.report_yak(self.message_id)

	def delete(self):
		if self.poster_id == self.client.id:
			return self.client.delete_yak(self.message_id)

	def add_comment(self, comment):
		return self.client.post_comment(self.message_id, comment)

	def get_comments(self):
		return self.client.get_comments(self.message_id)

	def print_yak(self):
		if self.handle is not None:
			print ("### %s ###" % self.handle)
		print ()
		print (self.message)
		# Show arrow if yak is upvoted or downvoted
		my_action = ""
		if self.liked > 0:
			my_action = "^ "
		elif self.liked < 0:
			my_action = "v "
		print ("\n\t%s%s likes  |  Posted  %s  at  %s %s" % (my_action, self.likes, self.time, self.latitude, self.longitude))

class Yakker:
	base_url = "https://us-east-api.yikyakapi.net/api/"
	user_agent = "Yik Yak/2.1.0.23 (iPhone; iOS 8.1; Scale/2.00)"
	version = "2.1.002"

	def __init__(self, user_id=None, location=None, force_register=False):
		if location is None:
			location = Location('0', '0')
		self.update_location(location)

		if user_id is None:
			user_id = self.gen_id()
			self.register_id_new(user_id)
		elif force_register:
			self.register_id_new(user_id)

		self.id = user_id

		self.handle = None

		#self.update_stats()

	def gen_id(self):
		return md5(os.urandom(128)).hexdigest().upper()

	def register_id_new(self, id):
		params = {
			"userID": id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		result = self.get("registerUser", params)
		return result

	def sign_request(self, page, params):
		key = "F7CAFA2F-FE67-4E03-A090-AC7FFF010729"

		#The salt is just the current time in seconds since epoch
		salt = str(int(time.time()))

		#The message to be signed is essentially the request, with parameters sorted
		msg = "/api/" + page
		sorted_params = list(params.keys())
		sorted_params.sort()
		if len(params) > 0:
			msg += "?"
		for param in sorted_params:
			msg += "%s=%s&" % (param, params[param])
		#Chop off last "&"
		if len(params) > 0:
			msg = msg[:-1]

		#the salt is just appended directly
		msg += salt

		#Calculate the signature
		h = hmac.new(key.encode(), msg.encode(), sha1)
		hash = base64.b64encode(h.digest())

		return hash, salt
		
	def post_sign_request(self, page, params):
		key = "F7CAFA2F-FE67-4E03-A090-AC7FFF010729"
	
		#The salt is just the current time in seconds since epoch
		salt = str(int(time.time()))
	
		#The message to be signed is essentially the request, with parameters sorted
		msg = "/api/" + page
	
		#the salt is just appended directly
		msg += salt
	
		#Calculate the signature
		h = hmac.new(key.encode(), msg.encode(), sha1)
		hash = base64.b64encode(h.digest())
		
		return hash, salt


	def get(self, page, params):
		url = self.base_url + page

		hash, salt = self.sign_request(page, params)
		params['hash'] = hash
		params['salt'] = salt

		headers = {
			"User-Agent": self.user_agent,
			"Accept-Encoding": "gzip",
		}
		return requests.get(url, params=params, headers=headers)

	def post(self, page, params):
		url = self.base_url + page

		hash, salt = self.post_sign_request(page, params)
		getparams = {'hash': hash, 'salt': salt}

		headers = {
			"User-Agent": self.user_agent,
			"Accept-Encoding": "gzip",
		}
		return requests.post(url, data=params, params=getparams, headers=headers)

	def get_yak_list(self, page, params):
		return self.parse_yaks(self.get(page, params).text)

	def parse_yaks(self, text):
		try:
			raw_yaks = json.loads(text)["messages"]
		except:
			raw_yaks = []
		yaks = []
		for raw_yak in raw_yaks:
			yaks.append(Yak(raw_yak, self))
		return yaks

	def parse_comments(self, text, message_id):
		try:
			raw_comments = json.loads(text)["comments"]
		except:
			raw_comments = []
		comments = []
		for raw_comment in raw_comments:
			comments.append(Comment(raw_comment, message_id, self))
		return comments

	def contact(self, message):
		params = {
			"userID": self.id,
			"message": message
		}
		return self.get("contactUs", params)

	def upvote_yak(self, message_id):
		params = {
			"userID": self.id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("likeMessage", params)

	def downvote_yak(self, message_id):
		params = {
			"userID": self.id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("downvoteMessage", params)

	def upvote_comment(self, comment_id):
		params = {
			"userID": self.id,
			"commentID": comment_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("likeComment", params)

	def downvote_comment(self, comment_id):
		params = {
			"userID": self.id,
			"commentID": comment_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("downvoteComment", params)

	def report_yak(self, message_id):
		params = params = {
			"userID": self.id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("reportMessage", params)

	def delete_yak(self, message_id):
		params = params = {
			"userID": self.id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("deleteMessage2", params)

	def report_comment(self, comment_id, message_id):
		params = {
			"userID": self.id,
			"commentID": comment_id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("reportMessage", params)

	def delete_comment(self, comment_id, message_id):
		params = {
			"userID": self.id,
			"commentID": comment_id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get("deleteComment", params)

	def get_greatest(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get_yak_list("getGreatest", params)

	def get_my_tops(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get_yak_list("getMyTops", params)

	def get_recent_replied(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get_yak_list("getMyRecentReplies", params)

	def update_location(self, location):
		self.location = location

	def get_my_recent_yaks(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get_yak_list("getMyRecentYaks", params)

	def get_area_tops(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		toplist = self.get_yak_list("getAreaTops", params)
		toplist.sort(key=lambda x: x.likes, reverse=True)
		return toplist

	def get_yaks(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.get_yak_list("getMessages", params)

	def post_yak(self, message, showloc=False, handle=False):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"message": message,
			"version": self.version,
		}
		if not showloc:
			params["hidePin"] = "1"
		if handle and (self.handle is not None):
			params["hndl"] = self.handle
		return self.post("sendMessage", params)

	def get_comments(self, message_id):
		params = {
			"userID": self.id,
			"messageID": message_id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}

		return self.parse_comments(self.get("getComments", params).text, message_id)

	def post_comment(self, message_id, comment):
		params = {
			"userID": self.id,
			"messageID": message_id,
			"comment": comment,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		return self.post("postComment", params)

	def get_peek_locations(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		data = self.get("getMessages", params).json()
		peeks = []
		for peek_json in data['otherLocations']:
			peeks.append(PeekLocation(peek_json))
		return peeks

	def get_featured_locations(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		data = self.get("getMessages", params).json()
		peeks = []
		for peek_json in data['featuredLocations']:
			peeks.append(PeekLocation(peek_json))
		return peeks

	def get_yakarma(self):
		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			"version": self.version,
		}
		data = self.get("getMessages", params).json()
		return int(data['yakarma'])

	def peek(self, peek_id):
		if isinstance(peek_id, PeekLocation):
			peek_id = peek_id.id

		params = {
			"userID": self.id,
			"lat": self.location.latitude,
			"long": self.location.longitude,
			'peekID': peek_id,
			"version": self.version,
		}
		return self.get_yak_list("getPeekMessages", params)
		
	def peekLoc(self, location):
		params = {
				"lat": location.latitude,
				"long": location.longitude,
				"userID": self.id,
				"userLat": self.location.latitude,
				"userLong": self.location.longitude,
				"version": self.version,
		}
		return self.get_yak_list("yaks", params)