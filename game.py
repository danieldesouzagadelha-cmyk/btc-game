from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN

import sqlite3


# =========================
# DATABASE
# =========================

conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players(
id TEXT PRIMARY KEY,
name TEXT,
coins INTEGER,
invited_by TEXT
)
""")

conn.commit()


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = str(user.id)
    name = user.first_name

    invited_by = None

    # convite
    if context.args:
        invited_by = context.args[0]

    cur.execute("SELECT * FROM players WHERE id=?", (user_id,))
    p = cur.fetchone()

    if not p:

        coins = 1000

        cur.execute(
            "INSERT INTO players VALUES (?,?,?,?)",
            (user_id, name, coins, invited_by)
        )

        conn.commit()

        # bônus de convite
        if invited_by:

            cur.execute(
                "UPDATE players SET coins = coins + 300 WHERE id=?",
                (invited_by,)
            )

            conn.commit()

    # botão abrir jogo

    keyboard = [[
        InlineKeyboardButton(
            "🎮 Abrir BTC Prediction Arena",
            web_app=WebAppInfo(
                url="https://btc-game-seven.vercel.app"
            )
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    invite_link = f"https://t.me/{context.bot.username}?start={user_id}"

    await update.message.reply_text(
f"""
🚀 BTC Prediction Arena

🪙 Você começa com 1000 coins

📈 Preveja se o BTC sobe ou desce.

👥 Convide amigos e ganhe 300 coins.

🔗 Seu link de convite:
{invite_link}
""",
        reply_markup=reply_markup
    )


# =========================
# RANKING
# =========================

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "SELECT name, coins FROM players ORDER BY coins DESC LIMIT 10"
    )

    rows = cur.fetchall()

    text = "🏆 TOP PLAYERS\n\n"

    pos = 1

    for r in rows:

        text += f"{pos}️⃣ {r[0]} — {r[1]} coins\n"

        pos += 1

    await update.message.reply_text(text)


# =========================
# BALANCE
# =========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = str(update.effective_user.id)

    cur.execute("SELECT coins FROM players WHERE id=?", (user,))
    row = cur.fetchone()

    if row:

        coins = row[0]

        await update.message.reply_text(
            f"🪙 Seu saldo: {coins} coins"
        )


# =========================
# BOT START
# =========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("balance", balance))

    print("🚀 Bot rodando...")

    app.run_polling()


if __name__ == "__main__":
    main()