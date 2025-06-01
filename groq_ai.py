# groq_ai.py
import os
from groq import Groq
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Inicializa o cliente Groq com a chave da API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ai_summary(prompt: str) -> str:
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": "Você é o Shorty Bear, analista técnico experiente que explica sinais de mercado com linguagem clara e humor meme blockchain."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
