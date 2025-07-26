💸 noex-bot — AI Chatbot That Talks Like Les Gold
"I'm Les Gold. I don't just talk — I close deals. And this bot? It talks like me!"

noex-bot is an AI-powered, voice-interactive chatbot that mimics the personality and voice of Les Gold from Hardcore Pawn. Using voice cloning, real-time speech recognition, and AI-generated responses, it gives you an animated, entertaining conversation experience — complete with a moving mouth.

[![Watch the demo](https://img.youtube.com/vi/i2vuju0tkIg/0.jpg)](https://www.youtube.com/watch?v=i2vuju0tkIg)

🚀 Features
🧠 AI Chatting – Generates smart, witty responses using OpenAI's API.

🗣️ Voice Cloning – Uses F5 TTS with a fine-tuned Orkhon-TTS model to mimic Les Gold’s voice.

🧏 Speech Recognition – Captures your voice via Google Cloud Speech-to-Text.

👄 Mouth Animation – Pygame UI opens and closes the mouth while speaking.

🎤 Fully Voice-Driven – You speak, the bot listens and responds — no typing needed.


F5 TTS with a fine-tuned Orkhon TTS model
(refer to the F5 TTS GitHub page for model setup) : https://github.com/SWivid/F5-TTS

Google Cloud credentials JSON for speech recognition

2. API Keys
Create a .env file with the following:

OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

🎬 Running the Bot
python start_conversation.py

The bot listens, thinks (via OpenAI), and replies in Les Gold’s voice.

Watch its mouth move as it talks.

🧩 Project Structure
noex-bot/
├── assets/                # Visuals for Pygame animation
├── models/                # Orkhon TTS model files
├── speech/                # Google Cloud STT integration
├── tts/                   # F5-TTS inference code
├── ui/                    # Pygame mouth animation
├── noex_bot.py            # Main entry point
└── README.md              # This file
🧠 Technologies Used
OpenAI GPT (chat/completions)

Google Cloud Speech-to-Text

F5-TTS (Orkhon TTS fine-tuned)

Pygame for visual interaction

@article{chen-etal-2024-f5tts,
  title={F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching}, 
  author={Yushen Chen and Zhikang Niu and Ziyang Ma and Keqi Deng and Chunhui Wang and Jian Zhao and Kai Yu and Xie Chen},
  journal={arXiv preprint arXiv:2410.06885},
  year={2024},
}

@misc{orkhon-tts,
  author = {Orkhon TTS Contributors},
  title = {Orkhon-TTS: Mongolic and Turkic multilingual TTS models},
  howpublished = {\url{https://github.com/talshaparov/orkhon-tts}},
  year = {2023},
}
