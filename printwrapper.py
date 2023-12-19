from fastapi import WebSocket
from vocode.streaming.models.websocket import (
  AudioConfigStartMessage,
  AudioMessage,
  ReadyMessage,
  WebSocketMessage,
  WebSocketMessageType,
)
from vocode.streaming.output_device.websocket_output_device import WebsocketOutputDevice
from vocode.streaming.client_backend.conversation import ConversationRouter
from vocode.streaming.models.message import BaseMessage
import typing
from vocode.streaming.agent.utils import format_openai_chat_messages_from_transcript
import requests
import json
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent


class PrintWrapper(ConversationRouter):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  # def print_message(self, direction: str, content: str):
  #     print(f"Message Direction: {direction}")
  #     print(f"Message Content: {content}")
  #     print("-----------------------------------")

  async def conversation(self, websocket: WebSocket):
    await websocket.accept()
    # agent_id=await websocket.receive_json()
    #do agent_id stuff
    start_message: AudioConfigStartMessage = AudioConfigStartMessage.parse_obj(
      await websocket.receive_json())
    a = json.loads(start_message.conversation_id)
    # agent_user_json=json.loads(start_message.conversation_id)
    # define the agent here. Vocode 0.1.10 takes a full agent and not just the thunk.
    # print(a)
    agent_id = a["agent_id"]
    user_id = a["user_id"]
    # fetch agent information from the agent_id
    # self.agent=
    fetch_url = "endpoint"
    # params={"user_id":user_id,"agent_id":agent_id}
    params = {"user_id": user_id, "agent_id": agent_id}
    response = requests.get(fetch_url, params=params)
    response = json.loads(response.text)
    type=response["type"]
    if type=="Sales":
      if personality=="executive":
        self.agent = ChatGPTAgent(
          ChatGPTAgentConfig(
            initial_message=BaseMessage(text="XYZ"),
            track_bot_sentiment=True,
            end_conversation_on_goodbye=True,
            prompt_preamble=
            f"""Prompt_ex2"""))
      else:
        self.agent = ChatGPTAgent(
          ChatGPTAgentConfig(
            initial_message=BaseMessage(text="XYZ"),
            track_bot_sentiment=True,
            end_conversation_on_goodbye=True,
            prompt_preamble=
            f"""prompt_ex3"""))
    else:
      if personality=="polite":
        self.agent=ChatGPTAgent(
          ChatGPTAgentConfig(
          initial_message=BaseMessage(text="XYZ"),
          track_bot_sentiment=True,
          end_conversation_on_goodbye=True,
          prompt_preamble=f"""Ex3"""))
      if personality=="angry":
        self.agent=ChatGPTAgent(
          ChatGPTAgentConfig(
          initial_message=BaseMessage(text=f"XYZ"),
          track_bot_sentiment=True,
          end_conversation_on_goodbye=True,
          prompt_preamble=f"""prompt_ex5"""))
    # Print the received start_message
    # self.print_message('received', start_message.json())

    # Continue with the original behavior
    output_device = WebsocketOutputDevice(
      websocket,
      start_message.output_audio_config.sampling_rate,
      start_message.output_audio_config.audio_encoding,
    )
    conversation = self.get_conversation(output_device, start_message)
    await conversation.start(lambda: websocket.send_text(ReadyMessage().json())
                             )

    while conversation.is_active():
      message: WebSocketMessage = WebSocketMessage.parse_obj(
        await websocket.receive_json())

      # Print every received WebSocketMessage
      # self.print_message('received', message.json())

      if message.type == WebSocketMessageType.STOP:
        break

      audio_message = typing.cast(AudioMessage, message)
      conversation.receive_audio(audio_message.get_bytes())
    bodmo = format_openai_chat_messages_from_transcript(
      conversation.agent.transcript)
    #append url here to reflect the new api which also accepts user_id
    url = 'endpoint_2'
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    output_device.mark_closed()
    conversation.terminate()
