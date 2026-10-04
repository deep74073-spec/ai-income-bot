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


# =================================================
# AI CHAT + COMPLETE SERVICE DASHBOARD
# =================================================

SERVICE_HOME = r"""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport" content="width=device-width,initial-scale=1">

<title>YourAI - AI Services</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    background:#f7f7fb;
    color:#171717;
    font-family:Arial,sans-serif;
}

.header{
    position:sticky;
    top:0;
    z-index:50;
    height:62px;
    background:white;
    border-bottom:1px solid #e8e8ed;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 18px;
}

.brand{
    display:flex;
    align-items:center;
    gap:9px;
    font-weight:700;
    font-size:19px;
}

.brand-icon{
    width:32px;
    height:32px;
    border-radius:9px;
    background:#111;
    display:flex;
    align-items:center;
    justify-content:center;
}

.brand-icon svg{
    width:18px;
    height:18px;
    stroke:white;
    fill:none;
    stroke-width:2;
}

.ask-top{
    border:0;
    background:#111;
    color:white;
    padding:10px 15px;
    border-radius:10px;
    font-size:14px;
    font-weight:600;
}

.hero{
    max-width:1050px;
    margin:auto;
    padding:34px 18px 20px;
}

.hero h1{
    margin:0;
    font-size:30px;
}

.hero p{
    color:#777;
    margin:9px 0 22px;
}

.ask-box{
    background:white;
    border:1px solid #e4e4e8;
    border-radius:18px;
    padding:12px;
    box-shadow:0 4px 20px rgba(0,0,0,.04);
}

.ask-row{
    display:flex;
    gap:10px;
    align-items:flex-end;
}

.ask-box textarea{
    flex:1;
    border:0;
    outline:0;
    resize:none;
    min-height:48px;
    max-height:130px;
    font-size:16px;
    padding:10px;
    font-family:inherit;
}

.send{
    width:42px;
    height:42px;
    border:0;
    border-radius:50%;
    background:#111;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
}

.send svg{
    width:18px;
    height:18px;
    stroke:white;
    fill:none;
    stroke-width:2;
}

.response{
    display:none;
    margin-top:15px;
    background:#fafafa;
    border:1px solid #e5e5e5;
    border-radius:14px;
    padding:15px;
    white-space:pre-wrap;
    line-height:1.6;
}

.services{
    max-width:1050px;
    margin:auto;
    padding:5px 18px 50px;
}

.category{
    margin:25px 0 12px;
}

.category h2{
    font-size:17px;
    margin:0 0 12px;
}

.grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:10px;
}

.service{
    background:white;
    border:1px solid #e5e5e9;
    border-radius:14px;
    padding:16px 12px;
    text-align:left;
    cursor:pointer;
    transition:.15s;
}

.service:hover{
    transform:translateY(-2px);
    border-color:#bbb;
    box-shadow:0 5px 18px rgba(0,0,0,.06);
}

.icon{
    width:38px;
    height:38px;
    border-radius:10px;
    background:#f1f1f3;
    display:flex;
    align-items:center;
    justify-content:center;
    margin-bottom:10px;
}

.icon svg{
    width:21px;
    height:21px;
    stroke:#111;
    fill:none;
    stroke-width:1.8;
}

.service strong{
    display:block;
    font-size:14px;
}

.service span{
    display:block;
    color:#888;
    font-size:11px;
    margin-top:4px;
}

.badge{
    display:inline-block;
    margin-top:7px;
    font-size:9px;
    border-radius:5px;
    padding:3px 6px;
    background:#eee;
    color:#555;
}

.footer{
    text-align:center;
    color:#999;
    font-size:12px;
    padding:30px;
}

@media(max-width:800px){

    .grid{
        grid-template-columns:repeat(2,1fr);
    }

    .hero h1{
        font-size:25px;
    }

}

@media(max-width:430px){

    .header{
        padding:0 12px;
    }

    .grid{
        grid-template-columns:repeat(2,1fr);
        gap:8px;
    }

    .service{
        padding:13px 10px;
    }

    .service strong{
        font-size:13px;
    }

}

</style>

</head>

<body>


<header class="header">

<div class="brand">

<div class="brand-icon">

<svg viewBox="0 0 24 24">
<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>
</svg>

</div>

YourAI

</div>


<button class="ask-top" onclick="focusAsk()">
Ask AI
</button>

</header>


<section class="hero">

<h1>What can I help you create?</h1>

<p>
Ask AI anything or choose a service below.
</p>


<div class="ask-box">

<div class="ask-row">

<textarea
id="prompt"
placeholder="Ask anything..."
onkeydown="keySend(event)"
></textarea>


<button class="send" onclick="askAI()">

<svg viewBox="0 0 24 24">
<path d="M4 12h15"/>
<path d="M13 5l7 7-7 7"/>
</svg>

</button>

</div>

<div id="response" class="response"></div>

</div>

</section>


<section class="services">


<!-- CONTENT -->

<div class="category">

<h2>✍️ AI Content</h2>

<div class="grid">

<button class="service" onclick="choose('Instagram Post')">
<div class="icon">✦</div>
<strong>Instagram Post</strong>
<span>Posts & captions</span>
</button>

<button class="service" onclick="choose('Facebook Post')">
<div class="icon">F</div>
<strong>Facebook Post</strong>
<span>Social content</span>
</button>

<button class="service" onclick="choose('WhatsApp Promotion')">
<div class="icon">W</div>
<strong>WhatsApp</strong>
<span>Promotional messages</span>
</button>

<button class="service" onclick="choose('Advertisement Copy')">
<div class="icon">↗</div>
<strong>Advertisement</strong>
<span>Ad copy & ideas</span>
</button>

<button class="service" onclick="choose('Product Description')">
<div class="icon">□</div>
<strong>Product Description</strong>
<span>Product copy</span>
</button>

<button class="service" onclick="choose('YouTube Description')">
<div class="icon">▶</div>
<strong>YouTube</strong>
<span>Video descriptions</span>
</button>

<button class="service" onclick="choose('Blog / Article')">
<div class="icon">≡</div>
<strong>Blog / Article</strong>
<span>Long-form writing</span>
</button>

<button class="service" onclick="choose('SEO Content')">
<div class="icon">⌕</div>
<strong>SEO Content</strong>
<span>Search content</span>
</button>

<button class="service" onclick="choose('Email Writer')">
<div class="icon">@</div>
<strong>Email Writer</strong>
<span>Professional emails</span>
</button>

</div>
</div>


<!-- CREATIVE -->

<div class="category">

<h2>🎨 AI Creative</h2>

<div class="grid">

<button class="service" onclick="choose('AI Image')">
<div class="icon">◇</div>
<strong>AI Image</strong>
<span>Image generation</span>
</button>

<button class="service" onclick="choose('Image Enhancement')">
<div class="icon">↗</div>
<strong>Image Enhancement</strong>
<span>Improve images</span>
</button>

<button class="service" onclick="choose('Background Removal')">
<div class="icon">□</div>
<strong>Background Removal</strong>
<span>Remove background</span>
</button>

<button class="service" onclick="choose('Logo & Brand Ideas')">
<div class="icon">◎</div>
<strong>Logo & Brand</strong>
<span>Brand concepts</span>
</button>

<button class="service" onclick="choose('Poster / Flyer')">
<div class="icon">▣</div>
<strong>Poster / Flyer</strong>
<span>Marketing designs</span>
</button>

<button class="service" onclick="choose('Thumbnail')">
<div class="icon">▤</div>
<strong>Thumbnail</strong>
<span>Video thumbnails</span>
</button>

</div>
</div>


<!-- VIDEO AUDIO -->

<div class="category">

<h2>🎬 AI Video & Audio</h2>

<div class="grid">

<button class="service" onclick="choose('AI Video')">
<div class="icon">▶</div>
<strong>AI Video</strong>
<span>Video creation</span>
</button>

<button class="service" onclick="choose('Reel / Short Script')">
<div class="icon">▷</div>
<strong>Reel / Short Script</strong>
<span>Short-form scripts</span>
</button>

<button class="service" onclick="choose('AI Voice')">
<div class="icon">)))</div>
<strong>AI Voice</strong>
<span>Voice generation</span>
</button>

<button class="service" onclick="choose('Text to Speech')">
<div class="icon">T</div>
<strong>Text to Speech</strong>
<span>Speech generation</span>
</button>

<button class="service" onclick="choose('Subtitle Generator')">
<div class="icon">≡</div>
<strong>Subtitles</strong>
<span>Generate captions</span>
</button>

<button class="service" onclick="choose('Audio Tools')">
<div class="icon">♪</div>
<strong>Audio Tools</strong>
<span>Audio workflows</span>
</button>

</div>
</div>


<!-- DEVELOPMENT -->

<div class="category">

<h2>💻 AI Development</h2>

<div class="grid">

<button class="service" onclick="choose('Web App Builder')">
<div class="icon">&lt;/&gt;</div>
<strong>Web App Builder</strong>
<span>Build web apps</span>
</button>

<button class="service" onclick="choose('Android App Builder')">
<div class="icon">□</div>
<strong>Android App</strong>
<span>Build Android apps</span>
</button>

<button class="service" onclick="choose('Web Game Builder')">
<div class="icon">◆</div>
<strong>Web Game</strong>
<span>Build browser games</span>
</button>

<button class="service" onclick="choose('Android Game')">
<div class="icon">◇</div>
<strong>Android Game</strong>
<span>Game development</span>
</button>

<button class="service" onclick="choose('Plugin Builder')">
<div class="icon">⊞</div>
<strong>Plugin Builder</strong>
<span>Build plugins</span>
</button>

<button class="service" onclick="choose('API Builder')">
<div class="icon">⇄</div>
<strong>API Builder</strong>
<span>Build APIs</span>
</button>

<button class="service" onclick="choose('Automation Tool')">
<div class="icon">⚙</div>
<strong>Automation Tool</strong>
<span>Automate tasks</span>
</button>

<button class="service" onclick="choose('Code Generator')">
<div class="icon">&lt;/&gt;</div>
<strong>Code Generator</strong>
<span>Generate code</span>
</button>

<button class="service" onclick="choose('Bug Fix')">
<div class="icon">!</div>
<strong>Bug Fix</strong>
<span>Debug code</span>
</button>

</div>
</div>


<!-- AUTOMATION -->

<div class="category">

<h2>⚙️ AI Automation</h2>

<div class="grid">

<button class="service" onclick="choose('AI Chatbot')">
<div class="icon">◇</div>
<strong>AI Chatbot</strong>
<span>Build chatbots</span>
</button>

<button class="service" onclick="choose('Customer Support Bot')">
<div class="icon">?</div>
<strong>Customer Support</strong>
<span>Support automation</span>
</button>

<button class="service" onclick="choose('FAQ Bot')">
<div class="icon">?</div>
<strong>FAQ Bot</strong>
<span>Answer FAQs</span>
</button>

<button class="service" onclick="choose('Email Automation')">
<div class="icon">@</div>
<strong>Email Automation</strong>
<span>Automate email</span>
</button>

<button class="service" onclick="choose('WhatsApp Automation')">
<div class="icon">W</div>
<strong>WhatsApp Automation</strong>
<span>Automate WhatsApp</span>
</button>

<button class="service" onclick="choose('Lead Generator')">
<div class="icon">◎</div>
<strong>Lead Generator</strong>
<span>Generate leads</span>
</button>

<button class="service" onclick="choose('Business Workflow')">
<div class="icon">↻</div>
<strong>Business Workflow</strong>
<span>Automate workflows</span>
</button>

</div>
</div>


<!-- DOCUMENTS -->

<div class="category">

<h2>📄 AI Documents</h2>

<div class="grid">

<button class="service" onclick="choose('Resume / CV')">
<div class="icon">▤</div>
<strong>Resume / CV</strong>
<span>Create resumes</span>
</button>

<button class="service" onclick="choose('Cover Letter')">
<div class="icon">✉</div>
<strong>Cover Letter</strong>
<span>Job applications</span>
</button>

<button class="service" onclick="choose('PDF Summarizer')">
<div class="icon">▤</div>
<strong>PDF Summarizer</strong>
<span>Summarize documents</span>
</button>

<button class="service" onclick="choose('Notes Generator')">
<div class="icon">≡</div>
<strong>Notes Generator</strong>
<span>Create notes</span>
</button>

<button class="service" onclick="choose('Report Generator')">
<div class="icon">▥</div>
<strong>Report Generator</strong>
<span>Generate reports</span>
</button>

<button class="service" onclick="choose('Presentation / PPT')">
<div class="icon">▣</div>
<strong>Presentation / PPT</strong>
<span>Create presentations</span>
</button>

</div>
</div>


<!-- BUSINESS -->

<div class="category">

<h2>💼 AI Business</h2>

<div class="grid">

<button class="service" onclick="choose('Business Ideas')">
<div class="icon">✦</div>
<strong>Business Ideas</strong>
<span>Find opportunities</span>
</button>

<button class="service" onclick="choose('Business Plan')">
<div class="icon">▥</div>
<strong>Business Plan</strong>
<span>Plan your business</span>
</button>

<button class="service" onclick="choose('Marketing Plan')">
<div class="icon">↗</div>
<strong>Marketing Plan</strong>
<span>Marketing strategy</span>
</button>

<button class="service" onclick="choose('Market Research')">
<div class="icon">⌕</div>
<strong>Market Research</strong>
<span>Research markets</span>
</button>

<button class="service" onclick="choose('Brand Name Generator')">
<div class="icon">A</div>
<strong>Brand Names</strong>
<span>Generate names</span>
</button>

<button class="service" onclick="choose('Slogan Generator')">
<div class="icon">✦</div>
<strong>Slogan Generator</strong>
<span>Create slogans</span>
</button>

<button class="service" onclick="choose('Pricing Ideas')">
<div class="icon">₹</div>
<strong>Pricing Ideas</strong>
<span>Pricing strategy</span>
</button>

<button class="service" onclick="choose('Sales Copy')">
<div class="icon">↗</div>
<strong>Sales Copy</strong>
<span>Sales messaging</span>
</button>

</div>
</div>


<!-- RESEARCH -->

<div class="category">

<h2>🔎 AI Research & Tools</h2>

<div class="grid">

<button class="service" onclick="choose('AI Research')">
<div class="icon">⌕</div>
<strong>AI Research</strong>
<span>Research assistant</span>
</button>

<button class="service" onclick="choose('Summarizer')">
<div class="icon">≡</div>
<strong>Summarizer</strong>
<span>Summarize text</span>
</button>

<button class="service" onclick="choose('Translator')">
<div class="icon">A</div>
<strong>Translator</strong>
<span>Translate languages</span>
</button>

<button class="service" onclick="choose('Grammar & Rewrite')">
<div class="icon">✓</div>
<strong>Grammar & Rewrite</strong>
<span>Improve writing</span>
</button>

<button class="service" onclick="choose('Keyword Generator')">
<div class="icon">#</div>
<strong>Keyword Generator</strong>
<span>Find keywords</span>
</button>

<button class="service" onclick="choose('Prompt Generator')">
<div class="icon">✦</div>
<strong>Prompt Generator</strong>
<span>Create prompts</span>
</button>

<button class="service" onclick="choose('Prompt Optimizer')">
<div class="icon">⚡</div>
<strong>Prompt Optimizer</strong>
<span>Improve prompts</span>
</button>

<button class="service" onclick="choose('JSON Generator')">
<div class="icon">{ }</div>
<strong>JSON Generator</strong>
<span>Create JSON</span>
</button>

</div>
</div>


<!-- CUSTOM -->

<div class="category">

<h2>🚀 Custom AI</h2>

<div class="grid">

<button class="service" onclick="choose('Custom AI Project')">
<div class="icon">✦</div>
<strong>Custom AI Project</strong>
<span>Build your idea</span>
</button>

<button class="service" onclick="choose('Build My AI Tool')">
<div class="icon">⚙</div>
<strong>Build My AI Tool</strong>
<span>Custom AI solution</span>
</button>

</div>
</div>


</section>


<div class="footer">
YourAI • AI tools & services
</div>


<script>

function focusAsk(){

    document.getElementById("prompt").focus();

    window.scrollTo({
        top:0,
        behavior:"smooth"
    });

}


function choose(service){

    const input=document.getElementById("prompt");

    input.value="Help me with " + service + ": ";

    input.focus();

    window.scrollTo({
        top:0,
        behavior:"smooth"
    });

}


function keySend(e){

    if(e.key==="Enter" && !e.shiftKey){

        e.preventDefault();

        askAI();

    }

}


async function askAI(){

    const input=document.getElementById("prompt");

    const response=document.getElementById("response");

    const text=input.value.trim();

    if(!text) return;

    response.style.display="block";

    response.textContent="Thinking...";

    try{

        const r=await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:text
            })

        });

        const data=await r.json();

        response.textContent =
            data.answer ||
            data.error ||
            "No response.";

    }catch(e){

        response.textContent=
            "Unable to connect to AI.";

    }

}

</script>


</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return SERVICE_HOME


@app.post("/chat")
async def chat(request: Request):

    data = await request.json()

    prompt = str(data.get("message", "")).strip()

    if not prompt:
        return {"error": "Message is required"}

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role":"system",
                "content":"""
You are the main AI assistant of an AI services platform.

Understand the user's request and help directly.

You can help with:
content, images, video ideas, audio, coding,
web apps, Android apps, games, plugins, automation,
documents, business, research and general AI tasks.

Do not claim that an external image/video/audio/file
was actually generated unless the corresponding backend
tool is connected.

For coding requests, provide useful working code.
For content requests, create ready-to-use content.
For business requests, give practical answers.
"""
            },

            {
                "role":"user",
                "content":prompt
            }

        ]

    )

    return {
        "answer":response.choices[0].message.content
    }

