from telegram.ext import Updater, CommandHandler
import yaml
import logging
from functools import partial
from modules.profile import pjsk_profile, pjsk_process
from modules.gacha import fakegacha, getcurrentgacha
from functools import wraps
from telegram import ChatAction
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

with open('config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def start(update, context):
    update.message.reply_text('https://nightcord.de/')


@send_typing_action
def profile(update, context, server):
    if len(context.args) == 0:
        update.message.reply_text('请指定玩家ID')
        return
    user_id = context.args[0]
    if not user_id.isdigit():
        update.message.reply_text('玩家ID必须为数字')
        return
    try:
        update.message.reply_photo(pjsk_profile(user_id, False, server))
    except Exception as e:
        update.message.reply_text('出了点毛病，可能是没找着')


@send_typing_action
def process(update, context, diff, server):
    if len(context.args) == 0:
        update.message.reply_text('请指定玩家ID')
        return
    user_id = context.args[0]
    if not user_id.isdigit():
        update.message.reply_text('玩家ID必须为数字')
        return
    try:
        update.message.reply_photo(pjsk_process(user_id, False, diff, server))
    except Exception as e:
        update.message.reply_text('出了点毛病，可能是没找着')


@send_typing_action
def gacha(update, context):
    if len(context.args) == 0:
        currentgacha = getcurrentgacha()['id']
    else:
        currentgacha = context.args[0]
    try:
        update.message.reply_photo(fakegacha(currentgacha, 10, False, True))
    except Exception as e:
        update.message.reply_text('出了点毛病，可能是没这个池子')


def main():
    updater = Updater(token=config['bot']['token'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    dispatcher.add_handler(CommandHandler('gacha', gacha, run_async=True))
    dispatcher.add_handler(CommandHandler('profile', partial(profile, server='jp'), run_async=True))
    dispatcher.add_handler(CommandHandler('experts', partial(process, diff='expert', server='jp'), run_async=True))
    dispatcher.add_handler(CommandHandler('masters', partial(process, diff='master', server='jp'), run_async=True))
    # dispatcher.add_handler(CommandHandler('enprofile', partial(profile, server='en'), run_async=True))
    # dispatcher.add_handler(CommandHandler('twprofile', partial(profile, server='tw'), run_async=True))
    # dispatcher.add_handler(CommandHandler('krprofile', partial(profile, server='kr'), run_async=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
