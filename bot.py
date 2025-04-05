import os 
import sys 
import dotenv
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
client = OpenAI(
    api_key = os.getenv("APIKEY")
)


def generate_response(messages, model="gpt-4o-mini", max_tokens = 1000, temperature = 0.7):
    try:
        response = client.chat.completions.create(
            model = model,
            messages = messages,
            max_tokens = max_tokens,
            temperature = temperature
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Error: {str(e)}"
    
def chat_cli():
    system = {"role": "system", "content": "You are a helpful assistant."}
    history = [system]

    while True:
        user = input("You › ").strip()
        if user.lower() in {"exit", "quit"}:
            break

        history.append({"role": "user", "content": user})
        reply = generate_response(history)
        print(f"Bot › {reply}\n")
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_cli()