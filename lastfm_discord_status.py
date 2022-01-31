import pypresence
import config_editor
import now_playing as np
import time
from datetime import datetime
import sys
import pylast

# config file stuff

class LastfmDiscordStatus:
	def __init__(self):
		self.settings = config_editor.ConfigEditor()
		self.settings.ask_for_missing_values()
		self.presence = pypresence.Presence(self.settings["discord"]["application_id"])
		self.presence.connect()
		self.now_playing = np.NowPlaying(self.settings["last.fm"]["username"], self.settings["last.fm"]["api_key"])
		self.song = None
		self.currently_enabled = False
		self.start_time = 0

	def __call__(self):
		new_song = self.now_playing()
		if new_song != self.song:
			now = datetime.now().timestamp()
			if now - self.start_time > 15: # we can only update every 15 seconds unfortunately
				self.song = new_song
				self.start_time = now
				if self.song:
					if not self.currently_enabled:
						self.currently_enabled = True
					self.presence.update(details = self.__min_length(self.song["title"], 2), state = "by " + self.song["artist"] + " on " + self.song["album"], start = self.start_time, large_image = "icon")
				else:
					self.currently_enabled = False
					self.presence.clear()

	def __min_length(self, s, n): #stupid workaround since discord doesn't allow you to have a 1 character details section
		if (l := len(s)) < n:
			s += " " * (n - l)
		return s

if __name__ == "__main__":
	fmstatus = LastfmDiscordStatus()
	consecutive_errors = 0
	while True:
		try:
			fmstatus()
			consecutive_errors = 0
		except pylast.WSError as e:
			if str(e) == "Invalid API key - You must be granted a valid key by last.fm": # why the hell is this not a separate exception??? jesus christ pylast
				fmstatus.settings["last.fm"]["api_key"] = "" # clear out the api key from the settings to ensure that we ask for a new one later
				with open(fmstatus.settings.config_file, "w") as f:
					fmstatus.settings.write(f)
				sys.exit("Please supply a valid API key")
			else:
				print("Last.fm gave an error. Retrying soon.")
			consecutive_errors += 1
		except pylast.MalformedResponseError:
			print("Something went wrong on last.fm's side. Retrying soon.")
			consecutive_errors += 1
		except pylast.NetworkError:
			print("Can't communicate with last.fm's servers. Retrying soon")
			consecutive_errors += 1
		time.sleep(min(60, 5 * 2**(consecutive_errors // 2))) # double the retry period on every second error up to a minute