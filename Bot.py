#!/usr/bin/env python3
"""
Telegram User Info Bot
- Shows detailed info when messages are forwarded
- /myid command to get your own ID
- Privacy-aware handling
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserInfoBot:
    def __init__(self, token: str):
        """Initialize the bot with Telegram token"""
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
            "🔹 Use /myid to see your Telegram ID\n"
            "🔹 Forward any message to see sender info\n"
            "🔹 Use /help for assistance",
            parse_mode="HTML"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message"""
        await update.message.reply_text(
            "ℹ️ <b>Bot Commands</b>\n\n"
            "/start - Welcome message\n"
            "/myid - Show your Telegram ID\n"
            "/help - This message\n\n"
            "<b>How to use:</b>\n"
            "1. Forward any message to see sender info\n"
            "2. Some info may be hidden due to privacy settings",
            parse_mode="HTML"
        )

    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /myid command"""
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 <b>Your Telegram ID</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ First Name: {user.first_name}\n"
            f"├ Last Name: {user.last_name if user.last_name else 'N/A'}\n"
            f"└ Username: @{user.username if user.username else 'N/A'}",
            parse_mode="HTML"
        )

    @staticmethod
    def estimate_account_age(user_id: int) -> str:
        """Estimate account age from Telegram user ID"""
        try:
            # Telegram ID contains timestamp information
            timestamp = (user_id >> 32) & 0xFFFFFFFF
            account_date = datetime.fromtimestamp(timestamp)
            age = datetime.now() - account_date
            
            if age.days > 365:
                return f"{age.days//365} year{'s' if age.days//365>1 else ''}"
            return f"{age.days//30} month{'s' if age.days//30>1 else ''}"
        except Exception as e:
            logger.warning(f"Couldn't estimate account age: {e}")
            return "unknown"

    def format_user_info(self, user) -> str:
        """Format user information in tree structure"""
        return (
            f"👤 <b>User Information</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ Is Bot: {'✅ Yes' if user.is_bot else '❌ No'}\n"
            f"├ First Name: {user.first_name}\n"
            f"├ Last Name: {user.last_name if user.last_name else 'N/A'}\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"└ Account Age: {self.estimate_account_age(user.id)}\n"
        )

    def format_chat_info(self, chat) -> str:
        """Format chat/channel information"""
        return (
            f"📢 <b>Chat Information</b>\n"
            f"├ ID: <code>{chat.id}</code>\n"
            f"├ Type: {chat.type.capitalize()}\n"
            f"├ Title: {chat.title}\n"
            f"└ Username: @{chat.username if chat.username else 'N/A'}\n"
        )

    async def handle_forwarded(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle forwarded messages with comprehensive fallbacks"""
        msg = update.message
        
        if msg.forward_from:
            # Message forwarded from a user
            await msg.reply_text(
                self.format_user_info(msg.forward_from),
                parse_mode="HTML"
            )
        elif msg.forward_from_chat:
            # Message forwarded from a chat/channel
            await msg.reply_text(
                self.format_chat_info(msg.forward_from_chat),
                parse_mode="HTML"
            )
        elif msg.forward_sender_name:
            # Privacy-enabled forward
            await msg.reply_text(
                f"👤 <b>Partial Information</b>\n"
                f"├ Name: {msg.forward_sender_name}\n"
                f"└ Forward Date: {msg.forward_date.strftime('%Y-%m-%d %H:%M')}\n"
                "\nℹ️ User has forwarding privacy enabled",
                parse_mode="HTML"
            )
        else:
            await msg.reply_text(
                "❌ Couldn't retrieve sender information.\n"
                "This might be because:\n"
                "1. The message wasn't properly forwarded\n"
                "2. The sender has strict privacy settings\n"
                "3. It's from a secret chat",
                parse_mode="HTML"
            )

    def run(self):
        """Run the bot until interrupted"""
        logger.info("Starting bot...")
        self.app.run_polling()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("Missing TELEGRAM_BOT_TOKEN in environment variables")
        exit(1)

    # Create and run bot
    bot = UserInfoBot(BOT_TOKEN)
    bot.run()
