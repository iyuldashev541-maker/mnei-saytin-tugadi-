import os, io, asyncio, re
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

# 1. Sozlamalarni yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchi ma'lumotlarini vaqtinchalik saqlash
user_data = {}


# 2. Klaviaturalar
def main_menu():
    url = "https://iyuldashev541-maker.github.io/meni-saytim-333/"
    kb = [
        [KeyboardButton(text="💎 Premium Launcher", web_app=WebAppInfo(url=url)), KeyboardButton(text="💸 Xarajatlar")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📞 Bog'lanish")],
        [KeyboardButton(text="🧹 Tozalash")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def expenses_menu():
    kb = [
        [KeyboardButton(text="🍎 Mevalar"), KeyboardButton(text="🚕 Taksi")],
        [KeyboardButton(text="🥤 Ichimliklar"), KeyboardButton(text="🏠 Ro'zg'or")],
        [KeyboardButton(text="🎁 Boshqa"), KeyboardButton(text="⬅️ Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# 3. Handlerlar
@dp.message(F.text == "/start")
async def start(m: types.Message):
    user_id = m.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'history': {}, 'current_cat': None}

    name = m.from_user.first_name if m.from_user.first_name else "User"
    await m.answer(f"SYSTEM_READY: Salom {name}! 💀\nBoshqaruv panelini tanlang:", reply_markup=main_menu())


# BOG'LANISH BO'LIMI (HTML formatga o'tkazildi, xato bermaydi)
@dp.message(F.text == "📞 Bog'lanish")
async def contact_info(m: types.Message):
    text = (
        "<b>🚷 ADMIN_OVERRIDE_ACCESS:</b>\n\n"
        "📞 <b>Tel:</b> +998999241280\n"
        "👤 <b>Username:</b> @Islombek_GIG\n"
        "📧 <b>Gmail:</b> iyuldashev541@gmail.com\n\n"
        "⚠️ <i>Tizimda xatolik aniqlansa, darhol bog'laning.</i>"
    )
    await m.answer(text, parse_mode="HTML")


@dp.message(F.text == "💸 Xarajatlar")
async def show_expenses(m: types.Message):
    await m.answer("DATABASE_CATEGORIES:", reply_markup=expenses_menu())


@dp.message(F.text.in_({"🍎 Mevalar", "🚕 Taksi", "🥤 Ichimliklar", "🏠 Ro'zg'or", "🎁 Boshqa"}))
async def set_cat(m: types.Message):
    uid = m.from_user.id
    if uid not in user_data: user_data[uid] = {'history': {}, 'current_cat': None}

    user_data[uid]['current_cat'] = m.text
    await m.answer(f"💰 {m.text} tanlandi. Miqdorni kiriting:\n(Masalan: 45000 olma yoki 15000)")


# Narxni saqlash (Barcha xatoliklar filtrlangan)
@dp.message(lambda m: user_data.get(m.from_user.id, {}).get('current_cat') is not None and m.text not in ["⬅️ Orqaga",
                                                                                                          "📊 Statistika",
                                                                                                          "📞 Bog'lanish",
                                                                                                          "🧹 Tozalash"])
async def save_money(m: types.Message):
    uid = m.from_user.id
    cat = user_data[uid]['current_cat']

    # Matn ichidan faqat raqamlarni ajratish
    nums = re.findall(r'\d+', m.text)
    if not nums:
        return await m.answer("XATO: Iltimos, miqdorni raqamda kiriting.")

    price = int("".join(nums))
    user_data[uid]['history'][cat] = user_data[uid]['history'].get(cat, 0) + price
    user_data[uid]['current_cat'] = None

    await m.answer(f"✅ LOG_SAVED: {price:,} so'm -> {cat}", reply_markup=main_menu())


# Statistika (Hacker stili va Emoji xatosiz)
@dp.message(F.text == "📊 Statistika")
async def get_stats(m: types.Message):
    uid = m.from_user.id
    if uid not in user_data or not user_data[uid]['history']:
        return await m.answer("NO_DATA_FOUND: Ma'lumotlar mavjud emas.")

    history = user_data[uid]['history']

    # Emojisiz label tayyorlash (Matplotlib xato bermasligi uchun)
    clean_labels = [re.sub(r'[^\w\s]', '', k).strip() for k in history.keys()]
    values = list(history.values())

    plt.figure(figsize=(6, 6), facecolor='#0d0208')
    plt.rcParams['text.color'] = '#00ff41'
    plt.pie(values, labels=clean_labels, autopct='%1.1f%%', startangle=140)
    plt.title("EXPENSE_ANALYSIS")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#0d0208')
    buf.seek(0)
    plt.close()

    await m.answer_photo(photo=BufferedInputFile(buf.read(), filename="stat.png"),
                         caption="📈 Tizim statistikasi tayyor.")


@dp.message(F.text == "⬅️ Orqaga")
async def back(m: types.Message):
    await m.answer("BACK_TO_ROOT:", reply_markup=main_menu())


@dp.message(F.text == "🧹 Tozalash")
async def clear(m: types.Message):
    user_data[m.from_user.id] = {'history': {}, 'current_cat': None}
    await m.answer("MEMORY_PURGED: Barcha ma'lumotlar o'chirildi! 🗑")


async def main():
    # Eski update'larni o'tkazib yuborish (Conflict xatosini kamaytiradi)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass