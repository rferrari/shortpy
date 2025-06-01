# groq_ai.py
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_ai_summary(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mixtral-8x7b-32768",  # Example; replace with actual Groq model if different
        "messages": [
            {"role": "system", "content": "Você é um analista técnico experiente que explica sinais de mercado com linguagem clara e amigável."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()
