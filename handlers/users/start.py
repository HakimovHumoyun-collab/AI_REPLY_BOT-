from loader import dp
import logging
import os  # Import os to use os.getenv()
from dotenv import load_dotenv
import google.generativeai as genai
from aiogram import types
from aiogram.utils import executor

# Load environment variables first
load_dotenv()

# Now you can safely get the API key from the environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configure Gemini API with the key from environment
genai.configure(api_key=GEMINI_API_KEY)

# Create a model instance
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Simple FAQ dictionary
faq = {
    "salom": "Va alaykum assalom! Qanday yordam bera olaman?"
}

@dp.message_handler(commands="start")
async def bot_start(message: types.Message):
    text = f"Assalomu alaykum, {message.from_user.full_name}! Sizga qanday yordam bera olaman?"
    await message.answer(text)


# Function to ask Gemini for a response
async def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "AI bilan bog‘lanishda xatolik yuz berdi."


@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text.lower()
    await message.answer_chat_action(types.ChatActions.TYPING)

    # Handle FAQ responses
    for key, answer in faq.items():
        if key in user_text:
            await message.reply(answer)
            return

    # If no FAQ match, get AI-generated response from Gemini
    ai_answer = await ask_gemini(user_text)

    # If the answer exceeds Telegram's message limit, send it as a file
    if len(ai_answer) > 4000:  # Telegram limit ~4096
        file_path = "response.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ai_answer)
        with open(file_path, "rb") as document:
            await message.reply_document(document)
    else:
        await message.reply(ai_answer)


if __name__ == "__main__":
    executor.start_polling(dp)
