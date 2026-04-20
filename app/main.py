from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .schemas import GenerateReplyRequest
from .services import build_prompt, generate_reply_with_openai

load_dotenv()

app = FastAPI(title="工作沟通辅助网页工具 V1.0")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate_reply")
def generate_reply(payload: GenerateReplyRequest):
    prompt = build_prompt(
        incoming_message=payload.incoming_message,
        communication_background=payload.communication_background,
        reference_material=payload.reference_material,
        my_intent=payload.my_intent,
    )

    try:
        draft_reply = generate_reply_with_openai(prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成失败: {exc}") from exc

    return JSONResponse({"draft_reply": draft_reply})
