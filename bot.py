from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os
import requests
import re

TOKEN = "8602271329:AAHyMA06xYEmjWlzRu1KYfV1_DC-6lPzRbc"
DATA_FILE = "notes.json"

def load_notes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_notes(notes):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def get_usd():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            irr = data['rates'].get('IRR', 0)
            if irr:
                return f"💵 دلار: {int(irr/10):,} تومان"
        return "❌ خطا"
    except:
        return "❌ خطا"

def get_gold():
    try:
        url = "https://api.gold-api.com/price/XAU"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            price = data.get('price', 0)
            if price:
                return f"🏆 طلا: ${price:,.2f}"
        return "❌ خطا"
    except:
        return "❌ خطا"

def get_coin():
    try:
        url = "https://www.tgju.org/coin-price"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*تومان', r.text)
            if match:
                price = match.group(1).replace(',', '')
                return f"🪙 سکه: {int(price):,} تومان"
        return "❌ خطا"
    except:
        return "❌ خطا"

def get_crypto(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if symbol in data:
                price = data[symbol]['usd']
                names = {
                    "bitcoin": "🪙 بیت‌کوین",
                    "ethereum": "🔷 اتریوم",
                    "dogecoin": "🐕 دوج‌کوین",
                    "solana": "☀️ سولانا"
                }
                name = names.get(symbol, symbol.upper())
                return f"{name}: ${price:,.2f}"
        return "❌ خطا"
    except:
        return "❌ خطا"

def get_cars():
    try:
        url = "https://www.bama.ir/car/api/search"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            cars = []
            for car in data.get('data', [])[:5]:
                name = car.get('title', 'نامشخص')
                price = car.get('price', 'نامشخص')
                if price != 'نامشخص':
                    cars.append(f"🚗 {name}: {price:,} تومان")
                else:
                    cars.append(f"🚗 {name}")
            if cars:
                return "\n".join(cars)
        return "❌ خطا"
    except:
        return "❌ خطا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 همه قیمت‌ها", callback_data="price")],
        [InlineKeyboardButton("💵 دلار", callback_data="usd"), InlineKeyboardButton("🏆 طلا", callback_data="gold")],
        [InlineKeyboardButton("🪙 سکه", callback_data="coin"), InlineKeyboardButton("🚗 ماشین", callback_data="car")],
        [InlineKeyboardButton("🪙 بیت‌کوین", callback_data="btc"), InlineKeyboardButton("🔷 اتریوم", callback_data="eth")],
        [InlineKeyboardButton("🐕 دوج‌کوین", callback_data="doge"), InlineKeyboardButton("☀️ سولانا", callback_data="solana")],
        [InlineKeyboardButton("📝 یادداشت‌ها", callback_data="notes")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "👋 **به ربات قیمت‌یاب خوش آمدید!**\n\n"
        "📊 با دکمه‌های زیر قیمت‌ها رو ببین:\n\n"
        "💵 دلار | 🏆 طلا | 🪙 سکه\n"
        "🪙 بیت‌کوین | 🔷 اتریوم | 🐕 دوج‌کوین\n"
        "🚗 قیمت ماشین\n\n"
        "📝 **یادداشت‌ها:**\n"
        "/note [متن] - ذخیره یادداشت\n"
        "/mynotes - دیدن یادداشت‌ها\n"
        "/del [شماره] - حذف یادداشت"
    )
    await update.message.reply_text(text, reply_markup=reply_markup)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت...")
    msg = (
        f"📊 **قیمت‌ها:**\n\n{get_usd()}\n{get_gold()}\n{get_coin()}\n"
        f"{get_crypto('bitcoin')}\n{get_crypto('ethereum')}\n{get_crypto('dogecoin')}\n{get_crypto('solana')}"
    )
    await update.message.reply_text(msg)

async def usd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_usd())

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_gold())

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_coin())

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto("bitcoin"))

async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto("ethereum"))

async def doge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto("dogecoin"))

async def solana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto("solana"))

async def car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت...")
    await update.message.reply_text(f"🚗 **ماشین‌ها:**\n\n{get_cars()}")

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    note_text = update.message.text.replace("/note", "").strip()
    if not note_text:
        await update.message.reply_text("❌ متن یادداشت رو بنویس!")
        return
    notes = load_notes()
    if user_id not in notes:
        notes[user_id] = []
    notes[user_id].append(note_text)
    save_notes(notes)
    await update.message.reply_text(f"✅ یادداشت ذخیره شد! (شماره: {len(notes[user_id])})\n\n📝 {note_text}")

async def mynotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    notes = load_notes()
    if user_id not in notes or not notes[user_id]:
        await update.message.reply_text("📭 یادداشتی نداری!")
        return
    note_list = []
    for i, note in enumerate(notes[user_id], 1):
        note_list.append(f"{i}️⃣ {note}")
    keyboard = [[InlineKeyboardButton(f"🗑️ حذف {i}", callback_data=f"del_{i}")] for i in range(1, len(notes[user_id]) + 1)]
    await update.message.reply_text("📋 **یادداشت‌های تو:**\n\n" + "\n".join(note_list), reply_markup=InlineKeyboardMarkup(keyboard))

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        parts = update.message.text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ شماره یادداشت رو بنویس!")
            return
        note_number = int(parts[1])
    except:
        await update.message.reply_text("❌ شماره نامعتبر!")
        return
    notes = load_notes()
    if user_id not in notes or not notes[user_id]:
        await update.message.reply_text("📭 یادداشتی نیست!")
        return
    if note_number < 1 or note_number > len(notes[user_id]):
        await update.message.reply_text(f"❌ یادداشت {note_number} پیدا نشد!")
        return
    deleted = notes[user_id].pop(note_number - 1)
    save_notes(notes)
    await update.message.reply_text(f"🗑️ حذف شد!\n\n📝 {deleted}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    data = query.data
    if data == "price":
        msg = f"📊 **قیمت‌ها:**\n\n{get_usd()}\n{get_gold()}\n{get_coin()}\n{get_crypto('bitcoin')}\n{get_crypto('ethereum')}\n{get_crypto('dogecoin')}\n{get_crypto('solana')}"
        await query.message.reply_text(msg)
    elif data == "usd":
        await query.message.reply_text(get_usd())
    elif data == "gold":
        await query.message.reply_text(get_gold())
    elif data == "coin":
        await query.message.reply_text(get_coin())
    elif data == "btc":
        await query.message.reply_text(get_crypto("bitcoin"))
    elif data == "eth":
        await query.message.reply_text(get_crypto("ethereum"))
    elif data == "doge":
        await query.message.reply_text(get_crypto("dogecoin"))
    elif data == "solana":
        await query.message.reply_text(get_crypto("solana"))
    elif data == "car":
        await query.message.reply_text(f"🚗 **ماشین‌ها:**\n\n{get_cars()}")
    elif data == "notes":
        await query.message.reply_text("📝 /note [متن]\n/mynotes\n/del [شماره]")
    elif data.startswith("del_"):
        note_number = int(data.split("_")[1])
        notes = load_notes()
        if user_id in notes and 0 < note_number <= len(notes[user_id]):
            deleted = notes[user_id].pop(note_number - 1)
            save_notes(notes)
            await query.edit_message_text(f"🗑️ حذف شد!\n\n📝 {deleted}")
        else:
            await query.edit_message_text("❌ قبلاً حذف شده!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("usd", usd))
    app.add_handler(CommandHandler("gold", gold))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("eth", eth))
    app.add_handler(CommandHandler("doge", doge))
    app.add_handler(CommandHandler("solana", solana))
    app.add_handler(CommandHandler("car", car))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("mynotes", mynotes))
    app.add_handler(CommandHandler("del", delete_note))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🤖 ربات روشن شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
