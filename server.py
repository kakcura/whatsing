# WhatSing : Bringing furture to now by making IBM Watson sing any famous song.
# Author :  Korhan Akcura

import json
import requests
import logging
import os
from pydub import AudioSegment
from PyLyrics import *

from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request

app = Flask(__name__, static_url_path='')

WATSON_API_KEY = "Put your's here."
WATSON_URL = "Put your's here."

@app.route("/", methods=['GET', 'POST'])
def root(): 
	return app.send_static_file('index.html')

@app.route('/sing', methods=['POST'])
def listen():
	try:
		query = json.loads(request.data)
		singer = query['singer'].lower()
		song = query['song'].lower()		
	except Exception:
		return jsonify({"response" : "Bad request!"}), 400

	filename = "static/" + singer + " - " + song + ".mp3"

	if not os.path.isfile(filename):
		lyrics= PyLyrics.getLyrics(singer, song)

		full_sound = AudioSegment.from_file("silent.wav")
		for line in lyrics.splitlines():
			if line:
				data = {'text': line}
				headers = {'Content-type': 'application/json', 'Accept': 'audio/wav'}
				response = requests.post(WATSON_URL, headers=headers, data=json.dumps(data), auth=('apikey', WATSON_API_KEY))
				print(str(response) + str(line))
				open("singing.wav", 'wb').write(response.content)
				new_sound = AudioSegment.from_file("singing.wav")
				full_sound = full_sound.append(new_sound)

		background = AudioSegment.from_file("background.mp3")
		full_sound = full_sound.overlay(background)

		full_sound.export(filename, format='mp3')

	return singer + " - " + song + ".mp3" 

if __name__ == '__main__':
	handler = RotatingFileHandler('server.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host="127.0.0.1",port=5000)

