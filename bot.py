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
def id_checker(message):
    cur = bdconnect.cursor()
    cur.execute('SELECT id_user FROM users;')         # Вытаскиваем ID для проверки регистрации
    ids = cur.fetchall()
    id_flag = bool()
    for id in ids:
        if id[0] == int(message.chat.id):             # Проверка регистрации
            id_flag = True
            break
        else:
            id_flag = False
    return id_flag

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if id_checker(message):
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Lighthouse! \n"
                                          "Вы уже зарегистрированы!\n\n Для продолжения просто напишите /menu")
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться C;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(message.chat.id, "Howdy! Добро пожаловать в Lighthouse! \n"
                                          "Для начала нужно пройти регистрацию", reply_markup=button)


@bot.message_handler(commands=['menu'])
def send_(message):
    if id_checker(message):
        buttons = types.InlineKeyboardMarkup()
        searchButton = types.InlineKeyboardButton(text="Лист медиа", callback_data="list0/length0//type0")
        finishedButton = types.InlineKeyboardButton(text="Посмотрел", callback_data="watched0/length0/finish")
        wishButton = types.InlineKeyboardButton(text="Желаемое", callback_data="watched0/length0/wish")
        subButton = types.InlineKeyboardButton(text="Подписки(UC)", callback_data="sub")
        suggestButton = types.InlineKeyboardButton(text="Предложить(UC)", callback_data="suggest")
        profileButton = types.InlineKeyboardButton(text="Профиль", callback_data="profile")
        buttons.add(searchButton, finishedButton, wishButton, subButton, suggestButton, profileButton)
        bot.send_message(message.chat.id, "Lighthouse menu\nДля поиска просто введите название", reply_markup=buttons)
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться С;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(message.chat.id, "Вы не можете использовать команду /menu без регистрации\n", reply_markup=button)

@bot.callback_query_handler(func=lambda call: True) #Обработчик для кнопок
def callback(call):
    cur = bdconnect.cursor()
    if call.data == "reg":
        if id_checker(call.message):                         # Если зарегистрирован
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id,
                             'Вы уже зарегистрированы в Lighthouse! =)\nВаш ID: {0}'.format(call.message.chat.id))
        else:                                                # Если не зарегистрирован
            cur.execute('INSERT INTO users (id_user, name, level, exp) '
                        'VALUES ({0}, \'{1}\', 1, 0);'.format(call.message.chat.id, call.message.chat.first_name))
            bdconnect.commit()
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id, 'Howdy! Добро пожаловать в Lighthouse! \n'
                                                   'Вы были успешно зарегистрированы!\n\nДля продолжения просто напишите /menu')
    if id_checker(call.message): #Проверка регистрации
        if call.data == "profile":
            cur.execute('SELECT * FROM users WHERE id_user = {0};'.format(call.message.chat.id))  # Вытаскиваем людей
            user = cur.fetchall()
            bot.send_message(call.message.chat.id, 'Профиль\n\nВаш ID: {0}\nИмя: {1}\nУровень: {2}\nОпыт: {3}'.format(user[0][0], user[0][1], user[0][2], user[0][3]))
        elif "list" in call.data:
            splitCall = call.data.split("/")
            page = splitCall[0].replace("list", "")
            length = splitCall[1].replace("length", "")
            search = splitCall[2]
            type = splitCall[3].replace("type", "")
            limit = 5
            last = int()
            i = limit * int(page) #Номер продукта на странице
            if i == 0:
                if type == "0":
                    cur.execute('SELECT * FROM media JOIN types ON types.id_type = media.id_type '
                                'WHERE UPPER(media.name) LIKE UPPER(\'%{0}%\')'.format(search))  # Вытаскиваем медиа
                else:
                    cur.execute('SELECT * FROM media JOIN types ON types.id_type = media.id_type '
                                'WHERE UPPER(media.name) LIKE UPPER(\'%{0}%\') AND media.id_type = {1}'.format(search, type))  # Вытаскиваем медиа
                media = cur.fetchall()
                length = len(media)

            #cur.execute('SELECT * FROM media JOIN types on types.id_type = media.id_type ORDER BY id_media LIMIT {0} OFFSET {1}'.format(limit, i))  # Вытаскиваем медиа
            if type == "0":
                cur.execute('SELECT media.id_media, types.name, media.name, authors.name, release_date, jenre, rating_average '
                            'FROM media JOIN types ON types.id_type = media.id_type JOIN authors ON authors.id_author = media.id_author '
                            'WHERE UPPER(media.name) LIKE UPPER(\'%{2}%\') ORDER BY id_media LIMIT {0} OFFSET {1}'.format(limit, i, search))  # Вытаскиваем медиа
            else:
                cur.execute('SELECT media.id_media, types.name, media.name, authors.name, release_date, jenre, rating_average '
                            'FROM media JOIN types ON types.id_type = media.id_type JOIN authors ON authors.id_author = media.id_author '
                            'WHERE UPPER(media.name) LIKE UPPER(\'%{2}%\') '
                            'AND media.id_type = {3} ORDER BY id_media LIMIT {0} OFFSET {1}'.format(limit, i, search, type))  # Вытаскиваем медиа
            media = cur.fetchall()
            if len(media) == 0:
                bot.send_message(call.message.chat.id, "Ничего не найдено :с")
            else:
                for item in media:
                    line = str()
                    line += str(i+1)
                    line += "\nРаздел:              " + item[1]
                    line += "\nНазвание:        " + item[2]
                    line += "\nАвтор:                " + item[3]
                    line += "\nДата выхода:  " + item[4]
                    line += "\nЖанр:                 " + item[5]
                    line += "\nОценка:             " + "(UC)" + "% одобрений"
                    line += "\n_______________________________"
                    i += 1
                    buttons = types.InlineKeyboardMarkup()
                    selectButton = types.InlineKeyboardButton(text="Выбрать", callback_data="select{0}".format(item[0]))
                    if i == (limit * int(page)) + limit and i != int(length):
                        nextButton = types.InlineKeyboardButton(text="Следующие {0}". format(limit),
                                                                callback_data="search{0}/length{1}".format(int(page)+1, length))
                        buttons.add(selectButton, nextButton)
                        bot.send_message(call.message.chat.id, line, reply_markup=buttons)
                    else:
                        buttons.add(selectButton)
                        bot.send_message(call.message.chat.id, line, reply_markup=buttons)

        elif "select" in call.data:
            mediaId = call.data.replace("select", "")
            #cur.execute('SELECT * FROM media JOIN types ON types.id_type = media.id_type WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            cur.execute('SELECT id_media, types.name, media.name, authors.name, release_date, jenre, rating_average, media.description '
                        'FROM media JOIN types ON types.id_type = media.id_type JOIN authors ON authors.id_author = media.id_author '
                        'WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            media = cur.fetchall()
            line = str()
            line += "\nРаздел:              " + media[0][1]
            line += "\nНазвание:        " + media[0][2]
            line += "\nАвтор:                " + media[0][3]
            line += "\nДата выхода:  " + media[0][4]
            line += "\nЖанр:                 " + media[0][5]
            line += "\nОценка:             " + "(UD)" + "% одобрений"
            line += "\n_______________________________"
            line += "\n" + media[0][7]
            #TODO: сделать проверку есть ли у пользователя выбранный продукт чтобы выводить соответствующие кнопки (и строки)
            cur.execute('SELECT * FROM finished_list WHERE id_user = {0} AND id_media = {1}'.format(call.message.chat.id, mediaId))  # Для проверки наличия медиа в законченном
            mediaChecker = cur.fetchall()
            if len(mediaChecker) == 0:
                buttons = types.InlineKeyboardMarkup()
                addWishButton = types.InlineKeyboardButton(text="Посмотрю!", callback_data="add{0}/wish/null".format(mediaId))
                addFinishedButton = types.InlineKeyboardButton(text="Посмотрел!", callback_data="add{0}/finish/null".format(mediaId))
                buttons.add(addWishButton, addFinishedButton)
                bot.send_message(call.message.chat.id, line, reply_markup=buttons)
            elif mediaChecker[0][0]==None:
                buttons = types.InlineKeyboardMarkup()
                deleteWishButton = types.InlineKeyboardButton(text="Не посмотрю!", callback_data="delete{0}".format(mediaId))
                addFinishedButton = types.InlineKeyboardButton(text="Посмотрел!", callback_data="add{0}/finish/null".format(mediaId))
                buttons.add(deleteWishButton, addFinishedButton)
                bot.send_message(call.message.chat.id, line, reply_markup=buttons)
            elif mediaChecker[0][0]!=None:
                buttons = types.InlineKeyboardMarkup()
                addFinishedButton = types.InlineKeyboardButton(text="Изменить оценку!", callback_data="add{0}/finish/null".format(mediaId))
                deleteFinishedButton = types.InlineKeyboardButton(text="Не посмотрел!", callback_data="delete{0}".format(mediaId))
                buttons.add(deleteFinishedButton)
                bot.send_message(call.message.chat.id, line, reply_markup=buttons)

        elif "add" in call.data:
            splitCall = call.data.split("/")
            mediaId = splitCall[0].replace("add", "")
            status = splitCall[1]
            rate = splitCall[2]
            cur.execute('SELECT media.name FROM media JOIN types ON types.id_type = media.id_type WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            media = cur.fetchall()
            cur.execute('SELECT * FROM finished_list WHERE id_user = {0} AND id_media = {1}'.format(call.message.chat.id, mediaId))  # Для проверки наличия медиа в законченном
            mediaChecker = cur.fetchall()
            # TODO изменение рейтинга медиа
            if status == "finish" and rate == "null":
                buttons = types.InlineKeyboardMarkup()
                ratedyes = types.InlineKeyboardButton(text="Рекомендую С:",
                                                      callback_data="add{0}/finish/1".format(mediaId))
                ratedno = types.InlineKeyboardButton(text="Не рекомендую :С",
                                                     callback_data="add{0}/finish/0".format(mediaId))
                buttons.add(ratedyes, ratedno)
                if len(mediaChecker) == 0:  # продукта нет в списке >добавить
                    bot.send_message(call.message.chat.id, "Вы рекомендуете этот продукт?", reply_markup=buttons)
                else:
                    bot.send_message(call.message.chat.id, "Решили изменить оценку?\nВы рекомендуете этот продукт?", reply_markup=buttons)

            elif status == "wish":
                if len(mediaChecker) == 0:  # продукта нет в списке >добавить
                    cur.execute('INSERT INTO finished_list (id_user, id_media, name_media) '
                                'VALUES ({0}, {1}, \'{2}\');'.format(call.message.chat.id, mediaId, media[0][0]))
                    bdconnect.commit()
                    bot.send_message(call.message.chat.id, "Продукт успешно добавлен в список желаемого")  # TODO LVL
                else:
                    bot.send_message(call.message.chat.id, "Вы уже добавили продукт в список желаемого")
            elif status == "finish" and rate != "null":
                if len(mediaChecker) == 0:  # продукта нет в списке >добавить
                    cur.execute('INSERT INTO finished_list (id_user, id_media, name_media, rating)'
                                'VALUES ({0}, {1}, \'{2}\', {3});'.format(call.message.chat.id, mediaId, media[0][0], rate))
                    bdconnect.commit()
                    bot.send_message(call.message.chat.id, "Продукт успешно добавлен в список законченного")  # TODO LVL
                else:
                    cur.execute('UPDATE finished_list SET rating = {0} WHERE id_user = {1} AND id_media = {2}'.format(rate, call.message.chat.id,mediaId))  # Для проверки наличия медиа в законченном
                    bdconnect.commit()
                    bot.send_message(call.message.chat.id, "Продукт успешно добавлен в список законченного")  # TODO LVL

        elif "delete" in call.data:
            mediaId = call.data.replace("delete", "")
            cur.execute('SELECT * FROM finished_list WHERE id_user = {0} AND id_media = {1}'.format(call.message.chat.id, mediaId))  # Для проверки наличия медиа в законченном
            mediaChecker = cur.fetchall()
            if len(mediaChecker) != 0:  # продукта нет в списке >добавить
                cur.execute('DELETE FROM finished_list WHERE id_user = {0} AND id_media = {1}'.format(call.message.chat.id, mediaId))
                bdconnect.commit()
                bot.send_message(call.message.chat.id, "Продукт был удален из вашего списка")  # TODO LVL
                # TODO изменение рейтинга медиа
            else:
                bot.send_message(call.message.chat.id, "Продукт уже удален из вашего списка")  # TODO LVL

        elif "watched" in call.data:
            splitCall = call.data.split("/")
            page = splitCall[0].replace("watched", "")
            length = splitCall[1].replace("length", "")
            status = splitCall[2]
            limit = 5
            last = int()
            i = limit * int(page) #Номер продукта на странице
            if i == 0:
                cur.execute('SELECT * FROM finished_list JOIN media ON finished_list.id_media = media.id_media WHERE id_user = {0}'.format(call.message.chat.id))  # Вытаскиваем медиа
                media = cur.fetchall()
                length = len(media)
            if status == "finish":
                cur.execute('SELECT id_finished, id_user, media.id_media, name_media, rating, description, release_date, jenre, rating_average, types.name '
                            'FROM finished_list JOIN media ON finished_list.id_media = media.id_media JOIN types ON types.id_type = media.id_type '
                            'WHERE id_user = {0} AND rating IS NOT NULL ORDER BY id_finished LIMIT {1} OFFSET {2}'.format(call.message.chat.id, limit, i))  # Вытаскиваем медиа
            elif status == "wish":
                cur.execute('SELECT id_finished, id_user, media.id_media, name_media, rating, description, release_date, jenre, rating_average, types.name '
                            'FROM finished_list JOIN media ON finished_list.id_media = media.id_media JOIN types ON types.id_type = media.id_type '
                            'WHERE id_user = {0} AND rating IS NULL ORDER BY id_finished LIMIT {1} OFFSET {2}'.format(call.message.chat.id, limit, i))  # Вытаскиваем медиа

            media = cur.fetchall()
            for item in media:
                rate = str()
                if (item[4]) == 1:
                    rate = "Да"
                elif (item[4]) == 0:
                    rate = "Нет"
                line = str()        #TODO коммент
                line += str(i+1)
                line += "\nРаздел:              " + str(item[9])
                line += "\nНазвание:        " + item[3]
                line += "\nДата выхода:  " + item[6]
                line += "\nЖанр:                 " + item[7]
                line += "\nОценка:             " + "(UD)" + "% одобрений"
                if status == "finish":
                    line += "\nВаша оценка:  " + rate
                line += "\n_______________________________"
                i += 1
                buttons = types.InlineKeyboardMarkup()
                selectButton = types.InlineKeyboardButton(text="Выбрать", callback_data="select{0}".format(item[2]))
                if i == (limit * int(page)) + limit and i != int(length):
                    nextButton = types.InlineKeyboardButton(text="Следующие {0}". format(limit),
                                                            callback_data="watched{0}/length{1}/{2}".format(int(page)+1, length, status))
                    buttons.add(selectButton, nextButton)
                    bot.send_message(call.message.chat.id, line, reply_markup=buttons)
                else:
                    buttons.add(selectButton)
                    bot.send_message(call.message.chat.id, line, reply_markup=buttons)

            # cur.execute('SELECT media.name FROM media JOIN types ON types.id_type = media.id_type WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            # media = cur.fetchall()
            # cur.execute('INSERT INTO finished_list (id_user, id_media, name_media, rating, commentary) '
            #             'VALUES ({0}, {1}, \'{2}\', 0, \'(UD)\');'.format(call.message.chat.id, mediaId, media[0][0]))
            # bdconnect.commit()
            #
            # bot.send_message(call.message.chat.id, "Продукт успешно добавлен в список законченного")  # TODO LVL

        #>>упрощен в watched
        # elif "wish" in call.data:
        #     splitCall = call.data.split("/")
        #     page = splitCall[0].replace("wish", "")
        #     length = splitCall[1].replace("length", "")
        #     limit = 5
        #     last = int()
        #     i = limit * int(page) #Номер продукта на странице
        #     if i == 0:
        #         cur.execute('SELECT * FROM finished_list JOIN media ON finished_list.id_media = media.id_media WHERE id_user = {0}'.format(call.message.chat.id))  # Вытаскиваем медиа
        #         media = cur.fetchall()
        #         length = len(media)
        #     cur.execute('SELECT id_finished, id_user, media.id_media, name_media, rating, commentary, description, release_date, jenre, rating_average, types.name '
        #                 'FROM finished_list JOIN media ON finished_list.id_media = media.id_media JOIN types ON types.id_type = media.id_type '
        #                 'WHERE id_user = {0} AND rating IS NULL ORDER BY id_finished LIMIT {1} OFFSET {2}'.format(call.message.chat.id, limit, i))  # Вытаскиваем медиа
        #     media = cur.fetchall()
        #     for item in media:
        #         line = str()
        #         line += str(i+1)
        #         line += "\nРаздел:              " + str(item[9])
        #         line += "\nНазвание:        " + item[3]
        #         line += "\nДата выхода:  " + item[7]
        #         line += "\nЖанр:                 " + item[8]
        #         line += "\nОценка:             " + str(item[9]) + " из 5"
        #         line += "\nВаша оценка:  " + str(item[4]) + " из 5"
        #         line += "\n_______________________________"
        #         i += 1
        #         buttons = types.InlineKeyboardMarkup()
        #         selectButton = types.InlineKeyboardButton(text="Выбрать", callback_data="select{0}".format(item[2]))
        #         if i == (limit * int(page)) + limit and i != int(length):
        #             nextButton = types.InlineKeyboardButton(text="Следующие {0}". format(limit),
        #                                                     callback_data="wish{0}/length{1}".format(int(page)+1, length))
        #             buttons.add(selectButton, nextButton)
        #             bot.send_message(call.message.chat.id, line, reply_markup=buttons)
        #         else:
        #             buttons.add(selectButton)
        #             bot.send_message(call.message.chat.id, line, reply_markup=buttons)

            # cur.execute('SELECT media.name FROM media JOIN types ON types.id_type = media.id_type WHERE id_media = {0}'.format(mediaId))  # Вытаскиваем медиа
            # media = cur.fetchall()
            # cur.execute('INSERT INTO finished_list (id_user, id_media, name_media, rating, commentary) '
            #             'VALUES ({0}, {1}, \'{2}\', 0, \'(UD)\');'.format(call.message.chat.id, mediaId, media[0][0]))
            # bdconnect.commit()
            #
            # bot.send_message(call.message.chat.id, "Продукт успешно добавлен в список законченного")  # TODO LVL

        #IDEA!!
        # call.data = "profile"
        # callback(call)
    else:
        button = types.InlineKeyboardMarkup()
        reg_button = types.InlineKeyboardButton(text="Нажмите на кнопку чтобы зарегистрироваться С;", callback_data="reg")
        button.add(reg_button)
        bot.send_message(call.message.chat.id, "Вы не зарегистрированы \n", reply_markup=button)


@bot.message_handler(func=lambda message: True)
def mesasge_answer(message):
    search = message.text
    buttons = types.InlineKeyboardMarkup()
    nofilter_button = types.InlineKeyboardButton(text="Без фильтра", callback_data="list0/length0/{0}/type0".format(search))
    gamesf_button = types.InlineKeyboardButton(text="Игры", callback_data="list0/length0/{0}/type1".format(search))
    filmsf_button = types.InlineKeyboardButton(text="Фильмы", callback_data="list0/length0/{0}/type2".format(search))
    buttons.add(nofilter_button, gamesf_button, filmsf_button)
    bot.send_message(message.chat.id, "Выберите фильтр", reply_markup=buttons)

    #bot.reply_to(message, 'Не спамь ;)')

if __name__ == '__main__':
    bot.polling(none_stop=True)