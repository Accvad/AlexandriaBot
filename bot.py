import config
import telebot
import psycopg2
from telebot import types

bot = telebot.TeleBot(config.token)

bdconnect = psycopg2.connect(
    dbname="LighthouseBotDB",
    user="Accvad",
    password="wololo",
    host="127.0.0.1",
    port="5432"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    cur = bdconnect.cursor()
    cur.execute('SELECT id_user FROM users;')         # Вытаскиваем ID для проверки регистрации
    ids = cur.fetchall()
    id_flag = bool()
    for id in ids:
        if id[0] == int (message.chat.id):            # Проверка регистрации
            chosenId = id[0]
            id_flag = True
            break
        else:
            id_flag = False
    if id_flag == False:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="reg")
        button.add(reg_button)
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n"
                                          "На данный момент реализована только регистрация, "
                                          "но разработка уже перешла в каждодневную. "
                                          "Нажмите на кнопку чтобы зарегистрироваться", reply_markup=button)
    else:
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Альфа-версию Lighthouse! \n"
                                          "На данный момент реализована только регистрация, "
                                          "но разработка уже перешла в каждодневную. \n"
                                          "Вы уже были зарегистрированы, так что для продолжения просто напишите /menu")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "reg":
            cur = bdconnect.cursor()
            cur.execute('SELECT id_user FROM users;')       # Вытаскиваем ID для проверки регистрации
            ids = cur.fetchall()
            id_flag = bool()
            for id in ids:
                if id[0] == int(call.message.chat.id):      # Проверка регистрации
                    chosenId = id[0]
                    id_flag = True
                    break
                else:
                    id_flag = False
            if id_flag == True:                             # Если зарегистрирован
                bot.send_message(call.message.chat.id,
                                 'Вы уже зарегистрированы в Lighthouse! =)\nВаш ID: {0}'.format(chosenId))
            else:  # Если не зарегестрирован
                cur.execute('INSERT INTO users (id_user) VALUES ({0});'.format(call.message.chat.id))
                bdconnect.commit()
                bot.send_message(call.message.chat.id, 'Вы были успешно зарегистрированы!\n\n')
    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")

@bot.message_handler(func=lambda message: True)
def repeat_all_messages(message):
    bot.reply_to(message, 'Не спамь ;)')

if __name__ == '__main__':
    bot.polling(none_stop=True)