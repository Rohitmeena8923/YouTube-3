import os
import logging
from pytube import YouTube, Search
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    InlineQueryHandler,
)
from uuid import uuid4
from db import log_search

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /search <keywords> or inline: @YourBotName <query>")

# /search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Use /search <keywords>")
        return

    search = Search(query)
    results = search.results[:10]

    buttons = [
        [InlineKeyboardButton(video.title[:50], callback_data=video.video_id)]
        for video in results
    ]

    log_search(update.effective_user.id, query)
    await update.message.reply_text("Top results:", reply_markup=InlineKeyboardMarkup(buttons))

# Button click handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_id = query.data
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    buttons = []

    for s in streams:
        try:
            size_mb = round(s.filesize / (1024 * 1024), 2)
        except:
            size_mb = "?"
        buttons.append([
            InlineKeyboardButton(f"{s.resolution} - {size_mb} MB", url=s.url)
        ])

    buttons.append([InlineKeyboardButton("Watch Video (stream)", url=yt.watch_url)])

    msg = f"*{yt.title}*\n\nChoose a resolution to download or stream:"
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# Inline search handler
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    search = Search(query)
    results = search.results[:5]

    articles = []
    for video in results:
        thumb_url = video.thumbnail_url
        articles.append(
            InlineQueryResultPhoto(
                id=str(uuid4()),
                title=video.title,
                description=video.watch_url,
                thumbnail_url=thumb_url,
                photo_url=thumb_url,
                caption=f"[{video.title}]({video.watch_url})",
                parse_mode="Markdown"
            )
        )
    log_search(update.inline_query.from_user.id, query)
    await update.inline_query.answer(articles, cache_time=1)

# Main entry point
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()

if __name__ == "__main__":
    main()