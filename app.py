# app.py
# Final backend for the Karigar Canvas full prototype

import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import vertexai
from vertexai.preview.generative_models import GenerativeModel
# THIS IS THE CORRECTED LINE:
from vertexai.preview.vision_models import ImageGenerationModel, Image 

# --- INITIAL SETUP ---
load_dotenv()
app = Flask(__name__)

# --- GOOGLE CLOUD VERTEX AI CONFIGURATION ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- MODELS ---
gemini_pro_model = GenerativeModel("gemini-pro")
# This line now works because of the corrected import
image_generation_model = ImageGenerationModel.from_pretrained("imagegeneration@005")

# --- CORE AI FUNCTIONS ---

def generate_story_and_social(keywords, tone):
    """Generates both the product story and a social media caption."""
    print(f"Generating content for keywords: {keywords} with tone: {tone}")

    prompt_text = f"""
    You are an expert marketing storyteller for Indian artisans.
    Your task is to write two pieces of content based on user-provided details:
    1. A product description.
    2. A short, engaging Instagram caption.

    Instructions:
    - Keywords for inspiration: {keywords}
    - Desired tone: {tone}
    - The product description should be 80-100 words, focusing on heritage and craftsmanship.
    - The Instagram caption should be short (2-3 sentences), use 1-2 relevant emojis, and include 3-4 relevant hashtags.
    - Structure your response with "STORY:" on one line, followed by the description, and "SOCIAL:" on another line, followed by the caption.
    """
    try:
        response = gemini_pro_model.generate_content(prompt_text)
        full_text = response.text
        
        story = full_text.split("STORY:")[1].split("SOCIAL:")[0].strip()
        social = full_text.split("SOCIAL:")[1].strip()
        
        return story, social
    except Exception as e:
        print(f"Error in Gemini content generation: {e}")
        return "Error generating story.", "Error generating social media post."

def generate_magic_photoshoot(image_bytes, prompt):
    """Generates a new image using a base image and a prompt."""
    print(f"Generating magic photoshoot with prompt: {prompt}")
    try:
        base_image = Image(image_bytes)
        images = image_generation_model.edit_image(
            base_image=base_image,
            prompt=prompt,
            sample_count=1,
            guidance_scale=21,
        )
        generated_image_bytes = images[0]._image_bytes
        return generated_image_bytes
    except Exception as e:
        print(f"Error in Imagen image generation: {e}")
        return None

# --- API ENDPOINTS ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/generate-all', methods=['POST'])
def handle_generate_all():
    """Handles the full content generation request from the frontend."""
    if 'photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400
        
    photo_file = request.files['photo']
    keywords = request.form.get('keywords')
    tone = request.form.get('tone')
    image_prompt = f"The uploaded product placed in a professional, high-quality, {tone.lower()} lifestyle setting. The background should be clean and well-lit to showcase the product."

    if not all([photo_file, keywords, tone]):
        return jsonify({"error": "Missing form data"}), 400

    image_bytes = photo_file.read()

    story, social = generate_story_and_social(keywords, tone)
    generated_image_bytes = generate_magic_photoshoot(image_bytes, image_prompt)

    if not generated_image_bytes:
        return jsonify({"error": "Failed to generate image"}), 500

    import base64
    generated_image_base64 = base64.b64encode(generated_image_bytes).decode('utf-8')

    return jsonify({
        "story": story,
        "social": social,
        "magic_photo": generated_image_base64
    })

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)