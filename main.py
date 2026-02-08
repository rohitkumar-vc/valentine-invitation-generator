import os
import sys
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from upstash_redis.asyncio import Redis  # NOTE: Using the Async client
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

# 1. Validation Check: Ensure credentials exist before starting
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not UPSTASH_URL or not UPSTASH_TOKEN:
    print("❌ ERROR: UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN not found in .env file.")
    sys.exit(1)

# 2. Initialize Async Redis
redis = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)

app = FastAPI(name="Valentine Generator", openapi_url=None, docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=".") 

# --- COMMON FOOTER CSS & HTML ---
FOOTER_HTML = """
    <div class="footer">Made with ❤️ by Rohit</div>
"""

FOOTER_CSS = """
    .footer {
        position: fixed;
        bottom: 15px;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: rgba(0, 0, 0, 0.4);
        pointer-events: none;
        font-family: 'Nunito', sans-serif;
        z-index: 999;
    }
"""

# --- HTML TEMPLATES ---
HTML_LANDING = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Create Valentine Invite</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Nunito', sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            background: #ffe6e9; 
            margin: 0;
            padding: 20px;
        }}
        .card {{ 
            background: white; 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
            text-align: center; 
            width: 100%; 
            max-width: 400px;
            position: relative;
            z-index: 10;
        }}
        h1 {{ color: #ff4d6d; margin-bottom: 10px; font-size: 28px; }}
        p {{ color: #666; margin-bottom: 25px; }}
        input {{ 
            width: 100%; 
            padding: 15px; 
            margin-bottom: 20px; 
            border: 2px solid #eee; 
            border-radius: 12px; 
            font-size: 16px; 
            outline: none;
            transition: border-color 0.3s;
        }}
        input:focus {{ border-color: #ff4d6d; }}
        button {{ 
            background: #ff4d6d; 
            color: white; 
            border: none; 
            padding: 15px; 
            font-size: 18px; 
            border-radius: 50px; 
            cursor: pointer; 
            font-weight: bold; 
            width: 100%; 
            transition: transform 0.1s, background 0.2s; 
            -webkit-tap-highlight-color: transparent;
        }}
        button:active {{ transform: scale(0.98); }}
        button:hover {{ background: #e01e45; }}
        
        {FOOTER_CSS}
    </style>
</head>
<body>
    <div class="card">
        <h1>💘 Valentine Generator</h1>
        <p>Who do you want to ask out?</p>
        <form action="/generate" method="post">
            <input type="text" name="name" placeholder="Enter their name (e.g. Rohit)" required autocomplete="off">
            <button type="submit">Create Link ✨</button>
        </form>
    </div>
    {FOOTER_HTML}
</body>
</html>
"""

HTML_VALENTINE_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>For {{{{ name }}}} ❤️</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            display: flex; justify-content: center; align-items: center; min-height: 100vh;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
            margin: 0; font-family: 'Nunito', sans-serif; overflow: hidden; touch-action: none; 
        }}
        .container {{
            text-align: center; background: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 25px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1), 0 5px 15px rgba(0,0,0,0.05);
            width: 90%; max-width: 450px; height: 500px; position: relative; 
            overflow: hidden; display: flex; flex-direction: column; align-items: center;
            justify-content: center; border: 4px solid #fff; z-index: 10;
        }}
        .gif-container img {{
            width: 160px; height: auto; border-radius: 15px; margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); pointer-events: none;
        }}
        h1 {{
            color: #4a4a4a; font-size: 24px; margin: 10px 0 30px 0; font-weight: 700;
            line-height: 1.4; z-index: 5; pointer-events: none;
        }}
        .name-highlight {{
            font-family: 'Pacifico', cursive; color: #ff4d6d; font-size: 32px; font-weight: normal;
        }}
        .btn-group {{
            width: 100%; display: flex; justify-content: center; gap: 15px; margin-top: 10px;
            height: 50px; position: static; z-index: 10;
        }}
        button {{
            padding: 10px 25px; font-size: 16px; border-radius: 50px; cursor: pointer;
            font-weight: 800; font-family: 'Nunito', sans-serif; transition: transform 0.1s ease;
            outline: none; -webkit-tap-highlight-color: transparent;
        }}
        #yesBtn {{
            background-color: #ff4d6d; color: white; border: 3px solid #e01e45;
            box-shadow: 0 4px 10px rgba(255, 77, 109, 0.3); z-index: 20; position: relative;
        }}
        #noBtn {{
            background-color: #f8f9fa; color: #6c757d; border: 3px solid #dee2e6; z-index: 15;
        }}
        .note {{ font-size: 12px; color: #aaa; margin-top: auto; font-style: italic; }}
        .hidden {{ display: none; }}
        .success-message h2 {{
            font-family: 'Pacifico', cursive; color: #ff4d6d; font-size: 36px; margin-bottom: 10px;
        }}
        .success-message p {{ font-size: 18px; color: #555; line-height: 1.5; }}
        .heart {{
            position: absolute; color: #ff4d6d; animation: float 4s ease-in infinite;
            opacity: 0; font-size: 20px; pointer-events: none; z-index: 100;
        }}
        
        {FOOTER_CSS}

        @keyframes float {{
            0% {{ transform: translateY(0) scale(0.5); opacity: 1; }}
            100% {{ transform: translateY(-100vh) scale(1.5); opacity: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container" id="mainCard">
        <div class="gif-container">
            <img src="https://media.tenor.com/dVr8gUFNKLYAAAAi/milk-and-mocha-cute.gif" alt="Cute Bears">
        </div>
        <h1><span class="name-highlight">{{{{ name }}}}</span>,<br>will you be my Valentine?</h1>
        <div class="btn-group">
            <button id="yesBtn">Yes 💛</button>
            <button id="noBtn">No</button>
        </div>
        <p class="note">("No" seems a bit shy 😈)</p>
    </div>
    <div class="container hidden" id="successCard">
        <div class="gif-container">
            <img src="https://media.tenor.com/gUiu1zyxfzYAAAAi/bear-kiss-bear-kisses.gif" alt="Bear Kiss">
        </div>
        <div class="success-message">
            <h2>Yeaaayyy! 🎉</h2>
            <p>I knew you would say yes! <br> Can't wait to see you! ❤️</p>
        </div>
    </div>
    {FOOTER_HTML}
    <script>
        const yesBtn = document.getElementById('yesBtn');
        const noBtn = document.getElementById('noBtn');
        const mainCard = document.getElementById('mainCard');
        const successCard = document.getElementById('successCard');
        const isOverlap = (rect1, rect2) => {{
            return !(rect1.right < rect2.left || rect1.left > rect2.right || rect1.bottom < rect2.top || rect1.top > rect2.bottom);
        }};
        const moveNoButton = (e) => {{
            if(e && e.type === 'touchstart') e.preventDefault();
            noBtn.style.position = 'absolute';
            const cardRect = mainCard.getBoundingClientRect();
            const yesRect = yesBtn.getBoundingClientRect();
            const btnRect = noBtn.getBoundingClientRect();
            const safePadding = 20;
            const maxLeft = cardRect.width - btnRect.width - safePadding;
            const maxTop = cardRect.height - btnRect.height - safePadding;
            let newLeft, newTop;
            let overlap = true;
            let attempts = 0;
            while (overlap && attempts < 50) {{
                newLeft = Math.random() * (maxLeft - safePadding) + safePadding;
                newTop = Math.random() * (maxTop - safePadding) + safePadding;
                const proposedNoRect = {{
                    left: cardRect.left + newLeft, top: cardRect.top + newTop,
                    right: cardRect.left + newLeft + btnRect.width, bottom: cardRect.top + newTop + btnRect.height
                }};
                if (!isOverlap(proposedNoRect, yesRect)) {{ overlap = false; }}
                attempts++;
            }}
            noBtn.style.left = newLeft + 'px';
            noBtn.style.top = newTop + 'px';
        }};
        noBtn.addEventListener('mouseover', moveNoButton);
        noBtn.addEventListener('touchstart', moveNoButton);
        noBtn.addEventListener('click', moveNoButton);
        yesBtn.addEventListener('click', () => {{
            mainCard.classList.add('hidden');
            successCard.classList.remove('hidden');
            createHearts();
        }});
        function createHearts() {{
            const body = document.querySelector('body');
            for (let i = 0; i < 60; i++) {{
                setTimeout(() => {{
                    const heart = document.createElement('div');
                    heart.classList.add('heart');
                    heart.innerHTML = '❤️';
                    heart.style.left = Math.random() * 100 + 'vw';
                    heart.style.top = '100vh';
                    heart.style.fontSize = (Math.random() * 20 + 10) + 'px';
                    heart.style.animationDuration = (Math.random() * 2 + 3) + 's';
                    body.appendChild(heart);
                    setTimeout(() => heart.remove(), 5000);
                }}, i * 60);
            }}
        }}
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.get("/make-invitation", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=HTML_LANDING, status_code=200)

@app.post("/generate", response_class=HTMLResponse)
async def generate_link(request: Request, name: str = Form(...)):
    # 1. Atomic INCR using await
    next_id = await redis.incr("valentine_counter")
    str_id = str(next_id)
    
    # 2. Set value using await
    await redis.set(f"invite:{str_id}", name)
    
    base_url = str(request.base_url).rstrip("/")
    generated_link = f"{base_url}/ask/{str_id}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Link Created!</title>
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: 'Nunito', sans-serif; 
                display: flex; flex-direction: column; align-items: center; justify-content: center; 
                min-height: 100vh; background: #e0ffe4; margin: 0; padding: 20px;
            }}
            .card {{ 
                background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
                width: 100%; max-width: 400px; text-align: center; z-index: 10;
            }}
            h1 {{ color: #2ecc71; margin-top: 0; font-size: 26px; }}
            .link-box {{
                background: #f8f9fa; border: 2px solid #e9ecef; padding: 12px; border-radius: 10px;
                word-break: break-all; font-family: monospace; color: #333; margin: 15px 0; font-size: 14px;
            }}
            .btn {{
                display: block; width: 100%; padding: 12px; margin-top: 10px; border-radius: 50px;
                text-decoration: none; font-weight: bold; text-align: center; cursor: pointer;
                transition: 0.2s; border: none; font-size: 16px;
            }}
            .btn-copy {{ background: #2ecc71; color: white; }}
            .btn-open {{ background: #fff; border: 2px solid #2ecc71; color: #2ecc71; }}
            .btn-back {{ background: #e9ecef; color: #666; margin-top: 20px; }}
            #toast {{
                visibility: hidden; min-width: 200px; background-color: #333; color: #fff;
                text-align: center; border-radius: 50px; padding: 10px; position: fixed; z-index: 1000;
                bottom: 50px; font-size: 14px;
            }}
            #toast.show {{ visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }}
            {FOOTER_CSS}
            @keyframes fadein {{ from {{bottom: 20px; opacity: 0;}} to {{bottom: 50px; opacity: 1;}} }}
            @keyframes fadeout {{ from {{bottom: 50px; opacity: 1;}} to {{bottom: 20px; opacity: 0;}} }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Link Ready! ✅</h1>
            <p>Share this link with <strong>{name}</strong>:</p>
            <div class="link-box" id="linkText">{generated_link}</div>
            <button class="btn btn-copy" onclick="copyLink()">📋 Copy Link</button>
            <a href="{generated_link}" class="btn btn-open">Open Link ↗️</a>
            <a href="/make-invitation" class="btn btn-back">Create Another</a>
        </div>
        {FOOTER_HTML}
        <div id="toast">Link copied to clipboard!</div>
        <script>
            function copyLink() {{
                const linkText = document.getElementById("linkText").innerText;
                navigator.clipboard.writeText(linkText).then(() => {{ showToast(); }})
                .catch(err => {{ alert("Manual copy required: " + linkText); }});
            }}
            function showToast() {{
                const x = document.getElementById("toast");
                x.className = "show";
                setTimeout(function(){{ x.className = x.className.replace("show", ""); }}, 3000);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/ask/{unique_id}", response_class=HTMLResponse)
async def ask_page(request: Request, unique_id: str):
    # Retrieve using await
    name = await redis.get(f"invite:{unique_id}")
    
    if not name:
        raise HTTPException(status_code=404, detail="Invitation not found. Please check the ID.")
    
    template = templates.env.from_string(HTML_VALENTINE_TEMPLATE)
    return template.render(name=name)

@app.get("/check-all-invitation")
async def check_all_invitations():
    # 1. Fetch all keys matching pattern
    keys = await redis.keys("invite:*")
    
    if not keys:
        return {}
    
    # 2. Optimization: Use MGET to fetch all values in one network call
    # keys are ['invite:1', 'invite:2'], we pass them directly to mget
    values = await redis.mget(keys)
    
    results = {}
    for key, value in zip(keys, values):
        # Extract ID from "invite:123" -> "123"
        clean_id = key.replace("invite:", "")
        results[clean_id] = value
        
    return results

@app.get("/health")
async def health_check():
    try:
        await redis.ping()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
