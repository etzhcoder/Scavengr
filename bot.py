import os 
import sys 
import dotenv
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
from flask_cors import CORS               


_ = load_dotenv(find_dotenv())
client = OpenAI(
    api_key = os.getenv("APIKEY")
)

app = Flask(__name__)
CORS(app)  

SYSTEM_PROMPT = (
    "You are a recipe maker for campers. "
    "I will give you: (1) a comma‑separated list of ingredients the camper brought, "
    "and (2) the campsite coordinates. "
    "First, figure out what wild ingredients can realistically be foraged around those coordinates "
    "(assume temperate‑zone forests if unsure). "
    "Then produce **one concise recipe** they can cook, each on its own line."
    "I want you to output this and this only, nothing else: First line, Recipe name. Lines after that, ingredients needed, each on their own line. Lastly, the numbered instructions, each on their own individual line"
)

def chat(brought: str, lat: float, lng: float) -> str:
    place = ""                                   # ← default so it’s always defined
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": lat, "lon": lng},
            timeout=5,
        )
        if r.ok:
            place = r.json().get("display_name", "")
    except Exception:
        pass                                     # keep empty string on any error

    user_msg = (
        f"Brought: {brought}\n"
        f"Coordinates: {lat:.4f}, {lng:.4f}\n"
        f"Location: {place}"
    )
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": user_msg}],
        max_tokens=400,
        temperature=0.7,
    )
    return r.choices[0].message.content.strip()

@app.post("/generate")
def generate():
    data = request.get_json()
    lat, lng = float(data["lat"]), float(data["lng"])
    brought = data.get("brought", "")
    txt = chat(brought, lat, lng)
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)