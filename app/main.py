from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Matter, Person, ReplyHistory
from .schemas import GenerateReplyRequest, SaveReplyRequest
from .services import build_prompt, generate_replies_with_openai, get_memory_context, load_profile_context

load_dotenv()

app = FastAPI(title="Work Communication Copilot MVP")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    people = db.scalars(select(Person).order_by(Person.name)).all()
    matters = db.scalars(select(Matter).order_by(Matter.title)).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "people": people,
            "matters": matters,
            "modifiers": ["more formal", "shorter", "more tactful", "more assertive"],
        },
    )


@app.post("/generate_reply")
def generate_reply(payload: GenerateReplyRequest, db: Session = Depends(get_db)):
    matter = db.get(Matter, payload.matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    if matter.person_id != payload.person_id:
        raise HTTPException(status_code=400, detail="Person and matter do not match")

    memory_context = get_memory_context(db, payload.person_id, payload.matter_id)
    profile_context = load_profile_context()
    prompt = build_prompt(
        incoming_message=payload.incoming_message,
        communication_goal=payload.communication_goal,
        matter=matter,
        memory_context=memory_context,
        profile_context=profile_context,
        modifiers=payload.modifiers,
    )

    try:
        replies = generate_replies_with_openai(prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成失败: {exc}") from exc

    return JSONResponse({**replies, "memory_context": memory_context})


@app.post("/save_reply")
def save_reply(payload: SaveReplyRequest, db: Session = Depends(get_db)):
    history = ReplyHistory(
        person_id=payload.person_id,
        matter_id=payload.matter_id,
        incoming_message=payload.incoming_message,
        communication_goal=payload.communication_goal,
        tone_modifiers=",".join(payload.modifiers),
        generated_prudent=payload.prudent,
        generated_concise=payload.concise,
        generated_push_forward=payload.push_forward,
        selected_reply=payload.selected_reply,
    )
    db.add(history)
    db.commit()
    return {"status": "ok", "history_id": history.id}
