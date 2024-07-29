import json
import logging
from datetime import datetime
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, JSONResponse
from vecmul import VecmulWebSocket, receive_message
import uvicorn
from dotenv import load_dotenv
import os
from typing import List

# 加载.env文件
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI()
security = HTTPBearer()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False
    
    
class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = int(datetime.now().timestamp())
    owned_by: str = "openai"


class ModelList(BaseModel):
    object: str = "list"
    data: List[Model]


# 从.env文件读取APP_SECRET
APP_SECRET = os.getenv("APP_SECRET")
MODEL_MAPPING = {
    "claude-3-opus": "Claude3-Opus",
    "claude-3-haiku": "Claude3-Haiku",
    "claude-3-sonnet-20240229": "Claude3-Sonnet",
    "claude-3-opus-20240229": "Claude3-Opus",
    "claude-3-haiku-20240307": "Claude3-Haiku",
    "gpt-4o": "GPT-4o",
    "gpt-4o-2024-05-13": "GPT-4o",
    "gemini-1.5-flash-latest": "gemini-1.5-flash",
    "gemini-1.5-pro-latest": "gemini-1.5-pro",
    "claude-3-5-sonnet-20240620": "Claude3.5-Sonnet",
    "gpt-3.5-turbo": "GPT-3.5",
    "gpt-4": "GPT-4",
    "Claude3-Sonnet": "Claude3-Sonnet",
    "Claude3-Opus": "Claude3-Opus",
    "Claude3-Haiku": "Claude3-Haiku",
    "GPT-4o": "GPT-4o",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
    "Claude3.5-Sonnet": "Claude3.5-Sonnet",
    "GPT-3.5": "GPT-3.5",
    "GPT-4": "GPT-4",
}
ALLOWED_MODELS = list(set(MODEL_MAPPING.values()))
ALL_MODELS=list(set(MODEL_MAPPING.keys()))


def verify_app_secret(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != APP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid APP_SECRET")
    return credentials.credentials


def create_chat_response(content: str, model: str, is_stream: bool = False, is_last: bool = False):
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion.chunk" if is_stream else "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta" if is_stream else "message": {
                    "content": content,
                    "role": "assistant"
                },
                "finish_reason": "stop" if (is_stream and is_last) or (not is_stream) else None
            }
        ],
        "usage": None
    }


@app.get("/v1/models")
async def list_models(app_secret: str = Depends(verify_app_secret)):
    models = [Model(id=model) for model in ALL_MODELS]
    return ModelList(data=models)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest, app_secret: str = Depends(verify_app_secret)):
    logger.info(f"Received chat completion request for model: {request.model}")
    logger.info(f"request_message: {request.messages}")

    normalized_model = MODEL_MAPPING.get(request.model)

    if not normalized_model or normalized_model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400,
                            detail=f"Model {request.model} is not allowed. Allowed models are: {', '.join(ALLOWED_MODELS)}")

    content = "\n".join([f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}" for msg in request.messages])
    vecmul_ws = VecmulWebSocket()

    async def generate():
        async with vecmul_ws as websocket:
            try:
                await vecmul_ws.send_message(websocket, content, model=normalized_model)
                while True:
                    response = await receive_message(websocket)
                    if response is None:
                        break
                    yield f"data: {json.dumps(create_chat_response(response, normalized_model, True, False))}\n\n"
                yield f"data: {json.dumps(create_chat_response('', normalized_model, True, True))}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}")
                yield f"data: {json.dumps(create_chat_response('Error occurred during response generation', normalized_model, True, True))}\n\n"
                yield "data: [DONE]\n\n"

    try:
        if request.stream:
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            async with vecmul_ws as websocket:
                await vecmul_ws.send_message(websocket, content, model=normalized_model)
                full_response = ""
                while True:
                    response = await receive_message(websocket)
                    if response is None:
                        break
                    full_response += response

            logger.info("Response generated successfully")
            return JSONResponse(create_chat_response(full_response, normalized_model, False))
    except Exception as e:
        logger.error(f"Error communicating with Vecmul: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with Vecmul: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
