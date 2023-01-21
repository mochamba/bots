import telebot, time
import pymongo
from pymongo import MongoClient

bot = telebot.TeleBot('')
#Определяем класс для работы с базой
class DataBase:
    def __init__(self):
        cluster = MongoClient("")
        self.db=cluster.QuizBot
        self.users=self.db.Users
        self.questions=self.db.Questions
        self.questions_count=len(list(self.questions.find({})))
#Функция добавляющая нового пользователя в базу, если его там нет
    def get_user(self,chat_id):
        user=self.users.find_one({"chat_id":chat_id})
        if user is not None:
            return user
        # Структура словаря пользователи
        user ={
            "chat_id": chat_id,
            "is_passing" : False,
            "is_passed" :False,
            "question_index": None,
            "answers":[]
            }

        self.users.insert_one(user)

        return user

    #Функция обновляющая запись о пользователе
    def set_user(self,chat_id,update):
        self.users.update_one({"chat_id":chat_id},{"$set":update})


    #   Функция получающая вопрос по его номеру
    def get_questions(self,index):
        quest=self.questions.find_one({"id":index})
        return quest

db=DataBase()

#Действия бота по команде старт проверка пройденности викторины,создание клавиатуры
@bot.message_handler(commands=["start"])
def start(message):
    user=db.get_user(message.chat.id)
    if user["is_passed"]:
        bot.send_message(message.from_user.id,"Вы уже прошли эту викторину. ВТорой раз пройти нельзя")
        return

    if user["is_passing"]:
        return

    db.set_user(message.chat.id,{"question_index":0,"is_passing":True})
    user = db.get_user(message.chat.id)

    post=get_question_message(user)
    if post is not None:
        bot.send_message(message.from_user.id, post["text"],reply_markup=post["keyboard"])

# Функция позволяющая боту получать ответы на вопросы
@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def aswered(query):
    user= db.get_user(query.message.chat.id)

    if user is None or user["is_passed"] or not user["is_passing"]:
        return

    user["answers"].append(int(query.data.split('&')[1]))
    db.set_user(query.message.chat.id,{"answers":user["answers"]})

    post = get_answered_message(user)
    if post is not None:
            bot.edit_message_text(post["text"],query.message.chat.id,query.message.id,reply_markup=post["keyboard"])

# Функция вызывающаяся после нажатия кнопки далее
@bot.callback_query_handler(func=lambda query:query.data==("?next"))
def next(query):
    user=db.get_user(query.message.chat.id)

    if user["is_passed"] or not user["is_passing"]:
        return

    user["question_index"]+=1
    db.set_user(query.message.chat.id, {"question_index":user["question_index"]})

    post=get_question_message(user)
    if post is not None:
        bot.edit_message_text(post["text"],query.message.chat.id,query.message.id,reply_markup=post["keyboard"])

#Функция получающая текст вопроса
def get_question_message(user):
    if user["question_index"]==db.questions_count:
        count=0
        for question_index, question in enumerate(db.questions.find({})):
            if question["correct"]==user["answers"][question_index]:
                count+=1
        percents=round(100*count / db.questions_count)
        if percents<40:
            smile='😭'
        elif percents <90:
            smile='🙂'
        else :
            smile='🤩'

        text=f"Вы ответили правильно на {percents}% вопросов {smile}"
        db.set_user(user["chat_id"], {"is_passed":True,"is_passing":False})

        return{
            "text": text,
            "keyboard": None
                }
    #В переменную question записываем вопрос по номеру
    question=db.get_questions(user["question_index"])

    if question is None:
        return
    keyboard=telebot.types.InlineKeyboardMarkup()
    for answer_index,answer in enumerate(question["answers"]):
            keyboard.row(telebot.types.InlineKeyboardButton(f"{answer}",callback_data=f"?ans&{answer_index}"))

    # в переменную техт записываем форматированную строку содержащую номер и текст следующего вопроса
    text= f"Вопрос №{user['question_index'] + 1}\n{question['text']}\n"

    return{
            "text":text,
            "keyboard":keyboard
            }
def get_answered_message(user):
    question=db.get_questions(user["question_index"])

    # в переменную техт записываем форматированную строку содержащую номер и текст следующего вопроса
    text = f"Вопрос №{user['question_index'] + 1}\n{question['text']}\n"

# цикл проверяющий ответы на вопросы и пересоздающий клавиатуру
    for answer_index,answer in enumerate(question["answers"]):
        text+=f" {answer}"
        if answer_index==question["correct"]:
            text+="✅"
        elif answer_index==user['answers'][-1]:
            text+="❌"

        text+='\n'

    keyboard=telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton("Далее",callback_data="?next"))

    return {
        "text": text,
        "keyboard": keyboard
    }


bot.polling()