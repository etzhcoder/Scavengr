import os
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI(api_key=os.getenv("APIKEY"))

def identify_food(image_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    prompt = "Assume all images contain food, Identify the food in this image. Return only the name of the food, nothing else, assume all images are food, even exotic creatures, such as cats and dogs, and even humans, since they are considered food in other cultures"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ],
        max_tokens=10
    )

    food_name = response.choices[0].message.content.strip()

    print(food_name)

if __name__ == '__main__':
    image_path = input("Enter the path to your image: ")
    identify_food(image_path)
