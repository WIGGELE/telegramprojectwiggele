import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
import yt_dlp

# --- КОНФИГУРАЦИЯ ---
TOKEN = '8409669775:AAF6pU3i-I1rs5I-LvfQpfFdcCHticHfk20'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройка логов, чтобы видеть ошибки
logging.basicConfig(level=logging.INFO)

# --- ФУНКЦИИ ЗАГРУЗКИ ---

# Функция для скачивания видео
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Лучшее качество в mp4
        'outtmpl': 'downloads/%(id)s.%(ext)s', # Куда сохранять
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# Функция для поиска и скачивания аудио
def download_audio_search(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'default_search': 'ytsearch1', # Искать 1 лучший результат
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Мы добавляем префикс ytsearch: к запросу
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        # Так как это поиск, info['entries'] содержит список результатов
        if 'entries' in info:
            info = info['entries'][0]
        
        # Получаем имя файла (с расширением mp3 после конвертации)
        filename = f"downloads/{info['title']}.mp3" 
        return filename

# --- ОБРАБОТЧИКИ (HANDLERS) ---

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет! 👋\n1. Отправь мне ссылку на видео (YouTube, TikTok, Shorts), и я скачаю его.\n2. Напиши 'найди песню [название]', чтобы скачать музыку.")

# Обработка поиска музыки
@dp.message(F.text.lower().startswith("найди песню"))
async def search_music(message: types.Message):
    query = message.text[11:].strip() # Отрезаем "найди песню "
    if not query:
        await message.answer("Пожалуйста, напиши название песни после команды.")
        return

    status_msg = await message.answer(f"🔍 Ищу и скачиваю: {query}...")
    
    try:
        # Запускаем блокирующую функцию скачивания в отдельном потоке
        file_path = await asyncio.to_thread(download_audio_search, query)
        
        audio = FSInputFile(file_path)
        await message.answer_audio(audio, caption=f"🎧 Вот твой трек: {query}")
        
        # Удаляем файл после отправки, чтобы не засорять диск
        os.remove(file_path)
        await status_msg.delete()
        
    except Exception as e:
        await message.answer(f"Ошибка при поиске: {e}")

# Обработка ссылок (видео)
@dp.message(F.text.regexp(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'))
async def download_link(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ Скачиваю видео...")

    try:
        file_path = await asyncio.to_thread(download_video, url)
        
        video = FSInputFile(file_path)
        await message.answer_video(video, caption="🎥 Готово!")
        
        os.remove(file_path) # Удаляем файл
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Не удалось скачать. Возможно, видео слишком длинное или приватное.\nОшибка: {str(e)}")

# --- ЗАПУСК ---
async def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())