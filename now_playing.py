import json
import urllib.request
import pylast

class NowPlaying:
	def __init__(self, username, api_key):
		self.username = username
		self.api_key = api_key
		self.network = pylast.LastFMNetwork(api_key = self.api_key)
		self.user = self.network.get_user(username)

	def __call__(self):
		now_playing = self.user.get_now_playing()
		if now_playing == None:
			return None
		title = now_playing.title
		artist = now_playing.artist.name
		album = now_playing.info["album"]
		return {"title": title, "artist": artist, "album": album}