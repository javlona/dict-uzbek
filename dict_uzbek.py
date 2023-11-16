import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from googletrans import Translator
import logging
import json

# File path to store user information
user_info_file_path = "user_info_dict_uzbek.json"

# Initialize the Translator
translator = Translator()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# # Sample list of English words
# english_words = ["apple", "book", "cat", "dog", "elephant", "flower", "guitar", "house", "island", "jungle"]

# Function to read words from a text file
def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

# Your list of words from the text file
word_list_file_path = "word_list.txt"
english_words = read_words_from_file(word_list_file_path)

# Save users infos into a json file
def save_user_info(user_id, first_name, last_name, username):
    # Load existing user information from the file
    user_info = load_user_info()

    # Add or update user information
    user_info[user_id] = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username
    }

    # Save the updated user information back to the file
    with open(user_info_file_path, 'w') as file:
        json.dump(user_info, file)

def load_user_info():
    try:
        # Load user information from the file
        with open(user_info_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty dictionary
        return {}


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    save_user_info(user.id, user.first_name, user.last_name, user.username)
    """Send a start message when the command /start is issued."""
    start_message = (
        "Inglizcha-o'zbekcha tarjimon botiga xush kelibsiz!\n"
        "Matnni ingliz tilidan oʻzbek tiliga tarjima qilish uchun ushbu botdan foydalanishingiz mumkin.\n"
        "Tarjimani boshlash uchun “Translate” tugmasini bosing yoki tasodifiy inglizcha so‘zlar va ularning o‘zbekcha tarjimalarini olish uchun “Send Random Words” tugmasini bosing."
    )
    keyboard = [
        [InlineKeyboardButton("Translate", callback_data='translate')],
        [InlineKeyboardButton("Send Random Words", callback_data='random_words')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(start_message, reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_message = (
        "This bot can do the following:\n"
        "/start - Start the bot and see the available options.\n"
        "/help - Get help and see available commands.\n"
        "Additionally, you can use the inline buttons to translate text or get random English words with their Uzbek translations."
    )
    update.message.reply_text(help_message)

def button(update: Update, context: CallbackContext) -> None:
    """Handle button press."""
    query = update.callback_query
    query.answer()

    # Determine which button was pressed
    if query.data == 'translate':
        context.bot.send_message(chat_id=query.message.chat_id, text="Send me a text and I will translate it.")
    elif query.data == 'random_words':
        send_random_words(query, context)

def translate_command(update: Update, context: CallbackContext) -> None:
    """Prompt user to send text for translation."""
    update.message.reply_text("Send me a text and I will translate it to Uzbek.")

def send_random_words(query, context: CallbackContext):
    """Send 5 random English words and their translations."""
    random_words = random.sample(english_words, 5)
    try:
        message = ""
        for word in random_words:
            translated = translator.translate(word, dest='uz')
            message += f"{word} - {translated.text}\n"
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        context.bot.send_message(chat_id=query.message.chat_id, text="Sorry, I couldn't process the request. Please try again later.")

def random_words_command(update: Update, context: CallbackContext) -> None:
    """Send 5 random English words and their translations."""
    random_words = random.sample(english_words, 5)
    try:
        message = ""
        for word in random_words:
            translated = translator.translate(word, dest='uz')
            message += f"{word} - {translated.text}\n"
        update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        update.message.reply_text("Sorry, I couldn't process the request. Please try again later.")

def translate_text(update: Update, context: CallbackContext) -> None:
    """Translate the user message."""
    user_text = update.message.text
    try:
        translated = translator.translate(user_text, dest='uz')
        update.message.reply_text(translated.text)
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        update.message.reply_text("Sorry, I couldn't translate that. Please try again later.")

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6946406792:AAFjSgfIwCa0eL0RfraypqzFU-8e6ydw27s", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher



    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", help_command))

    # on button press in Telegram
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler("translate", translate_command))

    dp.add_handler(CommandHandler("random_words", random_words_command))

    # on non-command i.e message - translate the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, translate_text))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
