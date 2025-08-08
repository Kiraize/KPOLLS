from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import JobQueue
import os
from datetime import time

TOKEN = os.getenv("8231704674:AAF7Pqc_jgftJrAajQy7KCi2pg7thlqeo0o")
MY_USER_ID = int(os.getenv("5949872528"))

TASKS_FILE = "tasks.txt"

async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save any message you send into a file for tomorrow's poll."""
    if update.effective_user.id != MY_USER_ID:
        return  # Ignore strangers

    text = update.message.text.strip()
    if not text:
        return

    with open(TASKS_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

    await update.message.reply_text(f"📝 Saved for tomorrow's poll: {text}")

async def send_polls(context: ContextTypes.DEFAULT_TYPE):
    """Send all saved tasks as polls, then clear the file."""
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
            is_anonymous=False
        )

    # Clear file after sending
    open(TASKS_FILE, "w").close()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Save any message as a task
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_task))

    # Schedule daily job at 8:00 AM Uzbekistan time (UTC+5)
    job_queue: JobQueue = app.job_queue
    job_queue.run_daily(
        send_polls,
        time=time(3, 0, 0),  # 3 AM UTC = 8 AM Uzbekistan
    )

    print("Bot is running...")
    app.run_polling()
