#!/usr/bin/env python3
"""
Telegram User Info Bot with /myid command
Shows user info for forwarded messages and own ID
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserInfoBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(self.token).build()
        
        # Register handlers
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help_command),
            CommandHandler("myid", self.myid_command),
            MessageHandler(filters.FORWARDED, self.handle_forwarded)
        ]
        for handler in handlers:
            self.app.add_handler(handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message"""
        user = update.effective_user
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n"
            "I can show information about forwarded messages and user IDs.\n\n"
            "Commands:\n"
            "/myid - Show your Telegram ID\n"
            "/help - Show help information\n\n"
            "Just forward me a message to see info about the sender!",
            parse_mode="HTML"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message"""
        await update.message.reply_text(
            "ℹ️ <b>Bot Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/myid - Show your Telegram ID\n"
            "/help - This message\n\n"
            "<b>Forwarding:</b>\n"
            "• Forward any message to see sender info\n"
            "• Some info may be hidden due to privacy settings\n\n"
            "<b>Privacy Note:</b>\n"
            "I don't store any of your data.",
            parse_mode="HTML"
        )

    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /myid command"""
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 <b>Your Telegram ID</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ First Name: {user.first_name}\n"
            f"└ Username: @{user.username if user.username else 'N/A'}",
            parse_mode="HTML"
        )

    @staticmethod
    def estimate_account_age(user_id: int) -> str:
        """Estimate account age from user ID"""
        try:
            timestamp = (user_id >> 32) & 0xFFFFFFFF
            account_date = datetime.fromtimestamp(timestamp)
            age = datetime.now() - account_date
            
            if age.days > 365:
                return f"{age.days//365} year{'s' if age.days//365>1 else ''}"
            return f"{age.days//30} month{'s' if age.days//30>1 else ''}"
        except:
            return "unknown"

    def format_user_info(self, user) -> str:
        """Format user info in tree structure"""
        return (
            f"👤 <b>User Information</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ Is Bot: {user.is_bot}\n"
            f"├ First Name: {user.first_name}\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"└ Account Age: {self.estimate_account_age(user.id)}\n"
        )

    def format_chat_info(self, chat) -> str:
        """Format chat/channel info"""
        return (
            f"📢 <b>Chat Information</b>\n"
            f"├ ID: <code>{chat.id}</code>\n"
            f"├ Type: {chat.type}\n"
            f"├ Title: {chat.title}\n"
            f"└ Username: @{chat.username if chat.username else 'N/A'}\n"
        )

    async def handle_forwarded(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle forwarded messages with privacy fallbacks"""
        msg = update.message
        response = None

        if msg.forward_from:
            response = self.format_user_info(msg.forward_from)
        elif msg.forward_from_chat:
            response = self.format_chat_info(msg.forward_from_chat)
        elif msg.forward_sender_name:
            response = (
                f"👤 <b>Partial Information</b> (Privacy Enabled)\n"
                f"├ Name: {msg.forward_sender_name}\n"
                f"└ Forward Date: {msg.forward_date.strftime('%Y-%m-%d %H:%M')}\n"
            )
        else:
            response = "❌ No forwarding information available"

        if response:
            await msg.reply_text(response, parse_mode="HTML")

    def run(self):
        """Run the bot"""
        logger.info("Starting User Info Bot...")
        self.app.run_polling()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("Missing TELEGRAM_BOT_TOKEN in environment variables")
        exit(1)

    bot = UserInfoBot(BOT_TOKEN)
    bot.run()
