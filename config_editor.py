import configparser
import re

class ConfigEditor(configparser.ConfigParser):

	def __init__(self, *args, **kwargs):
		super(ConfigEditor, self).__init__(*args, **kwargs)
		self.config_file = "config.ini"
		self.default_settings = {"last.fm": {"username": "", "api_key": ""}, "discord": {"application_id": "910259161055502376"}}
		try:
			self.read(self.config_file)
		except: # something is fundamentally broken in the config
			pass # but it's ok, we don't have to do anything about it, we can just re-initialise the config! i *hate* using except: pass, but it actually works here
		self.__fix_config() # and there we have it, problems solved

	def __fix_config(self):
		for section in self.default_settings: # add missing keys - a very simplistic approach but it will do for now :)
			if not section in self._sections:
				self.add_section(section)
			for setting in self.default_settings[section]:
				if not setting in self._sections[section]:
					self.set(section, setting, self.default_settings[section][setting])

	def ask_for_missing_values(self):
		# just ask for the values on the command line - i want to make a gui for this, but it works for now
		while not self.validate_lastfm_username(self.get("last.fm","username")):
			self.set("last.fm","username", input("Please enter your last.fm username: "))

		while not self.validate_lastfm_api_key(self.get("last.fm","api_key")):
			self.set("last.fm","api_key", input("Please enter your last.fm API key, as obtained from https://www.last.fm/api/account/create: "))

		with open(self.config_file, "w") as f:
			self.write(f)

	def validate_lastfm_username(self,s):
		return re.match(r"[a-zA-Z0-9\-_]{2,15}$", s)

	def validate_lastfm_api_key(self, s):
		return re.match(r"[a-f0-9]{32}$", s)