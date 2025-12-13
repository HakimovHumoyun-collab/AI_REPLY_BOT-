from loader import dp
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from aiogram import types
from aiogram.utils import executor
load_dotenv()

GEMINI_API_KEY = "AIzaSyAScKBShl9sQv_2j_8gUtD9AZ0ixR6SSFI"

logging.basicConfig(level=logging.INFO)


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

faq = {
    "salom": "Va alaykum assalom! Qanday yordam bera olaman?"
}
@dp.message_handler(commands="start")
async def bot_start(message: types.Message):
    text = f" Assalomu alaykum, {message.from_user.full_name} Sizga qanday yordam bera olaman?"
    await message.answer(text)

async def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)

        # Har doim mavjud bo‘ladigan format
        return response.candidates[0].content.parts[0].text

    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "AI bilan bog‘lanishda xatolik yuz berdi."

@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text.lower()
    await message.answer_chat_action(types.ChatActions.TYPING)
    for key, answer in faq.items():
        if key in user_text:
            await message.reply(answer)
            return

    ai_answer = await ask_gemini(user_text)
    if len(ai_answer) > 4000:  # Telegram limit ~4096
            file_path = "response.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(ai_answer)
            await message.reply_document(open(file_path, "rb"))
    else:
            await message.reply(ai_answer)

if __name__ == "__main__":
    executor.start_polling(dp)
