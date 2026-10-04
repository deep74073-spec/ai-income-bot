import os
import time
from fastapi import FastAPI, Request, Form, Request
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

/* ===== PROFESSIONAL NAVIGATION ===== */
.navbar {
    position: sticky;
    top: 0;
    z-index: 1000;
    height: 70px;
    background: rgba(255,255,255,.96);
    border-bottom: 1px solid #e8e8ed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 22px;
    backdrop-filter: blur(12px);
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 21px;
    font-weight: 800;
    text-decoration: none;
    color: #111;
}

.brand-mark {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    background: #111;
    color: white;
    display: grid;
    place-items: center;
}

.menu-btn {
    width: 44px;
    height: 44px;
    padding: 0;
    margin: 0;
    border: 1px solid #e5e5ea;
    background: white;
    color: #111;
    border-radius: 11px;
    display: grid;
    place-items: center;
    cursor: pointer;
}

.menu-btn:hover {
    background: #f5f5f7;
}

.menu-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.28);
    z-index: 1090;
    opacity: 0;
    visibility: hidden;
    transition: .2s ease;
}

.menu-overlay.open {
    opacity: 1;
    visibility: visible;
}

.side-menu {
    position: fixed;
    top: 0;
    right: 0;
    width: min(370px, 88vw);
    height: 100vh;
    background: white;
    z-index: 1100;
    transform: translateX(100%);
    transition: transform .25s ease;
    box-shadow: -12px 0 35px rgba(0,0,0,.12);
    overflow-y: auto;
}

.side-menu.open {
    transform: translateX(0);
}

.menu-head {
    height: 70px;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #eee;
}

.menu-title {
    font-size: 18px;
    font-weight: 800;
}

.close-btn {
    width: 40px;
    height: 40px;
    border: 1px solid #eee;
    background: #f7f7f8;
    color: #111;
    border-radius: 10px;
    padding: 0;
    margin: 0;
    cursor: pointer;
}

.menu-section {
    padding: 20px;
}

.menu-label {
    font-size: 12px;
    font-weight: 800;
    color: #8a8a93;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 10px;
}

.menu-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 13px 12px;
    margin: 3px 0;
    color: #17171a;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 600;
}

.menu-item:hover {
    background: #f5f5f7;
}

.menu-icon {
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: #f3f3f5;
}

.menu-item.game {
    background: #111;
    color: white;
    margin-top: 8px;
}

.menu-item.game:hover {
    background: #222;
}

.menu-item.game .menu-icon {
    background: #2d2d31;
}

.menu-sub {
    margin-left: 51px;
    border-left: 1px solid #e5e5e8;
    padding-left: 12px;
}

.menu-sub a {
    display: block;
    padding: 9px 10px;
    color: #666;
    text-decoration: none;
    font-size: 14px;
    border-radius: 8px;
}

.menu-sub a:hover {
    background: #f5f5f7;
    color: #111;
}

@media (max-width: 600px) {
    .navbar {
        padding: 0 15px;
    }

    .brand {
        font-size: 19px;
    }

    .hero {
        padding-top: 45px;
    }
}

</style>
</head>

<body>

<nav class="navbar">

<a class="brand" href="/">
    <span class="brand-mark">
        <svg width="21" height="21" viewBox="0 0 24 24" fill="none">
            <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"
                  fill="currentColor"/>
            <path d="M19 16l.7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16z"
                  fill="currentColor"/>
        </svg>
    </span>
    ContentAI
</a>

<button class="menu-btn" onclick="openMenu()" aria-label="Open menu">
    <svg width="23" height="23" viewBox="0 0 24 24" fill="none">
        <path d="M4 6h16M4 12h16M4 18h16"
              stroke="currentColor" stroke-width="2"
              stroke-linecap="round"/>
    </svg>
</button>

</nav>

<div class="menu-overlay" id="menuOverlay" onclick="closeMenu()"></div>

<aside class="side-menu" id="sideMenu">

    <div class="menu-head">
        <div class="menu-title">Services</div>

        <button class="close-btn" onclick="closeMenu()" aria-label="Close menu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M6 6l12 12M18 6L6 18"
                      stroke="currentColor" stroke-width="2"
                      stroke-linecap="round"/>
            </svg>
        </button>
    </div>

    <div class="menu-section">

        <div class="menu-label">AI Content</div>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="3" width="18" height="18" rx="5"
                          stroke="currentColor" stroke-width="1.8"/>
                    <circle cx="12" cy="12" r="4"
                            stroke="currentColor" stroke-width="1.8"/>
                    <circle cx="17.5" cy="6.5" r="1"
                            fill="currentColor"/>
                </svg>
            </span>
            Instagram Content
        </a>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3z"
                          stroke="currentColor" stroke-width="1.8"/>
                    <path d="M8.5 8.5c.4-.5.8-.5 1.1-.1l1 1.3c.2.3.2.6 0 .9l-.5.6c.8 1.4 1.8 2.3 3.2 3.1l.6-.5c.3-.2.6-.2.9 0l1.3 1c.4.3.4.7-.1 1.1-.6.6-1.5.8-2.3.5-2.8-.9-5.2-3.3-6.1-6.1-.3-.8-.1-1.7.5-2.3z"
                          stroke="currentColor" stroke-width="1.3"/>
                </svg>
            </span>
            WhatsApp Promotion
        </a>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M4 7h16v13H4z"
                          stroke="currentColor" stroke-width="1.8"/>
                    <path d="M8 7V5h8v2M8 12h8M8 16h5"
                          stroke="currentColor" stroke-width="1.8"
                          stroke-linecap="round"/>
                </svg>
            </span>
            Product Description
        </a>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M4 20V10M10 20V4M16 20v-7M22 20H2"
                          stroke="currentColor" stroke-width="1.8"
                          stroke-linecap="round"/>
                </svg>
            </span>
            Advertisement Copy
        </a>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="5" width="18" height="14" rx="3"
                          stroke="currentColor" stroke-width="1.8"/>
                    <path d="M10 9l5 3-5 3V9z" fill="currentColor"/>
                </svg>
            </span>
            YouTube Description
        </a>

        <div class="menu-label" style="margin-top:24px;">AI Development</div>

        <a class="menu-item game" href="#game-builder" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="21" height="21" viewBox="0 0 24 24" fill="none">
                    <path d="M8 13l-2 4a2.5 2.5 0 0 0 4.3 2.4L12 17l1.7 2.4A2.5 2.5 0 0 0 18 17l-2-4"
                          stroke="currentColor" stroke-width="1.8"
                          stroke-linecap="round"/>
                    <rect x="6" y="5" width="12" height="10" rx="5"
                          stroke="currentColor" stroke-width="1.8"/>
                    <path d="M9 10h3M10.5 8.5v3"
                          stroke="currentColor" stroke-width="1.8"
                          stroke-linecap="round"/>
                    <circle cx="15.5" cy="9.5" r=".8" fill="currentColor"/>
                </svg>
            </span>
            Game &amp; App Builder
        </a>

        <div class="menu-sub" id="game-builder">
            <a href="#generator" onclick="closeMenu()">Web Game</a>
            <a href="#generator" onclick="closeMenu()">Android App</a>
            <a href="#generator" onclick="closeMenu()">Plugin</a>
            <a href="#generator" onclick="closeMenu()">Custom AI Project</a>
        </div>

        <div class="menu-label" style="margin-top:24px;">More</div>

        <a class="menu-item" href="#generator" onclick="closeMenu()">
            <span class="menu-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="9"
                            stroke="currentColor" stroke-width="1.8"/>
                    <path d="M12 10v6M12 7.5v.2"
                          stroke="currentColor" stroke-width="1.8"
                          stroke-linecap="round"/>
                </svg>
            </span>
            How It Works
        </a>

    </div>
</aside>


<section class="hero">

<h1>ContentAI</h1>

<p>
Create social media posts, WhatsApp promotions and product descriptions with AI in seconds.
</p>

<a class="btn" href="#generator">Try Free</a>

<div class="limit">3 free generations per day</div>

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


<script>
function openMenu() {
    document.getElementById("sideMenu").classList.add("open");
    document.getElementById("menuOverlay").classList.add("open");
    document.body.style.overflow = "hidden";
}

function closeMenu() {
    document.getElementById("sideMenu").classList.remove("open");
    document.getElementById("menuOverlay").classList.remove("open");
    document.body.style.overflow = "";
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        closeMenu();
    }
});
</script>

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



# =========================
# AI SERVICE ROUTER
# =========================

def detect_service(prompt: str) -> str:
    text = prompt.lower()

    if any(x in text for x in ["instagram", "facebook post", "caption", "hashtag", "advertisement", "ad copy", "whatsapp promotion"]):
        return "content"

    if any(x in text for x in ["image", "photo", "poster", "thumbnail", "logo", "background remove"]):
        return "image"

    if any(x in text for x in ["video", "reel", "short video", "video script"]):
        return "video"

    if any(x in text for x in ["voice", "voiceover", "voice over", "text to speech", "tts"]):
        return "voice"

    if any(x in text for x in ["website", "web app", "html", "css", "javascript", "android app", "apk", "game", "plugin", "api", "code"]):
        return "development"

    if any(x in text for x in ["resume", "cv", "cover letter", "pdf", "report", "document", "presentation", "ppt"]):
        return "documents"

    if any(x in text for x in ["business idea", "business plan", "marketing plan", "brand name", "slogan", "market research", "sales"]):
        return "business"

    if any(x in text for x in ["translate", "translation", "summarize", "summary", "rewrite", "grammar", "seo", "keyword", "research"]):
        return "research"

    if any(x in text for x in ["automation", "automate", "chatbot", "customer support", "lead generation", "workflow"]):
        return "automation"

    return "general"


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    prompt = str(data.get("message", "")).strip()

    if not prompt:
        return {"error": "Message is required"}

    service = detect_service(prompt)

    system_prompt = f"""
You are the main AI assistant of an AI services platform.

Detected service category: {service}

Your job:
- Understand the user's request.
- Give a useful direct answer.
- If the request requires creation, provide the actual useful output.
- Do not invent facts about a user's business, product, prices, phone numbers,
  addresses, features, certifications or other real-world details.
- Ask for missing information only when it is genuinely required.
- For coding requests, provide practical working code.
- For business/content requests, make the result ready to use.
- Be concise but helpful.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
    )

    return {
        "service": service,
        "answer": response.choices[0].message.content
    }



CHAT_HOME = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YourAI</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:#212121;
    color:#fff;
}

.app{
    height:100vh;
    display:flex;
    flex-direction:column;
}

.header{
    height:60px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 16px;
    border-bottom:1px solid #333;
}

.logo{
    font-size:19px;
    font-weight:700;
}

.menu{
    width:42px;
    height:42px;
    border:0;
    border-radius:10px;
    background:#2f2f2f;
    color:white;
    font-size:21px;
}

.messages{
    flex:1;
    overflow-y:auto;
    padding:30px 18px 150px;
}

.welcome{
    min-height:65%;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    text-align:center;
}

.welcome h1{
    font-size:30px;
    margin-bottom:8px;
}

.welcome p{
    color:#aaa;
    margin:0;
}

.message{
    max-width:760px;
    margin:0 auto 25px;
    line-height:1.6;
    white-space:pre-wrap;
}

.user{
    background:#2f2f2f;
    border-radius:18px;
    padding:12px 16px;
    margin-left:auto;
    width:fit-content;
    max-width:80%;
}

.ai{
    padding:8px 2px;
}

.composer-wrap{
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    background:linear-gradient(transparent,#212121 30%);
    padding:25px 16px 20px;
}

.composer{
    max-width:760px;
    margin:auto;
    background:#2f2f2f;
    border:1px solid #444;
    border-radius:18px;
    padding:10px 12px;
}

textarea{
    width:100%;
    border:0;
    outline:0;
    resize:none;
    background:transparent;
    color:#fff;
    font-size:16px;
    min-height:48px;
    max-height:180px;
}

.row{
    display:flex;
    justify-content:flex-end;
}

.send{
    width:38px;
    height:38px;
    border:0;
    border-radius:50%;
    background:#fff;
    color:#111;
    font-size:18px;
}

.status{
    text-align:center;
    color:#888;
    font-size:12px;
    margin-top:7px;
}

@media(max-width:600px){
    .welcome h1{font-size:25px}
    .messages{padding-left:12px;padding-right:12px}
}
</style>
</head>

<body>

<div class="app">

<header class="header">
    <div class="logo">✨ YourAI</div>
    <button class="menu" onclick="openServices()">☰</button>
</header>

<main id="messages" class="messages">

    <div id="welcome" class="welcome">
        <h1>How can I help you?</h1>
        <p>Ask anything or choose a service from the menu.</p>
    </div>

</main>

<div class="composer-wrap">

    <div class="composer">

        <textarea
            id="prompt"
            rows="1"
            placeholder="Message YourAI..."
            onkeydown="handleKey(event)"
        ></textarea>

        <div class="row">
            <button class="send" onclick="sendMessage()">↑</button>
        </div>

    </div>

    <div class="status">
        YourAI can make mistakes. Check important information.
    </div>

</div>

<script>

function openServices(){
    /*
      Existing hamburger/service navigation remains available.
      Hash is used so the existing menu system can handle it.
    */
    location.hash="services";
}

function handleKey(e){
    if(e.key==="Enter" && !e.shiftKey){
        e.preventDefault();
        sendMessage();
    }
}

function addMessage(text,type){

    const messages=document.getElementById("messages");
    const welcome=document.getElementById("welcome");

    if(welcome) welcome.remove();

    const div=document.createElement("div");
    div.className="message";

    if(type==="user"){
        div.innerHTML='<div class="user"></div>';
        div.querySelector(".user").textContent=text;
    }else{
        div.innerHTML='<div class="ai"></div>';
        div.querySelector(".ai").textContent=text;
    }

    messages.appendChild(div);
    messages.scrollTop=messages.scrollHeight;
}

async function sendMessage(){

    const input=document.getElementById("prompt");
    const message=input.value.trim();

    if(!message) return;

    input.value="";

    addMessage(message,"user");
    addMessage("Thinking...","ai");

    const messages=document.getElementById("messages");
    const aiMessages=messages.querySelectorAll(".ai");
    const currentAI=aiMessages[aiMessages.length-1];

    try{

        const response=await fetch("/chat",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:message
            })
        });

        const data=await response.json();

        if(data.error){
            currentAI.textContent=data.error;
        }else{
            currentAI.textContent=data.answer;
        }

    }catch(error){
        currentAI.textContent="Something went wrong. Please try again.";
    }

    messages.scrollTop=messages.scrollHeight;
}

</script>

</div>

</body>
</html>
"""

@app.get("/chat-home", response_class=HTMLResponse)
def chat_home():
    return CHAT_HOME
