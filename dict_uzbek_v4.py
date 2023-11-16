import random
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
from datetime import datetime, time, timedelta
import logging
import json

# File path to store user information
user_info_file_path = "dict_uzbek_userinfo.json"

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

# Function to save user information
def save_user_info(chat_id, user_id, first_name, last_name, username):
    # Load existing user information from the file
    user_info = load_user_info()

    # Add or update user information
    user_info[user_id] = {
        "chat_id": chat_id,
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



# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat_id = update.message.chat_id
    save_user_info(chat_id, user.id, user.first_name, user.last_name, user.username)
    
    start_message = (
        "Inglizcha-o'zbekcha tarjimon botiga xush kelibsiz!\n"
        "Matnni ingliz tilidan oʻzbek tiliga tarjima qilish uchun ushbu botdan foydalanishingiz mumkin.\n"
        "Tarjimani boshlash uchun “Translate” tugmasini bosing yoki tasodifiy inglizcha so‘zlar va ularning o‘zbekcha tarjimalarini olish uchun “Send Random Words” tugmasini bosing."
    )
    
      # Create a custom keyboard
    keyboard = [
        [KeyboardButton("/translate")],
        [KeyboardButton("/random_words")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(start_message, reply_markup=reply_markup)




def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_message = (
        "This bot can do the following:\n"
        "/start - Botni ishga tushiring va mavjud variantlarni ko'ring.\n"
        "/random_words - Tasodifiy so'zlarni va ularning tarjimasini yuboradi.\n"
        "/send_words_daily - Har kuni avtomatik ravishda so'zlarni yuborishni boshlaydi.\n"
        "/stop_messages - Har kuni avtomatik ravishda so'zlarni yuborishni to'xtatadi.\n"
        "/help - Yordam olish va mavjud buyruqlarni ko'ring."
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
        

# Generates 5 random words and translates them
def generate_random_words_message():
    random_words = random.sample(english_words, 5)
    message = ""
    for word in random_words:
        try:
            translated = translator.translate(word, dest='uz')
            message += f"{word} - {translated.text}\n"
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            # You can choose to append an error message or skip the word
            message += f"{word} - Translation Error\n"
    return message


def send_random_words(query, context: CallbackContext):
    """Send 5 random English words and their translations."""
    message = generate_random_words_message()
    context.bot.send_message(chat_id=query.message.chat_id, text=message)


def random_words_command(update: Update, context: CallbackContext) -> None:
    """Send 5 random English words and their translations."""
    message = generate_random_words_message()
    update.message.reply_text(message)


def translate_command(update: Update, context: CallbackContext) -> None:
    """Prompt user to send text for translation."""
    update.message.reply_text("Menga matn yuboring, men uni o‘zbek tiliga tarjima qilaman.")

# def send_random_words(query, context: CallbackContext):
#     """Send 5 random English words and their translations."""
#     random_words = random.sample(english_words, 5)
#     try:
#         message = ""
#         for word in random_words:
#             translated = translator.translate(word, dest='uz')
#             message += f"{word} - {translated.text}\n"
#         context.bot.send_message(chat_id=query.message.chat_id, text=message)
#     except Exception as e:
#         logger.error(f"Error in translation: {e}")
#         context.bot.send_message(chat_id=query.message.chat_id, text="Sorry, I couldn't process the request. Please try again later.")

# def random_words_command(update: Update, context: CallbackContext) -> None:
#     """Send 5 random English words and their translations."""
#     random_words = random.sample(english_words, 5)
#     try:
#         message = ""
#         for word in random_words:
#             translated = translator.translate(word, dest='uz')
#             message += f"{word} - {translated.text}\n"
#         update.message.reply_text(message)
#     except Exception as e:
#         logger.error(f"Error in translation: {e}")
#         update.message.reply_text("Sorry, I couldn't process the request. Please try again later.")

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


def send_scheduled_message(context: CallbackContext):
    job = context.job
    chat_id, message_func, scheduled_time = job.context
    message = message_func()  # Call the function to get the message
    context.bot.send_message(chat_id=chat_id, text=message)

    # Reschedule the job for the next day
    next_day = datetime.now() + timedelta(days=1)
    scheduled_datetime = datetime.combine(next_day.date(), scheduled_time)
    delay = (scheduled_datetime - datetime.now()).total_seconds()
    context.job_queue.run_once(send_scheduled_message, delay, context=(chat_id, message_func, scheduled_time))

# It schedules a time for sending messages periodically
def schedule_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    # Define multiple scheduled times and corresponding message functions
    schedule_times = [(time(11, 0, 0), generate_random_words_message),
                      (time(17, 0, 0), generate_random_words_message)]

    for scheduled_time, message_func in schedule_times:
        # Check if a job for this time already exists
        existing_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        if any(job.context[2] == scheduled_time for job in existing_jobs):
            # Skip scheduling if a job for this time already exists
            continue

        # Calculate the delay for the first run
        now = datetime.now()
        scheduled_datetime = datetime.combine(now.date(), scheduled_time)
        if now.time() > scheduled_time:
            scheduled_datetime += timedelta(days=1)
        delay = (scheduled_datetime - now).total_seconds()

        # Schedule the job
        context.job_queue.run_once(send_scheduled_message, delay, context=(chat_id, message_func, scheduled_time), name=str(chat_id))

    # Send a confirmation message
    if existing_jobs:
        update.message.reply_text("Siz allaqachon har kuni so'zlar olishni rejalashtirgansiz.")
    else:
        update.message.reply_text("Siz endi har kuni kuniga ikki marta 5 ta tasodifiy so'z olasiz.")

def stop_scheduled_messages(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    # Stop any current jobs for this chat_id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    update.message.reply_text("Barcha rejalashtirilgan xabarlar to'xtatildi.")

def main():
    """Start the bot."""

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create the Updater and pass it your bot's token.
    updater = Updater("6946406792:AAFjSgfIwCa0eL0RfraypqzFU-8e6ydw27s", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(CommandHandler("translate", translate_command))

    dp.add_handler(CommandHandler("random_words", random_words_command))

    # Handler to start scheduling everyday messages
    dp.add_handler(CommandHandler("send_words_daily", schedule_message))
    
    # It will stop sending everyday messages
    dp.add_handler(CommandHandler("stop_messages", stop_scheduled_messages))

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
