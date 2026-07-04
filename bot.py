import os
import requests
import telebot
from yt_dlp import YoutubeDL

TOKEN = "6199150269:AAEERF7ApDgqeoTz5no25iIHoQA4tjgloqQ"
bot = telebot.TeleBot(TOKEN, threaded=True)

RAPIDAPI_KEY = "d78b9c0a1dmshfcaa8a1dc14a878p1f0534jsn7e22ff8d255d"
RAPIDAPI_HOST = "shazam-api-free.p.rapidapi.com"

def identify_music(file_path):
    url = "https://shazam-api-free.p.rapidapi.com/shazam/recognize/"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}
    with open(file_path, 'rb') as f:
        files = {'upload_file': f}
        response = requests.post(url, files=files, headers=headers, timeout=20).json()
    return response.get('track')

@bot.message_handler(content_types=['voice', 'video', 'audio'])
def handle_media(message):
    chat_id = message.chat.id
    status = bot.reply_to(message, "🎧 Fayl tahlil qilinmoqda, musiqa qidirilyapti... ⏳")
    try:
        file_id = message.voice.file_id if message.voice else (message.video.file_id if message.video else message.audio.file_id)
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_file = "temp_media.mp3"
        with open(temp_file, 'wb') as f: f.write(downloaded_file)
        track = identify_music(temp_file)
        if os.path.exists(temp_file): os.remove(temp_file)
        if track:
            title = f"{track.get('subtitle', '')} - {track.get('title', '')}"
            bot.edit_message_text(f"🔍 Topildi: *{title}*\nYuklab beryapman... 🎵", chat_id, status.message_id, parse_mode="Markdown")
            download_and_send_music(chat_id, title, status.message_id)
        else:
            bot.edit_message_text("Kechirasiz, bu fayldan musiqa topa olmadim. 😕", chat_id, status.message_id)
    except Exception as e:
        try: bot.edit_message_text(f"Xatolik: {str(e)}", chat_id, status.message_id)
        except: pass

def download_and_send_music(chat_id, query, status_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'musiqa.mp3',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info['entries'][0]['title'] if 'entries' in info else info.get('title', 'Musiqa')
        with open('musiqa.mp3', 'rb') as audio:
            bot.send_audio(chat_id, audio, caption=f"🎵 {title}\n\nMuvaffaqiyatli topildi! 🌟", timeout=60)
        if os.path.exists('musiqa.mp3'): os.remove('musiqa.mp3')
        try: bot.delete_message(chat_id, status_id)
        except: pass
    except Exception:
        if os.path.exists('musiqa.mp3'): os.remove('musiqa.mp3')

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    status = bot.reply_to(message, f"🔍 '{message.text}' qidirilmoqda...")
    download_and_send_music(message.chat.id, message.text, status.message_id)

print("Serverda bot ishga tushdi...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
