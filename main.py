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
    font-family: Arial;
    max-width: 700px;
    margin: auto;
    padding: 20px;
    background: #fafafa;
}
h1 { text-align: center; }
input, textarea, select, button {
    width: 100%;
    padding: 12px;
    margin: 8px 0 15px;
    box-sizing: border-box;
    border-radius: 8px;
    border: 1px solid #ccc;
}
textarea { min-height: 100px; }
button {
    background: #111;
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
}
small { color: #666; }
</style>
</head>

<body>

<h1>🚀 AI Content Generator</h1>

<form method="post" action="/generate">

<label>Business / Brand</label>
<input name="business" placeholder="Example: Sharma Bakery" required>

<label>Topic / Offer</label>
<textarea name="topic" placeholder="Example: Diwali special cake offer" required></textarea>

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

Create ready-to-publish marketing content.

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

STRICT FACT RULES:
- Use ONLY facts explicitly provided by the user.
- Never invent prices, ingredients, discounts, dates, phone numbers,
  addresses, delivery options, product features, awards, certifications,
  guarantees, or business claims.
- Do not use unverified claims such as "best", "premium", "fresh",
  "perfectly sweet", "high quality", "handcrafted", "made with love",
  "perfect for everyone", or similar claims unless explicitly provided.
- Do not create fake contact information.
- Creative wording is allowed only when it does not introduce a new
  factual claim.
- If information is missing, simply leave it out.
- Keep the result natural and ready to publish.

Length instructions:
Short = concise social media copy.
Normal = balanced social media copy.
Detailed = longer but still focused copy.

Generate exactly:
1. Catchy Title
2. Main Content
3. Call To Action
4. 8 relevant hashtags
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
<title>Generated Content</title>

<style>
body {{
    font-family: Arial;
    max-width: 700px;
    margin: auto;
    padding: 20px;
    background: #fafafa;
}}

.result {{
    white-space: pre-wrap;
    background: white;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #ddd;
    line-height: 1.6;
}}

.actions {{
    display: flex;
    gap: 10px;
    margin-top: 15px;
}}

button, a {{
    flex: 1;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
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

.message {{
    margin-top: 10px;
    color: green;
    font-weight: bold;
    text-align: center;
}}
</style>
</head>

<body>

<h1>✅ Generated Content</h1>

<div class="result" id="content">{safe_answer}</div>

<div class="actions">
<button onclick="copyContent()">📋 Copy</button>
<a href="/">🔄 Generate Again</a>
</div>

<div class="message" id="message"></div>

<script>
function copyContent() {{
    const text = document.getElementById("content").innerText;

    navigator.clipboard.writeText(text)
    .then(function() {{
        document.getElementById("message").innerText =
        "✅ Content copied!";
    }})
    .catch(function() {{
        document.getElementById("message").innerText =
        "Please select and copy the content manually.";
    }});
}}
</script>

</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
