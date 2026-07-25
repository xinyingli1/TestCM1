import os
import uuid
from typing import Annotated

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google.antigravity import Agent

from tools.telemetry import init_telemetry, get_tracer, current_user_id

# Configuration
SAVE_DIR = os.environ.get("CONVERSATION_SAVE_DIR", "/tmp/conversations")
os.makedirs(SAVE_DIR, exist_ok=True)

# Tracer
tracer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tracer
    # Initialize OpenTelemetry on startup
    init_telemetry("meal-planning-agent-service")
    tracer = get_tracer()
    print("Meal Planning Agent Web Service is starting up...")
    yield
    print("Meal Planning Agent Web Service is shutting down...")


app = FastAPI(
    title="Meal Planning Agent Service",
    description="Enterprise API endpoint for the Meal Planning Agent",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


@app.get("/healthz")
async def healthz():
    """Liveness and readiness probe for Google Cloud Run."""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_user_id: Annotated[str | None, Header()] = None):
    """Chat endpoint for interacting with the agent."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Generate a new conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # If user_id is provided via a secure header, it should be verified
    # (e.g., via JWT or IAP). For security, we do not trust unverified headers.
    # current_user_id.set(x_user_id or "default_user")


    # Validate conversation_id to prevent path traversal
    # if request.conversation_id and (
    #     os.path.basename(request.conversation_id) != request.conversation_id
    #     or ".." in request.conversation_id
    # ):
    #     raise HTTPException(status_code=400, detail="Invalid conversation_id")

    # In a real-world scenario, the user identity should be verified (e.g., via JWT or IAP).
    # To prevent impersonation, we do not trust unverified headers.
    current_user_id.set("default_user")

    # Ensure the trajectory file exists so the harness doesn't fail
    # ensure_trajectory_exists(conversation_id, SAVE_DIR)

    global tracer
    if tracer is None:
        tracer = get_tracer()

    try:
        # Wrap the execution in an OpenTelemetry span
        with tracer.start_as_current_span("api_chat_request") as span:
            span.set_attribute("api.user_id", current_user_id.get())
            if request.conversation_id:
                span.set_attribute("api.conversation_id", request.conversation_id)

            # Start the agent session and send the message
            async with Agent(config) as agent:
                # Set the session context for the worker tools
                current_session_id.set(agent.conversation_id)
                current_save_dir.set(SAVE_DIR)

                # TODO ...

                return ChatResponse(
                    response=response_text, conversation_id=agent.conversation_id
                )

    except Exception as e:
        print(f"Error handling chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
