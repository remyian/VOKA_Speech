import azure.cognitiveservices.speech as speechsdk
import time
import config
from flask import Flask, jsonify, request
from flask_cors import CORS
from repositories.datarepository import DataRepository
from pydantic import BaseModel
from flask_socketio import SocketIO
import threading
done = False

app = Flask(__name__)
app.config['SECRET KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

endpoint = '/api/v1'
all_results = []

speech_config = speechsdk.SpeechConfig(
    subscription=config.SPEECH_KEY, region=config.SERVICE_REGION)

speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, language="nl-NL")


def speech_recognize_continuous():
    global done, all_results
    """performs continuous speech recognition with input from an audio file"""
    # <SpeechContinuousRecognitionWithFile>

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        done = True

    def handle_final_result(evt):
        all_results.append(evt.result.text)

    speech_recognizer.recognized.connect(handle_final_result)
    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(
        lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(
        lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(
        lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(
        lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(
        lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()


@socketio.on('connect')
def initial_connect():
    print('Nieuwe clienconnectie')


@socketio.on("F2B_start_listening")
def toggle_speech(command):
    global done
    if command == 'listen':
        speech_recognize_continuous()
    elif command == 'stop':
        print(all_results)
        socketio.emit('B2F_text', all_results)
        speech_recognizer.stop_continuous_recognition()


# START THE APP
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
