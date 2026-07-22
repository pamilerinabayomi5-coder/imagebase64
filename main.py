import os
import io
import base64
import telebot

# 1. Fetch the bot token from environment variables (configured on Render)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

bot = telebot.TeleBot(BOT_TOKEN)

# Welcome image URL and promotional caption text
WELCOME_IMAGE_URL = "https://freeimage.host/i/CNjKSFp"
WELCOME_TEXT = (
    "Atg is a buy and sell token application, you can earn every time you will buy token using Inr or Usdt. "
    "USDT RATE 101 RS INR 4-5% https://app-web.atg-game.com/regist?code=0eeshowcayk9\n\n"
    "Channel link https://t.me/atgpay_channel\n\n"
    "Coustomer care @Andrewtril21\n\n"
    "-------------------------------------\n"
    "📷 Send me any image, and I will convert it into a Base64 string for you."
)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        # Send photo with the text as caption
        bot.send_photo(
            message.chat.id,
            photo=WELCOME_IMAGE_URL,
            caption=WELCOME_TEXT
        )
    except Exception:
        # Fallback to plain text message if image loading fails
        bot.reply_to(message, WELCOME_TEXT)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Inform the user that the bot is processing
        bot.send_chat_action(message.chat.id, 'typing')

        # Get the highest resolution version of the photo sent
        photo_file = message.photo[-1]
        file_info = bot.get_file(photo_file.file_id)
        
        # Download the file directly into memory bytes
        downloaded_file = bot.download_file(file_info.file_path)

        # Convert the raw bytes into a Base64 string
        base64_encoded = base64.b64encode(downloaded_file).decode('utf-8')
        
        # Format the text with a standard data URI prefix
        output_text = f"data:image/jpeg;base64,{base64_encoded}"

        # Telegram text messages have a strict 4096 character limit. 
        # If the string fits, send it as text. Otherwise, send it as a .txt file.
        if len(output_text) <= 4000:
            bot.reply_to(message, f"```\n{output_text}\n```", parse_mode="Markdown")
        else:
            # Create an in-memory text file so we don't clog local storage
            file_buffer = io.BytesIO(output_text.encode('utf-8'))
            file_buffer.name = "base64_image.txt"
            
            bot.send_document(
                message.chat.id, 
                file_buffer, 
                caption="📄 The Base64 string was too long for a Telegram message, so I compiled it into this file!",
                reply_to_message_id=message.message_id
            )
            
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred while converting your image: {str(e)}")

if __name__ == "__main__":
    print("Bot is starting up using long polling...")
    bot.infinity_polling()
