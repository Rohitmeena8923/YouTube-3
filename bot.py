import os
import logging
from pytube import YouTube, Search
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler
from uuid import uuid4

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send /search <query> or use inline mode to search videos.")

# Search Command
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /search <your query>")
        return

    search = Search(query)
    results = search.results[:5]

    keyboard = [
        [InlineKeyboardButton(video.title[:50], callback_data=video.video_id)]
        for video in results
    ]

    await update.message.reply_text("Top results:", reply_markup=InlineKeyboardMarkup(keyboard))

# Button click
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = query.data
    yt = YouTube(f"https://youtube.com/watch?v={video_id}")

    buttons = []

    for stream in yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc():
        try:
            size = round(stream.filesize / (1024 * 1024), 2)
            label = f"{stream.resolution} - {size} MB"
        except:
            label = f"{stream.resolution}"
        buttons.append([InlineKeyboardButton(label, url=stream.url)])

    buttons.append([InlineKeyboardButton("Stream on YouTube", url=yt.watch_url)])

    await query.edit_message_text(
        f"*{yt.title}*\n\nChoose an option below:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Inline Query
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    search = Search(query)
    results = search.results[:5]

    articles = []
    for video in results:
        articles.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=video.title,
                description="Click to view",
                input_message_content=InputTextMessageContent(
                    f"{video.title}\nhttps://youtube.com/watch?v={video.video_id}"
                ),
            )
        )

    await update.inline_query.answer(articles, cache_time=1)

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(InlineQueryHandler(inline_handler))
    app.run_polling()

if __name__ == "__main__":
    main()