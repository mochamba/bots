import telebot, time

from telebot import types
#Загружаем список шуток
f=open('Data/jokes.txt', 'r', encoding='UTF-8')
jokes=f.read().split('\n')
adres=@ElenaRibak (https://t.me/ElenaRibak)
# Создаем экземпляр бота
bot = telebot.TeleBot('')
# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
for i in jokes:
    bot.send_message(adres, i.split())
    time.sleep(60)

# Запускаем бота
bot.polling(none_stop=True, interval=0)