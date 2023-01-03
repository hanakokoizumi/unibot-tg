from telegram.ext import Updater, CommandHandler
import yaml
import logging
from functools import partial
from modules.profile import pjsk_profile, pjsk_process
from modules.gacha import fakegacha, getcurrentgacha
from functools import wraps
from telegram import ChatAction, Update
from request import get
from db import sess, User
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


def bind(update, context, server):
    if len(context.args) == 0:
        update.message.reply_text('请提供玩家ID。')
        return
    userid = context.args[0]
    if not userid.isdigit():
        update.message.reply_text('玩家ID必须是数字。')
        return
    user = update.message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.from_user
    uid = user.id
    user = sess.query(User).filter(User.uid == uid, User.server == server).first()
    if user is not None:
        update.message.reply_text('你已经绑定过了。')
        return
    resp = get(f'https://api.nightcord.de/profile/{server}/{userid}/')
    if resp.status_code != 200:
        update.message.reply_text('玩家不存在。')
        return
    sess.add(User(
        uid=update.message.from_user.id,
        server=server,
        gid=userid
    ))
    sess.commit()
    update.message.reply_text('绑定成功！')


def unbind(update, context, server):
    user = update.message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.from_user
    uid = user.id
    user = sess.query(User).filter(User.uid == uid, User.server == server).first()
    if user is None:
        update.message.reply_text('你还没有绑定。')
        return
    sess.delete(user)
    sess.commit()
    update.message.reply_text('解绑成功！')


@send_typing_action
def profile(update: Update, context, server):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.reply_to_message.from_user
        uid = user.id
        db_user = sess.query(User).filter(User.uid == uid, User.server == server).first()
        if db_user:
            user_id = db_user.gid
        else:
            update.message.reply_text('该用户未绑定。')
            return
    elif len(context.args) == 0:
        user = update.message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.from_user
        db_user = sess.query(User).filter(User.uid == user.id, User.server == server).first()
        if db_user:
            user_id = db_user.gid
        else:
            update.message.reply_text('请使用 /bind 绑定，或指定玩家ID，或回复要查询的用户。')
            return
    else:
        user_id = context.args[0]
    if not user_id.isdigit():
        update.message.reply_text('玩家ID必须为数字')
        return
    update.message.reply_photo(pjsk_profile(user_id, False, server))


@send_typing_action
def process(update, context, diff, server):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.reply_to_message.from_user
        uid = user.id
        db_user = sess.query(User).filter(User.uid == uid, User.server == server).first()
        if db_user:
            user_id = db_user.gid
        else:
            update.message.reply_text('该用户未绑定。')
            return
    elif len(context.args) == 0:
        user = update.message.sender_chat if update.message.from_user.username == 'Channel_Bot' else update.message.from_user
        db_user = sess.query(User).filter(User.uid == user.id, User.server == server).first()
        if db_user:
            user_id = db_user.gid
        else:
            update.message.reply_text('请使用 /bind 绑定，或指定玩家ID，或回复要查询的用户。')
            return
    else:
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
        currentgacha = int(getcurrentgacha()['id'])
    else:
        currentgacha = context.args[0]
    gacha = fakegacha(currentgacha, 10, False, True)
    if isinstance(gacha, str):
        update.message.reply_text(gacha)
        return
    update.message.reply_photo(fakegacha(currentgacha, 10, False, True))


def main():
    updater = Updater(token=config['bot']['token'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    dispatcher.add_handler(CommandHandler('gacha', gacha, run_async=True))
    dispatcher.add_handler(CommandHandler('bind', partial(bind, server='jp'), run_async=True))
    dispatcher.add_handler(CommandHandler('unbind', partial(unbind, server='jp'), run_async=True))
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
