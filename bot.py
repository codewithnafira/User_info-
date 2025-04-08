#!/usr/bin/env python3
"""
Telegram User Info Bot
Displays detailed information about forwarded messages in a tree format
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
        """Initialize the bot with a Telegram token"""
        self.token = token
        self.app = Application.builder().token(self.token).build()
        
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.FORWARDED, self.handle_forwarded))
        self.app.add_handler(CommandHandler("help", self.help_command))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when command /start is issued"""
        user = update.effective_user
        welcome_msg = (
            f"👋 Hello {user.first_name}!\n\n"
            "🔍 I can show information about forwarded messages.\n"
            "Simply forward me any message and I'll display details about the original sender.\n\n"
            "Type /help for more information."
        )
        await update.message.reply_text(welcome_msg)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message when command /help is issued"""
        help_msg = (
            "ℹ️ <b>User Info Bot Help</b>\n\n"
            "• Forward any message to me to see information about the original sender\n"
            "• Some information might be unavailable due to privacy settings\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - This help message\n\n"
            "The bot will display information in this format:\n"
            "👤 User Information\n"
            " ├ ID: 123456789\n"
            " ├ Is Bot: False\n"
            " ├ First Name: John\n"
            " ├ Username: @johndoe\n"
            " └ Account Age: 2 years old"
        )
        await update.message.reply_text(help_msg, parse_mode="HTML")

    @staticmethod
    def estimate_account_age(user_id: int) -> str:
        """Estimate account age based on Telegram user ID"""
        try:
            timestamp = (user_id >> 32) & 0xFFFFFFFF
            account_date = datetime.fromtimestamp(timestamp)
            delta = datetime.now() - account_date
            
            if delta.days > 365:
                years = delta.days // 365
                return f"{years} year{'s' if years > 1 else ''} old"
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} old"
        except Exception as e:
            logger.warning(f"Couldn't estimate account age: {e}")
            return "unknown age"

    def format_user_info(self, user) -> str:
        """Format user information in tree structure"""
        return (
            f"👤 <b>User Information</b>\n"
            f" ├ ID: <code>{user.id}</code>\n"
            f" ├ Is Bot: {user.is_bot}\n"
            f" ├ First Name: {user.first_name}\n"
            f" ├ Username: @{user.username if user.username else 'N/A'}\n"
            f" ├ Language: {user.language_code if hasattr(user, 'language_code') else 'N/A'}\n"
            f" └ Account Age: {self.estimate_account_age(user.id)}\n"
        )

    def format_chat_info(self, chat) -> str:
        """Format chat/channel information in tree structure"""
        return (
            f"📢 <b>Chat Information</b>\n"
            f" ├ ID: <code>{chat.id}</code>\n"
            f" ├ Type: {chat.type}\n"
            f" ├ Title: {chat.title}\n"
            f" └ Username: @{chat.username if chat.username else 'N/A'}\n"
        )

    async def handle_forwarded(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle forwarded messages and display information"""
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
        else:
            await msg.reply_text(
                "⚠ Couldn't retrieve sender information. "
                "This might be due to privacy settings that prevent forwarding.",
                parse_mode="HTML"
            )

    def run(self):
        """Run the bot until interrupted"""
        logger.info("Starting User Info Bot...")
        self.app.run_polling()


if __name__ == "__main__":
    # Load configuration
    import os
    from dotenv import load_dotenv
    
    load_dotenv()  # Load environment variables from .env file
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
        exit(1)
    
    # Create and run bot
    bot = UserInfoBot(BOT_TOKEN)
    bot.run()
