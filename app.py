from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import nltk
import spacy
import requests
from dotenv import load_dotenv
import os




app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


load_dotenv()
api_key = os.getenv('OPENWEATHERMAP_API_KEY')

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load NLP model
nlp = spacy.load('en_core_web_sm')

@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({'error': 'No command provided'}), 400

    # Process command using NLP
    doc = nlp(command.lower())

    response = ""

    # Simple intent recognition
    if 'weather' in command:
        # Fetch weather information
        location = extract_location(doc)
        weather = get_weather(location)
        response = f"The current weather in {location} is {weather}."
    elif 'remind' in command or 'reminder' in command:
        # Set a reminder
        reminder = extract_reminder(doc)
        set_reminder(reminder)
        response = f"Reminder set for {reminder}."
    elif 'turn on' in command or 'turn off' in command:
        # Control smart home device
        device, action = extract_device_action(doc)
        control_device(device, action)
        response = f"Turning {action} the {device}."
    else:
        response = "I'm sorry, I didn't understand that command."

    return jsonify({'response': response})

def extract_location(doc):
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            return ent.text
    return 'your location'

def get_weather(location):
    # Example using OpenWeatherMap API
    api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if data.get('weather'):
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{description} with a temperature of {temp}°C."
    else:
        return "I couldn't fetch the weather information right now."

def extract_reminder(doc):
    # Simple extraction logic: extract noun phrases after 'remind me to'
    reminder = ""
    if 'remind me to' in doc.text:
        reminder = doc.text.split('remind me to')[1].strip()
    elif 'reminder' in doc.text:
        reminder = doc.text.split('reminder')[1].strip()
    return reminder or 'something'

def set_reminder(reminder):
    # Integrate with a reminder service or database
    print(f"Setting reminder: {reminder}")
    # Placeholder: In production, store reminders in a database and use a scheduler to trigger notifications

def extract_device_action(doc):
    action = 'on' if 'turn on' in doc.text else 'off'
    device = ' '.join([token.text for token in doc if token.pos_ == 'NOUN'])
    return device, action

def control_device(device, action):
    # Integrate with smart home APIs (e.g., Philips Hue, SmartThings)
    print(f"Turning {action} the {device}")
    # Example for Philips Hue:
    if device.lower() == 'lights':
        hue_api_url = 'http://<bridge_ip>/api/<username>/lights/1/state'
        payload = {'on': True if action == 'on' else False}
        requests.put(hue_api_url, json=payload)

if __name__ == '__main__':
    app.run(debug=True)
