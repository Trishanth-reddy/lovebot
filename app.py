from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import requests
import random
from google.generativeai.types import HarmCategory, HarmBlockThreshold

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Hardcoded API Keys
GEMINI_API_KEY = "AIzaSyAnVAtKWzgN34WvD0Is1g1lk1hPEKcREUU"  # Replace with your Gemini API key
GIPHY_API_KEY = "ueh0apsVu61b9JM5bVZsJkVh3tBMtjfK"  # Replace with your Giphy API key

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# List of romantic emojis
love_emojis = ["💖", "💌", "🌹", "😍", "💞", "😘", "💑", "❤️", "💘", "💕"]

# Function to get a random romantic GIF from Giphy
def get_romantic_gif():
    try:
        url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&tag=love&rating=g"
        response = requests.get(url).json()
        gif_url = response["data"]["images"]["original"]["url"]
        return gif_url
    except Exception as e:
        print("Error fetching GIF:", e)
        return None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a message. 💕"})

    # Define system instructions for a love-themed chatbot
    system_instruction = """You are a love-themed chatbot who only talks about love, relationships, romance, Valentine's Day, and affection. 
    Your responses should always be sweet, charming, and full of love. 
    Avoid any inappropriate or explicit content. 
    If someone asks about a different topic, gently redirect them to love and romance."""

    # Define safety settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,  # Allow sexually explicit content
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,   # Block only high-probability hate speech
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,    # Block only high-probability harassment
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,  # Block only high-probability dangerous content
    }

    try:
        # Send message to Gemini AI with instructions
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"{system_instruction}\nUser: {user_message}\nBot:",
            safety_settings=safety_settings
        )

        # Check if response is valid
        if response.candidates and response.candidates[0].finish_reason == 1:  # finish_reason == 1 means "STOP" (valid response)
            response_text = response.text + " " + random.choice(love_emojis)
        else:
            response_text = "I'm sorry, I can't respond to that. Let's talk about something else! 💕"

        # Get a romantic GIF
        romantic_gif = get_romantic_gif()

        return jsonify({
            "response": response_text,
            "gif": romantic_gif  # Send GIF URL in response
        })
    except Exception as e:
        print("Error generating Gemini response:", e)
        return jsonify({"response": "I'm feeling a little shy right now. Can you say that again? 💕"})

if __name__ == "__main__":
    app.run(debug=True)