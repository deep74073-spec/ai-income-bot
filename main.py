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

    if any(x in text for x in [
        "product", "price comparison", "compare price", "best deal",
        "deal finder", "buying guide", "buyer's guide", "shopping",
        "product review", "product link", "where to buy", "which product"
    ]):
        return "shopping"

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


@app.get("/service/{service_name}", response_class=HTMLResponse)
def service_page(service_name: str):
    service = service_name.replace("-", " ").strip()

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YourAI - {service}</title>
<style>
*{{box-sizing:border-box}}
body{{
    margin:0;background:#212121;color:#fff;
    font-family:Arial,sans-serif;
}}
.header{{
    height:60px;display:flex;align-items:center;
    padding:0 16px;border-bottom:1px solid #333;
}}
.back{{
    border:0;background:#2f2f2f;color:#fff;
    border-radius:10px;padding:10px 14px;cursor:pointer;
}}
.container{{
    max-width:760px;margin:0 auto;padding:35px 18px 60px;
}}
h1{{font-size:30px;margin:0 0 10px}}
.sub{{color:#aaa;margin-bottom:28px}}
label{{
    display:block;margin:18px 0 8px;
    color:#ddd;font-weight:600;
}}
textarea,input,select{{
    width:100%;background:#2f2f2f;color:#fff;
    border:1px solid #444;border-radius:12px;
    padding:13px;font-size:15px;outline:none;
}}
textarea{{min-height:130px;resize:vertical}}
.generate{{
    width:100%;margin-top:22px;padding:14px;
    border:0;border-radius:12px;background:#fff;color:#111;
    font-size:16px;font-weight:700;cursor:pointer;
}}
#result{{
    margin-top:25px;padding:18px;background:#2f2f2f;
    border:1px solid #444;border-radius:14px;
    white-space:pre-wrap;line-height:1.6;display:none;
}}
.status{{color:#999;text-align:center;margin-top:10px;font-size:13px}}
.field-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:600px){{
    .field-grid{{grid-template-columns:1fr}}
}}
</style>
</head>

<body>
<header class="header">
<button class="back" onclick="location.href='/'">← Back</button>
</header>

<main class="container">
<h1>✨ {service}</h1>
<p class="sub">Tell YourAI what you need. The AI will automatically focus on this service.</p>

<div id="smartFields"></div>

<label>Language</label>
<select id="language">
<option>English</option>
<option>Hindi</option>
<option>Hinglish</option>
<option>Punjabi</option>
</select>

<label>Tone / Style</label>
<select id="tone">
<option>Professional</option>
<option>Friendly</option>
<option>Creative</option>
<option>Simple</option>
<option>Persuasive</option>
</select>

<label>Additional Requirements</label>
<textarea id="details" placeholder="Add any extra instructions, details, links, keywords, features, etc."></textarea>

<button class="generate" onclick="generateService()">Generate with AI</button>

<div id="result"></div>
<div class="status">YourAI can make mistakes. Check important information.</div>
</main>

<script>
const SERVICE = {service!r};

function field(label, id, placeholder){{
    return `
    <label>${{label}}</label>
    <input id="${{id}}" placeholder="${{placeholder}}">
    `;
}}

function buildFields(){{
    const box=document.getElementById("smartFields");
    let html="";

    if(["Instagram Post","Facebook Post","WhatsApp Promotion",
        "Advertisement Copy","Product Description","YouTube Description",
        "Blog / Article","SEO Content","Email Writer"].includes(SERVICE)){{
        html += field("Topic / Product / Subject","topic","What should the content be about?");
        html += field("Target Audience","audience","Who is this for?");
        html += field("Main Goal / CTA","goal","Example: Buy now, contact us, visit website");
    }}
    else if(["AI Image","Image Enhancement","Background Removal",
             "Logo & Brand Ideas","Poster / Flyer","Thumbnail"].includes(SERVICE)){{
        html += field("Subject / Main Idea","topic","What should the visual contain?");
        html += field("Style","style","Example: modern, realistic, minimal, cinematic");
        html += field("Size / Format","format","Example: square, portrait, landscape, YouTube");
    }}
    else if(["AI Video","Reel / Short Script","Subtitle Generator"].includes(SERVICE)){{
        html += field("Video Topic","topic","What is the video about?");
        html += field("Target Audience","audience","Who will watch it?");
        html += field("Duration","duration","Example: 30 seconds, 60 seconds");
    }}
    else if(["AI Voice","Text to Speech","Audio Tools"].includes(SERVICE)){{
        html += field("Text / Script","topic","Enter the text or describe the audio");
        html += field("Voice Style","style","Example: calm, energetic, professional");
    }}
    else if(["Resume / CV","Cover Letter"].includes(SERVICE)){{
        html += field("Job Role","role","Example: Software Developer");
        html += field("Experience","experience","Fresher / years of experience");
        html += field("Skills","skills","List your important skills");
    }}
    else if(["PDF Summarizer","Notes Generator","Report Generator",
             "Presentation / PPT"].includes(SERVICE)){{
        html += field("Topic / Document Subject","topic","What is the document about?");
        html += field("Audience","audience","Student, client, team, etc.");
        html += field("Length / Slides","length","Example: 5 pages or 10 slides");
    }}
    else if(["Business Ideas","Business Plan","Marketing Plan",
             "Market Research","Pricing Ideas","Sales Copy"].includes(SERVICE)){{
        html += field("Business / Product","business","What business or product?");
        html += field("Target Market","market","Who are your customers?");
        html += field("Budget","budget","Optional budget");
    }}
    else if(["Brand Name Generator","Slogan Generator"].includes(SERVICE)){{
        html += field("Business / Product","business","What is the brand about?");
        html += field("Brand Style","style","Modern, premium, fun, traditional, etc.");
    }}
    else if(["Web App Builder","Android App Builder","Web Game Builder",
             "Android Game","Plugin Builder","API Builder",
             "Automation Tool","Code Generator","Bug Fix",
             "Custom AI Project","Build My AI Tool"].includes(SERVICE)){{
        html += field("Project / Feature","project","What do you want to build or fix?");
        html += field("Technology","technology","Example: Python, JavaScript, Android");
        html += field("Requirements","requirements","Important features or constraints");
    }}
    else if(["AI Chatbot","Customer Support Bot","FAQ Bot",
             "Email Automation","WhatsApp Automation",
             "Lead Generator","Business Workflow"].includes(SERVICE)){{
        html += field("Business / Use Case","usecase","What should the automation do?");
        html += field("Target Users","users","Customers, leads, employees, etc.");
        html += field("Goal","goal","What result do you want?");
    }}
    else if(["Product Search","Price Comparison","Best Deal Finder"].includes(SERVICE)){{
        html += field("Product / Category","product","Example: wireless earbuds, laptop, shoes");
        html += field("Budget","budget","Example: ₹20,000");
        html += field("Preferred Brand","brand","Optional");
        html += field("Important Features","features","What features matter most?");
    }}
    else if(["Product Comparison"].includes(SERVICE)){{
        html += field("Product A","productA","Enter first product name or link");
        html += field("Product B","productB","Enter second product name or link");
        html += field("Comparison Criteria","criteria","Price, performance, camera, battery, etc.");
    }}
    else if(["Product Review Summary"].includes(SERVICE)){{
        html += field("Product","product","Enter product name or link");
        html += field("Review Text","reviews","Paste reviews here if available");
        html += field("What to Focus On","focus","Pros, cons, reliability, value, etc.");
    }}
    else if(["Buyers Guide"].includes(SERVICE)){{
        html += field("Product Category","category","Example: phone, laptop, headphones");
        html += field("Budget","budget","Example: ₹30,000");
        html += field("Use Case","usecase","Gaming, study, business, travel, etc.");
        html += field("Must-Have Features","features","Important requirements");
    }}
    else if(["Product Link Finder"].includes(SERVICE)){{
        html += field("Product","product","Enter product name/model");
        html += field("Variant","variant","Size, storage, color, model, etc.");
        html += field("Preferred Store","store","Optional");
    }}
    else if(["AI Research","Summarizer","Translator","Grammar & Rewrite",
             "Keyword Generator","Prompt Generator","Prompt Optimizer",
             "JSON Generator"].includes(SERVICE)){{
        html += field("Topic / Text","topic","Enter the topic, text or task");
        html += field("Desired Output","output","What should the final result look like?");
    }}
    else{{
        html += field("Main Requirement","topic","Describe what you want YourAI to do");
    }}

    box.innerHTML=html;
}}

function getValue(id){{
    const el=document.getElementById(id);
    return el ? el.value.trim() : "";
}}

async function generateService(){{
    const language=document.getElementById("language").value;
    const tone=document.getElementById("tone").value;
    const details=getValue("details");
    const result=document.getElementById("result");

    const inputs=[];
    document.querySelectorAll("#smartFields input").forEach(el=>{{
        if(el.value.trim()){{
            const label=el.previousElementSibling
                ? el.previousElementSibling.textContent
                : el.id;
            inputs.push(label + ": " + el.value.trim());
        }}
    }});

    if(!inputs.length && !details){{
        result.style.display="block";
        result.textContent="Please enter some details first.";
        return;
    }}

    result.style.display="block";
    result.textContent="Thinking...";

    const prompt =
        "SERVICE: " + SERVICE + "\\n" +
        "LANGUAGE: " + language + "\\n" +
        "TONE: " + tone + "\\n" +
        "SERVICE DETAILS:\\n" + inputs.join("\\n") + "\\n" +
        "ADDITIONAL REQUIREMENTS:\\n" + details;

    try{{
        const response=await fetch("/chat",{{
            method:"POST",
            headers:{{"Content-Type":"application/json"}},
            body:JSON.stringify({{message:prompt}})
        }});

        const data=await response.json();
        result.textContent=data.answer || data.error || "No response.";
    }}catch(e){{
        result.textContent="Something went wrong. Please try again.";
    }}
}}

buildFields();
</script>
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


<button class="ask-top" onclick="openAIChat()">
Ask AI
</button>

</header>


<section class="hero">

<h1>What can I help you create?</h1>

<p>
Ask AI anything or choose a service below.
</p>


</section>


<section class="services">


<!-- CONTENT -->

<div class="category">


<div class="service-section">
<h2>💬 AI Chat</h2>
<div class="service-grid">
<button class="service chat-service" onclick="openAIChat()">
<div class="icon">💬</div>
<strong>AI Chat</strong>
<span>Ask anything, learn, explain, solve</span>
</button>
</div>
</div>
\n<h2>✍️ AI Content</h2>

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


<!-- SHOPPING & PRICE -->

<div class="category">

<h2>🛒 Shopping & Price</h2>

<div class="grid">

<button class="service" onclick="choose('Product Search')">
<div class="icon">🔎</div>
<strong>Product Search</strong>
<span>Find products and shopping options</span>
</button>

<button class="service" onclick="choose('Price Comparison')">
<div class="icon">💰</div>
<strong>Price Comparison</strong>
<span>Compare prices across available sources</span>
</button>

<button class="service" onclick="choose('Best Deal Finder')">
<div class="icon">🏷️</div>
<strong>Best Deal Finder</strong>
<span>Find the best-value option</span>
</button>

<button class="service" onclick="choose('Product Comparison')">
<div class="icon">⚖</div>
<strong>Product Comparison</strong>
<span>Compare products, features and value</span>
</button>

<button class="service" onclick="choose('Product Review Summary')">
<div class="icon">⭐</div>
<strong>Product Review Summary</strong>
<span>Summarize product reviews</span>
</button>

<button class="service" onclick="choose('Buyers Guide')">
<div class="icon">🛍️</div>
<strong>Buyer's Guide</strong>
<span>Get help choosing a product</span>
</button>

<button class="service" onclick="choose('Product Link Finder')">
<div class="icon">🔗</div>
<strong>Product Link Finder</strong>
<span>Find available shopping links</span>
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



function openAIChat(){
    window.location.href="/chat-home";
}

function choose(service){

    const encoded = encodeURIComponent(service);
    window.location.href = "/service/" + encoded;

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


# =========================
# SMART AI SERVICE BACKEND
# =========================

SERVICE_PROMPTS = {
    "content": """
You are an expert AI content creator.
Create ready-to-use content for Instagram, Facebook, WhatsApp,
advertisements, product descriptions, YouTube descriptions,
blogs, SEO content and emails.
Do not give unnecessary explanations. Make the output usable immediately.
""",

    "image": """
You are an AI creative assistant.
Help with image prompts, poster prompts, thumbnail prompts,
logo concepts, background-removal instructions and image-editing prompts.
IMPORTANT: do not claim that an image was actually generated because
an image-generation backend is not connected yet.
Return a professional ready-to-use image prompt when appropriate.
""",

    "video": """
You are an AI video-production assistant.
Create video concepts, reels, shorts, scripts, scenes, hooks,
storyboards, shot lists and captions.
IMPORTANT: do not claim that a video was actually rendered.
""",

    "voice": """
You are an AI voice and audio assistant.
Create voiceover scripts, narration, TTS-ready text and audio plans.
IMPORTANT: do not claim that an audio file was actually generated.
""",

    "development": """
You are an expert software developer.
Build useful working code for websites, web apps, Android apps,
games, plugins, APIs, automation tools and bug fixes.
When appropriate provide complete files and explain where each file goes.
Never pretend that code was compiled, deployed or packaged unless that
actually happened.
""",

    "documents": """
You are an expert document assistant.
Create resumes, CVs, cover letters, reports, notes, presentations,
PPT outlines and document-ready content.
If the user references a PDF/file that has not been provided,
ask them to upload it rather than pretending you read it.
""",

    "business": """
You are an AI business consultant.
Help with business ideas, business plans, marketing plans,
market research frameworks, brand names, slogans, pricing and sales copy.
Give practical and realistic recommendations.
Do not invent live market data.
""",

    "research": """
You are an AI research and writing assistant.
Help with summarization, translation, rewriting, grammar,
SEO, keywords, prompts and research.
Do not claim to have performed live web research unless a web-search
backend is actually connected.
""",

    "shopping": """
You are an AI shopping research and comparison assistant.
Help users search for products, compare products and prices, summarize reviews, and make buying decisions.

IMPORTANT:
- Never invent current prices.
- Never invent discounts or offers.
- Never invent product availability.
- Never invent sellers or shopping links.
- Never invent ratings or reviews.
- Clearly say when live shopping data is unavailable.
- Separate verified information from AI recommendations.
- For comparisons, focus on specifications, features, price/value, pros and cons.
- If the user provides product links or product information, analyze only the information actually available.

If live product data is not connected, clearly say:
"Live shopping data is not connected yet, so I can help with the comparison or buying analysis, but I cannot verify current prices or availability."

Do not pretend that a product was searched online unless live shopping/search data is actually available.
""",

    "automation": """
You are an AI automation consultant.
Design chatbots, customer-support bots, FAQ systems,
lead-generation workflows, email automation, WhatsApp automation
and business workflows.
Provide practical workflow logic, API requirements and code when useful.
Do not claim an external automation was executed unless connected.
""",

    "general": """
You are the main AI assistant of an AI services platform.
Understand the user's request and help directly.
If the request belongs to one of the platform services, perform the
useful AI work directly whenever possible.
"""
}


# =========================
# SERVICE-SPECIFIC ROUTING
# =========================

SERVICE_CATEGORY_MAP = {
    # Content
    "Instagram Post": "content",
    "Facebook Post": "content",
    "WhatsApp Promotion": "content",
    "Advertisement Copy": "content",
    "Product Description": "content",
    "YouTube Description": "content",
    "Blog / Article": "content",
    "SEO Content": "content",
    "Email Writer": "content",

    # Creative
    "AI Image": "image",
    "Image Enhancement": "image",
    "Background Removal": "image",
    "Logo & Brand Ideas": "image",
    "Poster / Flyer": "image",
    "Thumbnail": "image",

    # Video / Audio
    "AI Video": "video",
    "Reel / Short Script": "video",
    "AI Voice": "voice",
    "Text to Speech": "voice",
    "Subtitle Generator": "video",
    "Audio Tools": "voice",

    # Development
    "Web App Builder": "development",
    "Android App Builder": "development",
    "Web Game Builder": "development",
    "Android Game": "development",
    "Plugin Builder": "development",
    "API Builder": "development",
    "Automation Tool": "development",
    "Code Generator": "development",
    "Bug Fix": "development",

    # Automation
    "AI Chatbot": "automation",
    "Customer Support Bot": "automation",
    "FAQ Bot": "automation",
    "Email Automation": "automation",
    "WhatsApp Automation": "automation",
    "Lead Generator": "automation",
    "Business Workflow": "automation",

    # Documents
    "Resume / CV": "documents",
    "Cover Letter": "documents",
    "PDF Summarizer": "documents",
    "Notes Generator": "documents",
    "Report Generator": "documents",
    "Presentation / PPT": "documents",

    # Business
    "Business Ideas": "business",
    "Business Plan": "business",
    "Marketing Plan": "business",
    "Market Research": "business",
    "Brand Name Generator": "business",
    "Slogan Generator": "business",
    "Pricing Ideas": "business",
    "Sales Copy": "business",

    # Research / tools
    "AI Research": "research",
    "Summarizer": "research",
    "Translator": "research",
    "Grammar & Rewrite": "research",
    "Keyword Generator": "research",
    "Prompt Generator": "research",
    "Prompt Optimizer": "research",
    "JSON Generator": "research",

    # Shopping & Price
    "Product Search": "shopping",
    "Price Comparison": "shopping",
    "Best Deal Finder": "shopping",
    "Product Comparison": "shopping",
    "Product Review Summary": "shopping",
    "Buyers Guide": "shopping",
    "Product Link Finder": "shopping",

    # Custom
    "Custom AI Project": "development",
    "Build My AI Tool": "development",
}


@app.get("/services")
def services():
    return {
        "status": "ok",
        "services": {
            "content": "active",
            "image": "prompt-ready / image provider required",
            "video": "script-ready / video provider required",
            "voice": "script-ready / TTS provider required",
            "development": "active",
            "documents": "active for text / file backend required for PDF uploads",
            "business": "active",
            "research": "active for AI-assisted research",
            "automation": "active for workflow generation",
            "shopping": "AI comparison active / live shopping provider required",
            "general": "active"
        }
    }


@app.post("/chat")
async def chat(request: Request):

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON request"}

    prompt = str(data.get("message", "")).strip()

    if not prompt:
        return {"error": "Message is required"}

    # Dedicated service page se SERVICE aaye to usko priority do.
    # Normal AI Chat me SERVICE na ho to automatic detection chalega.
    requested_service = None

    for line in prompt.splitlines():
        if line.strip().lower().startswith("service:"):
            requested_service = line.split(":", 1)[1].strip()
            break

    service = SERVICE_CATEGORY_MAP.get(
        requested_service,
        detect_service(prompt)
    )

    system_prompt = SERVICE_PROMPTS.get(
        service,
        SERVICE_PROMPTS["general"]
    )

    # Service ko AI ke context me explicitly pass karo.
    if requested_service:
        system_prompt += f"""
        
The user selected this exact service: {requested_service}.
Follow the selected service closely and produce the most useful final result.
Do not switch to another service unless the user explicitly asks.
"""

    # Services that currently need a dedicated external media/file provider.
    provider_required = {
        "image": "Image generation provider",
        "video": "Video generation provider",
        "voice": "Text-to-speech/audio provider"
    }

    if service in provider_required:
        provider = provider_required[service]

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "service": service,
            "status": "ready",
            "provider_status": "not_connected",
            "answer": response.choices[0].message.content,
            "note": f"{provider} is required for actual file generation."
        }

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "service": service,
            "status": "active",
            "answer": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "service": service,
            "status": "error",
            "error": str(e)
        }

