import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    JobQueue,
)
from datetime import time

TOKEN = os.getenv("8391501465:AAG8K2zsVz8XPbkBAtFiw2zQN4VPdHyndH0")
MY_USER_ID = int(os.getenv("5949872528"))
TASKS_FILE = "tasks.txt"

async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MY_USER_ID:
        return
    text = update.message.text.strip()
    if not text:
        return
    with open(TASKS_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    await update.message.reply_text(f"Task saved for tomorrow: {text}")

async def send_polls(context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(TASKS_FILE):
        return
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = [line.strip() for line in f if line.strip()]
    if not tasks:
        return
    for task in tasks:
        await context.bot.send_poll(
            chat_id=MY_USER_ID,
            question=task,
            options=["Yes", "No"],
            is_anonymous=False,
        )
    open(TASKS_FILE, "w").close()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_task))
    job_queue: JobQueue = app.job_queue
    # 13:00 Uzbekistan = 08:00 UTC
    job_queue.run_daily(send_polls, time=time(8, 0, 0))
    print("Bot started...")
    app.run_polling()
