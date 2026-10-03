import os
import time
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Simple in-memory free usage counter.
# Note: Render restarts can reset this counter.
usage = {}
FREE_LIMIT = 3


def get_usage(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()

    if ip not in usage:
        usage[ip] = {"count": 0, "started": now}

    # Reset after 24 hours
    if now - usage[ip]["started"] >= 86400:
        usage[ip] = {"count": 0, "started": now}

    return ip


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

.limit {
    display: inline-block;
    margin-top: 15px;
    padding: 8px 14px;
    background: #f0f0f0;
    border-radius: 20px;
    font-size: 14px;
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

.icon {
    width: 54px;
    height: 54px;
    margin: auto auto 15px;
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

textarea {
    min-height: 100px;
}

button {
    background: #111;
    color: white;
    border: 0;
    font-weight: bold;
    cursor: pointer;
}

label {
    font-weight: bold;
}
</style>
</head>

<body>

<section class="hero">

<h1>✨ ContentAI</h1>

<p>
Create social media posts, WhatsApp promotions and product descriptions with AI in seconds.
</p>

<a class="btn" href="#generator">🚀 Try Free</a>

<div class="limit">🎁 3 free generations per day</div>

</section>


<section class="features">

<div class="card">

<div class="icon">
<svg viewBox="0 0 24 24" width="54" height="54" aria-label="Instagram">
<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/>
<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/>
<circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>
</svg>
</div>

<h2>Instagram</h2>
<p>Create ready-to-publish Instagram content.</p>

</div>


<div class="card">

<div class="icon">
<svg viewBox="0 0 24 24" width="54" height="54" aria-label="WhatsApp">
<path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3z"
fill="none" stroke="currentColor" stroke-width="2"/>
<path d="M8.5 8.5c.4-.5.8-.5 1.1-.1l1 1.3c.2.3.2.6 0 .9l-.5.6c.8 1.4 1.8 2.3 3.2 3.1l.6-.5c.3-.2.6-.2.9 0l1.3 1c.4.3.4.7-.1 1.1-.6.6-1.5.8-2.3.5-2.8-.9-5.2-3.3-6.1-6.1-.3-.8-.1-1.7.5-2.3z"
fill="none" stroke="currentColor" stroke-width="1.5"/>
</svg>
</div>

<h2>WhatsApp</h2>
<p>Create promotional messages ready to share.</p>

</div>


<div class="card">

<div class="icon">
<svg viewBox="0 0 24 24" width="54" height="54" aria-label="Product">
<path d="M4 7h16v13H4z" fill="none" stroke="currentColor" stroke-width="2"/>
<path d="M8 7V5h8v2" fill="none" stroke="currentColor" stroke-width="2"/>
<path d="M8 12h8M8 16h5" stroke="currentColor" stroke-width="2"/>
</svg>
</div>

<h2>Product Copy</h2>
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
    request: Request,
    business: str = Form(...),
    topic: str = Form(...),
    details: str = Form(""),
    content_type: str = Form(...),
    language: str = Form(...),
    tone: str = Form(...),
    length: str = Form(...)
):

    ip = get_usage(request)

    if usage[ip]["count"] >= FREE_LIMIT:
        return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Limit</title>
<style>
body {
    font-family: Arial;
    text-align: center;
    padding: 60px 20px;
    background: #f7f7fb;
}
.card {
    max-width: 500px;
    margin: auto;
    background: white;
    padding: 30px;
    border-radius: 15px;
}
a {
    display: inline-block;
    margin-top: 20px;
    padding: 12px 20px;
    background: #111;
    color: white;
    text-decoration: none;
    border-radius: 8px;
}
</style>
</head>
<body>
<div class="card">
<h1>🎁 Free Limit Reached</h1>
<p>You have used your 3 free generations for today.</p>
<p>Come back tomorrow for more free generations.</p>
<a href="/">← Back to ContentAI</a>
</div>
</body>
</html>
"""

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
- Do not make unsupported claims such as best, premium, fresh,
  high quality, perfectly sweet, handcrafted, made with love, etc.
- Never create fake contact information.
- If information is missing, leave it out.
- Creative wording must not introduce new factual claims.

Create:

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

    usage[ip]["count"] += 1
    remaining = FREE_LIMIT - usage[ip]["count"]

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
.actions {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
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
    cursor: pointer;
}}
a {{
    background: #eee;
    color: #111;
}}
.remaining {{
    text-align: center;
    color: #666;
}}
</style>
</head>

<body>

<h1>✅ Your AI Content</h1>

<p class="remaining">🎁 {remaining} free generation(s) remaining today</p>

<div class="card">
<div class="content" id="content">{safe_answer}</div>

<div class="actions">

<button onclick="copyContent()">📋 Copy</button>

<button onclick="shareWhatsApp()">💬 WhatsApp</button>

<a href="/">🔄 Generate Again</a>

</div>
</div>

<script>
function copyContent() {{
    const text = document.getElementById("content").innerText;

    navigator.clipboard.writeText(text)
    .then(function() {{
        alert("✅ Content copied!");
    }})
    .catch(function() {{
        alert("Please select and copy the content manually.");
    }});
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
