import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>AI Content Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 700px;
                margin: auto;
                padding: 20px;
            }
            input, textarea, select, button {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                box-sizing: border-box;
            }
            button {
                cursor: pointer;
                font-weight: bold;
            }
            .result {
                white-space: pre-wrap;
                background: #f5f5f5;
                padding: 15px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>AI Content Generator</h1>

        <form method="post" action="/generate">
            <label>Business / Brand</label>
            <input name="business" placeholder="Example: Sharma Bakery" required>

            <label>Topic / Offer</label>
            <textarea name="topic" placeholder="Example: Diwali special cake offer" required></textarea>

            <label>Content Type</label>
            <select name="content_type">
                <option>Instagram Post</option>
                <option>Facebook Post</option>
                <option>Product Description</option>
                <option>Advertisement</option>
                <option>YouTube Description</option>
            </select>

            <button type="submit">Generate Content</button>
        </form>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate", response_class=HTMLResponse)
def generate(
    business: str = Form(...),
    topic: str = Form(...),
    content_type: str = Form(...)
):
    prompt = f"""
Create marketing content for this business.

Business: {business}
Topic/Offer: {topic}
Content type: {content_type}

Generate:
1. Catchy title
2. Main content
3. Call to action
4. 8 relevant hashtags

Make it natural and ready to publish.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert marketing content writer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    answer = response.choices[0].message.content

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Generated Content</title>
    </head>
    <body style="font-family:Arial;max-width:700px;margin:auto;padding:20px;">
        <h1>Generated Content</h1>
        <div style="white-space:pre-wrap;background:#f5f5f5;padding:15px;">
{answer}
        </div>
        <br>
        <a href="/">← Generate another</a>
    </body>
    </html>
    """
