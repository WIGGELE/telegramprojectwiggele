import yt_dlp
import os
from aiogram import Bot, Dispatcher, types, executor
from youtubesearchpython import VideosSearch

TOKEN = "6378040699:AAESbisI818kPjSb5ttOCQzgyw-tcFqKEys"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== Видео по ссылке =====
@dp.message_handler(lambda m: m.text.startswith("http"))
async def download_video(message: types.Message):
    url = message.text
    file = "video.mp4"

    ydl_opts = {
        'outtmpl': file,
        'format': 'mp4/best',
    }

    try:
        await message.reply("⏳ Загружаю видео...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await message.reply_document(open(file, "rb"))
    except Exception as e:
        await message.reply("⚠ Ошибка при загрузке")
        print(e)
    finally:
        if os.path.exists(file):
            os.remove(file)

# ===== Поиск песни =====
@dp.message_handler(lambda m: m.text.lower().startswith("найди песню"))
async def find_song(message: types.Message):
    text = message.text[11:].strip().replace('"', '')
    search = VideosSearch(text + " audio", limit=1)
    video = search.result()["result"][0]
    url = video["link"]

    file = "music.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        await message.reply("🎧 Ищу и загружаю песню...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await message.reply_audio(open(file, "rb"), caption=f"Нашёл 🎶 {text}")
    except Exception as e:
        await message.reply("⚠ Не удалось найти песню")
        print(e)
    finally:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    executor.start_polling(dp)
