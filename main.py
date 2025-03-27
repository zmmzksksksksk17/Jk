import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext
import yt_dlp

# Bot configuration
BOT_TOKEN = "7516781828:AAFWWfcB-u5LZpZmBGjtAm_XWgK4YkRYTng"
ADMIN_ID = 7439517139
DOWNLOAD_DIR = 'downloads'

# Headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Ensure download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Validate YouTube URL
def is_youtube_url_valid(url):
    try:
        response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

# Download the YouTube video
async def download_youtube_video(url):
    filename = None
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
        'retries': 5,
        'user_agent': HEADERS["User-Agent"],
        'geo_bypass': True,
        'ffmpeg_location': 'ffmpeg'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

# Handle messages with a URL
async def handle_url(update: Update, context: CallbackContext):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Invalid YouTube URL.")
        return

    if not is_youtube_url_valid(url):
        await update.message.reply_text("That link seems broken or blocked. Try another.")
        return

    await update.message.reply_text("Downloading... please wait.")

    try:
        video_path = await download_youtube_video(url)
        await update.message.reply_video(video=open(video_path, 'rb'))
        os.remove(video_path)
    except Exception as e:
        await update.message.reply_text(f"Download failed: {str(e)}")

# Admin commands
async def handle_admin_commands(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You’re not authorized to use admin commands.")
        return

    command = update.message.text.lower()

    if command == "/status":
        await update.message.reply_text("Bot is running smoothly.")
    elif command == "/stop":
        await update.message.reply_text("Stopping the bot...")
        await context.bot.stop()
    else:
        await update.message.reply_text("Unknown admin command.")

# Main bot function (automatic event loop management by Application)
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_admin_commands))
    await app.run_polling()

if __name__ == '__main__':
    # Let the application manage the event loop itself
    import asyncio
    asyncio.run(main())
