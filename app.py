import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("CRITICAL ERROR: GOOGLE_API_KEY not found. Please check your .env file.")
genai.configure(api_key=API_KEY)

PROMPT_PRODUCT_GENERATION = """
Persona: You are an expert e-commerce copywriter for Indian crafts.
Context: The user is a local artisan. Your task is to generate marketing content for their product. The language should be simple and beautiful.
Task: Analyze the image and return a rich, structured JSON object with a concise description, a provenance report, and a short artisan's note.
Output Format: Respond ONLY with a valid JSON object with the following structure:
{
 "product_title": "A short, attractive title for the product (under 50 characters).",
 "description": "A short, beautiful, and easy-to-understand description in a single paragraph (about 2-3 sentences).",
 "provenance": {
    "craft_type": "e.g., Block Printing",
    "materials": "e.g., Cotton, Natural Dyes",
    "region": "e.g., Rajasthan, India"
 },
 "artisans_note": "A short, heartwarming note in the first person, as if from the artisan (1-2 sentences)."
}
"""

PROMPT_MARKETING_SUGGESTIONS = """
Persona: You are a helpful friend giving simple, practical advice to a local artisan who is not an expert in digital marketing.
Context: Based on the following product description, provide three very simple and actionable marketing ideas. Avoid complex jargon. Use simple language.
Task: Generate three distinct suggestions.
Output Format: Respond ONLY with a valid JSON array of objects with the following structure:
[
    {"title": "Share Your Process", "idea": "Post a short video of you making this craft on Instagram or WhatsApp to show the hard work involved."},
    {"title": "Connect with Local Shops", "idea": "Partner with a local boutique or hotel to display and sell your products to new customers."},
    {"title": "Use Festive Seasons", "idea": "Promote this as a perfect, handmade gift for festivals like Diwali, Eid, or Christmas."}
]
"""

@app.route('/generate', methods=['POST'])
def generate_product_content():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file part in the request'}), 400
    try:
        img = Image.open(request.files['image'].stream)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content([PROMPT_PRODUCT_GENERATION, img])
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        generated_data = json.loads(response_text)
        return jsonify(generated_data)
    except Exception as e:
        print(f"!!! BACKEND ERROR !!! /generate: {e}")
        return jsonify({'error': f'An error occurred on the server: {e}'}), 500

@app.route('/generate-suggestions', methods=['POST'])
def generate_marketing_suggestions():
    request_data = request.get_json()
    if not request_data or 'description' not in request_data:
        return jsonify({'error': 'No product description provided.'}), 400
    description = request_data['description']
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content([PROMPT_MARKETING_SUGGESTIONS, description])
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        generated_data = json.loads(response_text)
        return jsonify(generated_data)
    except Exception as e:
        print(f"!!! BACKEND ERROR !!! /generate-suggestions: {e}")
        return jsonify({'error': f'An error occurred on the server: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

