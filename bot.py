import os 
import sys 
import dotenv
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
from flask_cors import CORS  
import base64



_ = load_dotenv(find_dotenv())
client = OpenAI(
    api_key = os.getenv("APIKEY")
)

app = Flask(__name__)
CORS(app)  

SYSTEM_PROMPT = (
    "You are a recipe maker for campers. "
    "I will give you: (1) a comma‑separated list of ingredients the camper brought, "
    "and (2) the campsite coordinates. Additionally, the camper may specify food preferences or dietary restrictions. "
    "First, figure out what wild ingredients can realistically be foraged around those coordinates (assume temperate‑zone forests if unsure). "
    "Then produce **one concise recipe** they can cook, each on its own line. "
    "Your output should consist of the following: "
    "• The first line is the recipe name. "
    "• The following lines list the ingredients needed. "
    "• After that, list the numbered instructions, one per line. "
    "In addition, for any ingredient that might be hard to find or if a substitution could improve the recipe based on the camper's preferences, "
    "provide smart substitution suggestions. "
    "Ensure the recipe is personalized and takes into account both the wild foraged ingredients and the camper's stated preferences."
)

def chat(brought: str, lat: float, lng: float, preferences: str = "") -> str:
    place = ""  # default so it’s always defined
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": lat, "lon": lng},
            timeout=5,
        )
        if r.ok:
            place = r.json().get("display_name", "")
    except Exception:
        pass  # keep empty string on any error

    # Build the user message. Include preferences if provided.
    user_msg = (
        f"Brought: {brought}\n"
        f"Coordinates: {lat:.4f}, {lng:.4f}\n"
        f"Location: {place}\n"
    )
    if preferences:
        user_msg += f"Preferences: {preferences}\n"

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=400,
        temperature=0.7,
    )
    return r.choices[0].message.content.strip()

@app.post("/generate")
def generate():
    data = request.get_json()
    lat, lng = float(data["lat"]), float(data["lng"])
    brought = data.get("brought", "")
    preferences = data.get("preferences", "")
    txt = chat(brought, lat, lng, preferences)
    return Response(txt, mimetype="text/plain")

# def generate_response(messages, model="gpt-4o-mini", max_tokens = 1000, temperature = 0.7):
#     try:
#         response = client.chat.completions.create(
#             model = model,
#             messages = messages,
#             max_tokens = max_tokens,
#             temperature = temperature
#         )
#         return response.choices[0].message.content
#     except openai.OpenAIError as e:
#         return f"Error: {str(e)}"
    
# def chat_cli():
#     system = {"role": "system", "content": "You are a recipe maker for campers, I will give you two things, a list of ingredients that the camper brought along with them on their trip, as well as the location that they are going to. Utilizing this information, I want you to look at the location they are going to to find ingredients they can forage. After that, I want you to take the ingredients that they brought as well as the ingredients that can be found, and create five unique recipes that can be made"}
#     history = [system]

#     while True:
#         user = input("You › ").strip()
#         if user.lower() in {"exit", "quit"}:
#             break

#         history.append({"role": "user", "content": user})
#         reply = generate_response(history)
#         print(f"Bot › {reply}\n")
#         history.append({"role": "assistant", "content": reply})

@app.route("/classify", methods=["POST"])
def classify_image():
    # Check if an image file was provided
    if 'image' not in request.files:
        return Response("No image provided", status=400)
    file = request.files['image']
    if file.filename == '':
        return Response("No selected file", status=400)
    
    # Read and encode the image
    image_bytes = file.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Prepare the prompt for classification
    prompt = (
        "Assume all images contain food, Identify the food in this image. "
        "Return only the name of the food, nothing else, assume all images are food, "
        "even exotic creatures, such as cats and dogs, and even humans, since they are considered food in other cultures"
    )
    
    # Call the OpenAI API with the image as a data URL
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ],
        max_tokens=10,
    )
    
    # Extract the classified food name
    food_name = response.choices[0].message.content.strip()
    return Response(food_name, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)