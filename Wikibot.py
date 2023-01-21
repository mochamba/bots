import telebot, wikipedia, re
# Создаем экземпляр бота
bot = telebot.TeleBot('')
wikipedia.set_lang("ru")
def getwiki(statia):
    try:
        ws=wikipedia.page(statia)
        # Получаем первую тысячу символов
        wikitext=ws.content[:1000]
        #Разделяеме на предложения
        wikimas=wikitext.split('.')
        #Отбрасываем все после последней точки
        wikimas=wikimas[:-1]
        #Пустаz Переменная для текста
        wikitext1=''
        #Проходим по массиву
        for x in wikimas:
            #Если не встречаем равно
            if not('==' in x):
                # длина строки больше 3
                if (len(x)>3):
                    wikitext1=wikitext1+x+'.'
                else:
                    break
                # Теперь при помощи регулярных выражений убираем разметку
                wikitext1 = re.sub('\([^()]*\)', '', wikitext1)
                wikitext1 = re.sub('\([^()]*\)', '', wikitext1)
                wikitext1 = re.sub('\{[^\{\}]*\}', '', wikitext1)
                # Возвращаем текстовую строку
        return wikitext1
    except Exception as  e:
                return ('В энциклопедии нет информации об этом')
# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Отправьте мне слово и я найду информацию в википедии )')
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, message.text+" это "+ getwiki(message.text))
# Запускаем бота
bot.polling(none_stop=True, interval=0)