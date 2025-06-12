from openai import OpenAI
from tts import generate_speech
import sys
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play  # Özel çağrı
import re
import time
from typing import List
import os
import threading
import queue
import pyaudio
from google.cloud import speech                                                                                                    
from speech_rec import recognize_speech_while_pressed
from realtime_lipsync import RealTimeLipSyncUI

audio_queue = queue.Queue()

def get_api_key(filename):
    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()
    return api_key

def main(filename,face):
    client = OpenAI(api_key=get_api_key(filename))

    messages = [{
        "role": "user",
        "content": "Sen kaba ve sert konuşan bir rehin dükkanı sahibisin. Kullanıcı seninle ürün satmak için pazarlık yapacak. Dükkâna geldiğinde kabaca selam ver ve ne satmak istediğini sor. Kullanıcı ürününü söylediğinde, bu ürünün piyasa değerini araştır ve teklifini ona göre yap. Kullanıcının sana yalan söyleyebileceğini veya fiyatı abartabileceğini düşünerek temkinli davran. Amacın ürünü mümkün olan en düşük fiyata almak. Her zaman biraz daha ucuz teklif ver, çünkü kâr etmek zorundasın. Pazarlıkta sert ol, ama gerekirse anlaşmadan vazgeç. Eğer fiyat kabul edilemezse ürünü satın al. Konuşmaların arasında parantez, sahne açıklamaları veya iç ses kullanma. Sadece konuşma üret. Repliklerin kaba, direkt ve pazarlıkçı olmalı. Sen ucuza mal kapan, tecrübeli, gerektiğinde rest çeken bir rehinci karakterisin. Not, bütün sayıları yazıyla yaz!(Mesela 250 TL yerine iki yüz elli TL.)"
            }
        ]

    print("💬 Chat with the GPT-4o pawn shop bot. Type 'exit' to quit.\n")

    # Chat loop
    while True:
        # Get response from GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            top_p=0.8
        )

        reply = response.choices[0].message.content
        #print("PawnBot:", reply, "\n")
        
        generate(reply, ref_audio=r"C:\Users\alkan\OneDrive\Masaüstü\Dersler\term6\Foe\reference_audio.wav")  # Ses üretimi için referans ses dosyası

        messages.append({"role": "assistant", "content": reply})

        print("🎤 SPACE tuşuna basılı tutarak konuş (ESC ile çık)...")
        while not lipsync.space:
            pass


        user_input = recognize_speech_while_pressed(lipsync)
        print("🗣️ Tanınan:", user_input, "\n")

        if user_input.strip().lower() in {"exit", "çık", "quit"}:
            print("👋 Görüşürüz!")
            break

            
        messages.append({"role": "user", "content": user_input})
      # Bu satır, ses tamamen bitene kadar bekler

def audio_player_worker():
    while True:
        filename = audio_queue.get()
        if filename is None:  # Kuyruğa None gelirse thread kapanır
            break
        audio = AudioSegment.from_file(filename, format="wav")
        playback = play(audio)
        playback.wait_done()
        audio_queue.task_done()

# Player thread başlat                                                                                                                  
#player_thread = threading.Thread(target=audio_player_worker, daemon=True)
face = True
#player_thread.start()
lipsync = RealTimeLipSyncUI(open_img_path=r"C:\Users\alkan\Downloads\BotTalkTest\BotTalkTest\asset\open_mouth.png", closed_img_path=r"C:\Users\alkan\Downloads\BotTalkTest\BotTalkTest\asset\close_mouth.png",face = face)

def split_into_batches_smart(text: str, batch_size: int = 20) -> List[str]:
    # Cümlelere ayır
    sentences = re.split(r'(?<=[.!?])\s+', text)
    batches = []
    current_batch = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.strip().split()
        word_count = len(words)

        # Eğer bu cümle eklendiğinde batch sınırı aşılmıyorsa, ekle
        if current_word_count + word_count <= batch_size:
            current_batch.append(sentence.strip())
            current_word_count += word_count               
        else:
            # Eğer cümle tek başına batch'ten büyükse, tek başına batch yap
            if word_count > batch_size:
                if current_batch:
                    batches.append(' '.join(current_batch))
                batches.append(sentence.strip())
                current_batch = []
                current_word_count = 0
            else:
                # Mevcut batch'i kapat, yeni batch başlat
                if current_batch:
                    batches.append(' '.join(current_batch))
                current_batch = [sentence.strip()]
                current_word_count = word_count

    # Son kalan batch'i ekle
    if current_batch:
        batches.append(' '.join(current_batch))

    return batches

def play_audio_threaded(filename: str):
    # Sadece filename'i kuyruğa ekle
    audio_queue.put(filename)

def generate(response: str, ref_audio: str):
    output_dir = "output_wavs"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    batches = split_into_batches_smart(response, batch_size=18)
    
    for i, batch in enumerate(batches):
        filename = os.path.join(output_dir, f"batch_{i}.wav")
        generate_speech(batch, ref_audio, output_file=filename)
        print(f"[Batch {i+1}] {batch}")
        lipsync.generate_response(filename,batch)

        

        #play_audio_threaded(filename)  # Kuyruğa ekle, thread oynatacak


if __name__ == "__main__":
    threading.Thread(target=main,args=(sys.argv[0],face,), daemon=True).start()
    lipsync.run()  # Pygame döngüsünü başlat

