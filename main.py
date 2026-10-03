import os
from fastapi import FastAPI
from groq import Groq

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def home():
    return {"status": "AI Income Bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ai")
def ai(prompt: str = "Give me one useful online business idea"):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI business assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return {
        "prompt": prompt,
        "answer": response.choices[0].message.content
    }
