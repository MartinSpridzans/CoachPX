import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.synthesizer.stream_elements_synthesizer import StreamElementsSynthesizer
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig, StreamElementsSynthesizerConfig
# from fastapi import APIRouter, Depends, HTTPException, WebSocket
# from typing import Callable, Any, Optional
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.client_backend.conversation import ConversationRouter

import typing
from vocode.streaming.models.message import BaseMessage
from fastapi import WebSocket
from vocode.streaming.models.websocket import (
    AudioConfigStartMessage,
    AudioMessage,
    ReadyMessage,
    WebSocketMessage,
    WebSocketMessageType,
)
from vocode.streaming.output_device.websocket_output_device import WebsocketOutputDevice
import os
import uvicorn
from printwrapper import PrintWrapper
app = FastAPI(docs_url=None)
templates = Jinja2Templates(directory="templates")

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


REPLIT_URL = f"{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER')}.repl.co"

STREAM_ELEMENTS_SYNTHESIZER_THUNK = lambda output_audio_config: StreamElementsSynthesizer(
  StreamElementsSynthesizerConfig.from_output_audio_config(output_audio_config)
)
# much more realistic, but slower responses and requires a paid API key
# female
ELEVEN_LABS_SYNTHESIZER_THUNK = lambda output_audio_config: ElevenLabsSynthesizer(
  ElevenLabsSynthesizerConfig.from_output_audio_config(
    output_audio_config,
    api_key=os.getenv("ELEVEN_LABS_API_KEY"),
    voice_id="#####",
    stability=0.00,
    similarity_boost=0.00,
  ))


@app.get("/")
async def root(request: Request):
  env_vars = {
    "REPLIT_URL": REPLIT_URL,
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "DEEPGRAM_API_KEY": os.environ.get("DEEPGRAM_API_KEY"),
    "ELEVEN_LABS_API_KEY": os.environ.get("ELEVEN_LABS_API_KEY"),
  }

  return templates.TemplateResponse("index.html", {
    "request": request,
    "env_vars": env_vars
  })


print_router = PrintWrapper(
  agent=ChatGPTAgent(
    ChatGPTAgentConfig(
      initial_message=BaseMessage(text="Hello!"),
      prompt_preamble=f"""prompt_ex1""",
      send_filler_audio=False
    )),
  synthesizer_thunk=STREAM_ELEMENTS_SYNTHESIZER_THUNK,
  synthesizer_thunk=ELEVEN_LABS_SYNTHESIZER_THUNK,
  logger=logger
)
app.include_router(conversation_router.get_router())
app.include_router(print_router.get_router())

uvicorn.run(app, host="0.0.0.0", port=3000)
