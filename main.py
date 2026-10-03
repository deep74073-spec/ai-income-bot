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
<title>ContentAI - AI Content Generator</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f7f7fb;
    color: #111;
}
.hero {
    text-align: center;
    padding: 60px 20px 40px;
    background: white;
}
.hero h1 {
    font-size: 42px;
    margin: 0 0 15px;
}
.hero p {
    color: #666;
    font-size: 18px;
    max-width: 600px;
    margin: auto;
}
.btn {
    display: inline-block;
    margin-top: 25px;
    padding: 14px 25px;
    background: #111;
    color: white;
    text-decoration: none;
    border-radius: 10px;
    font-weight: bold;
}
.features {
    max-width: 900px;
    margin: auto;
    padding: 40px 20px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #eee;
}
.generator {
    max-width: 700px;
    margin: 20px auto 50px;
    background: white;
    padding: 25px;
    border-radius: 15px;
}
input, textarea, select, button {
    width: 100%;
    padding: 12px;
    margin: 8px 0 15px;
    border-radius: 8px;
    border: 1px solid #ccc;
}
textarea { min-height: 100px; }
button {
    background: #111;
    color: white;
    border: 0;
    font-weight: bold;
    cursor: pointer;
}
label { font-weight: bold; }
</style>
</head>

<body>

<section class="hero">
    <h1>✨ ContentAI</h1>
    <p>Create social media posts, WhatsApp promotions and product descriptions with AI in seconds.</p>
    <a class="btn" href="#generator">🚀 Try Free</a>
</section>

<section class="features">
    <div class="card">
        <h2>📱 Social Posts</h2>
        <p>Create ready-to-publish Instagram and Facebook content.</p>
    </div>

    <div class="card">
        <h2>💬 WhatsApp</h2>
        <p>Create promotional messages that are easy to copy and share.</p>
    </div>

    <div class="card">
        <h2>📝 Product Copy</h2>
        <p>Generate clear product descriptions for your business.</p>
    </div>
</section>

<section class="generator" id="generator">
<h2>🚀 Try ContentAI Free</h2>

<form method="post" action="/generate">

<label>Business / Brand</label>
<input name="business" placeholder="Example: Sharma Bakery" required>

<label>Topic / Offer</label>
<textarea name="topic" placeholder="Example: Diwali special eggless cake offer" required></textarea>

<label>Actual Product Details</label>
<textarea name="details" placeholder="Example: Eggless cakes, starting price ₹499"></textarea>

<label>Content Type</label>
<select name="content_type">
<option>Instagram Post</option>
<option>Facebook Post</option>
<option>WhatsApp Message</option>
<option>Product Description</option>
<option>Advertisement</option>
<option>YouTube Description</option>
</select>

<label>Language</label>
<select name="language">
<option>English</option>
<option>Hindi</option>
<option>Hinglish</option>
</select>

<label>Tone</label>
<select name="tone">
<option>Professional</option>
<option>Friendly</option>
<option>Premium</option>
<option>Fun</option>
</select>

<label>Content Length</label>
<select name="length">
<option>Short</option>
<option selected>Normal</option>
<option>Detailed</option>
</select>

<button type="submit">✨ Generate Content</button>

</form>
</section>

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
    details: str = Form(""),
    content_type: str = Form(...),
    language: str = Form(...),
    tone: str = Form(...),
    length: str = Form(...)
):

    prompt = f"""
You are a factual marketing content writer.

Business:
{business}

Topic/Offer:
{topic}

Actual Product Details:
{details}

Content Type:
{content_type}

Language:
{language}

Tone:
{tone}

Length:
{length}

STRICT RULES:
- Use ONLY facts explicitly provided by the user.
- Never invent prices, ingredients, discounts, dates, phone numbers,
  addresses, delivery options, product features, awards, certifications,
  guarantees, or business claims.
- Do not claim something is best, premium, fresh, high quality,
  perfectly sweet, handcrafted, made with love, or similar unless
  explicitly provided.
- Never create fake contact information.
- If information is missing, leave it out.
- Creative wording must not introduce new factual claims.

Create THREE sections:

SOCIAL MEDIA
Catchy Title
Main Content
Call To Action
8 relevant hashtags

WHATSAPP
A short WhatsApp-ready promotional message.

PRODUCT DESCRIPTION
A concise product description.

Keep everything natural and ready to copy.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a careful marketing writer. Never invent business facts."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    answer = response.choices[0].message.content

    safe_answer = (
        answer.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ContentAI Result</title>
<style>
body {{
    font-family: Arial;
    max-width: 800px;
    margin: auto;
    padding: 20px;
    background: #f7f7fb;
}}
.card {{
    background: white;
    padding: 20px;
    margin: 15px 0;
    border-radius: 12px;
    border: 1px solid #ddd;
}}
.content {{
    white-space: pre-wrap;
    line-height: 1.6;
}}
button, a {{
    display: inline-block;
    padding: 12px 18px;
    margin-top: 12px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
}}
button {{
    background: #111;
    color: white;
    border: none;
}}
a {{
    background: #eee;
    color: #111;
}}
</style>
</head>

<body>

<h1>✅ Your AI Content</h1>

<div class="card">
<h2>📄 Generated Content</h2>
<div class="content" id="content">{safe_answer}</div>

<button onclick="copyContent()">📋 Copy All</button>
<button onclick="shareWhatsApp()">💬 WhatsApp</button>
</div>

<a href="/">🔄 Create Another</a>

<script>
function copyContent() {{
    const text = document.getElementById("content").innerText;
    navigator.clipboard.writeText(text);
    alert("✅ Content copied!");
}}

function shareWhatsApp() {{
    const text = document.getElementById("content").innerText;
    window.open(
        "https://wa.me/?text=" + encodeURIComponent(text),
        "_blank"
    );
}}
</script>

</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
