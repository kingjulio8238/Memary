from openai import OpenAI
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("openai_api_key")

client = OpenAI()
      
def call_gpt_model(prompt, data, model, temperature=None):
  messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": data}
  ]

  api_params = {
      "model": model,
      "messages": messages
  }

  if temperature is not None:
    api_params["temperature"] = temperature

  try:
    response = client.chat.completions.create(**api_params)
    response_content = response.choices[0].message.content.strip()

    return response_content

  except Exception as e:
    raise RuntimeError(f"An error occurred while making an API call: {e}")
  
def call_gpt_vision(base64_image, user): 
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
  }
  
  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "system", 
        "content": "You are tasked with answering a blind individual's question about their current environment. Aim for brevity without sacrificing the immersive experience."
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": user
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }
  
  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  
  return response.json()['choices'][0]['message']['content']

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')  

def text_to_speech(text, filepath):   
  try: 
    response = client.audio.speech.create(
      model="tts-1",
      voice="shimmer",
      input=text
    )
    response.stream_to_file(filepath)
    
  except Exception as e: 
    raise RuntimeError(f"An unexpected error occurred: {str(e)}")
    
def speech_to_text(filepath):
  try: 
    audio_file = open(filepath, "rb")
    transcript = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file, 
      prompt="The transcript is about a blind person asking about their environment",
      response_format="text"
    )
  except Exception as e: 
    return f"An unexpected error occurred: {str(e)}"