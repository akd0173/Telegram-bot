import logging
import random
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder

# --- Configuration ---
# Sets up basic logging to see when the bot sends videos
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Data ---
# Load the list of video File IDs from the JSON file created earlier
VIDEO_IDS = []
try:
    with open('video_ids.json', 'r') as f:
        VIDEO_IDS = json.load(f)
    logger.info(f"Loaded {len(VIDEO_IDS)} video File IDs.")
except FileNotFoundError:
    logger.error("video_ids.json not found! Bot will not be able to send videos.")

# --- Bot Commands ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcoming message with instructions."""
    await update.message.reply_text(
        'Welcome! I am your random video bot. Click /video to get a random video!',
    )

async def send_random_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a random video using a stored File ID."""
    if not VIDEO_IDS:
        await update.message.reply_text("Sorry, no video IDs found. Please upload videos first.")
        return

    # Pick a random File ID from the list
    random_id = random.choice(VIDEO_IDS)
    
    # Send the video using the File ID (Telegram handles the rest for free)
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=random_id,
        caption="Enjoy this random video from the cloud!"
    )
    logger.info(f"Sent video with File ID: {random_id[:10]}... to chat {update.effective_chat.id}")

# --- Main Function for Deployment (STABILITY FIX) ---
def main() -> None:
    """Start the bot using Polling for maximum stability on free host."""
    
    # Get the token securely from the Render environment variables
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set. Bot cannot start.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("video", send_random_video))

    # CRITICAL FIX: Running POLLING instead of the crashing Webhook setup
    # This keeps the bot stable, though it might be slow (5-10 second delay).
    application.run_polling(poll_interval=3) 

if __name__ == "__main__":
    main()
