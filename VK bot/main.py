import time
import requests
import random
import vk_api
import json
token = ""
urlcon  = 'https://api.vk.com/method/messages.getConversations?v=5.52&count=200&access_token='+token


class Teacher:
    def __init__(self):
        self.questions = []
        self.id = ''


class Student:
    def __init__(self):
        self.questions = []
        self.teachers = []
        self.id = ''


class Server:
    def __init__(self, api_token, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)  # добавили токен
        self.vk_api = self.vk.get_api()

    def send_msg(self, send_id, message, keyb):
        return self.vk_api.messages.send(peer_id=send_id,
                                         message=message,
                                         random_id=random.randint(10**4, 10**6),
                                         keyboard=open(keyb, "r", encoding="UTF-8").read())


serv = Server(token)
users = 0
tcur = 0
scur = 0
while True:
    r = requests.get(urlcon).json()
    for i in r['response']['items']:
        try:
          if (i['conversation']['unread_count']!=0):
            urlmark = 'https://api.vk.com/method/messages.markAsRead?v=5.52&'+str(i['conversation']['last_message_id'])+'&peer_id='+str(i['conversation']['peer']['id'])+'&access_token='+token
            print(urlmark)
            print(requests.get(urlmark).json())
            if i['last_message']['text'] == 'Я - учитель':
                users += 1
                t = Teacher()
                t.id = i['conversation']['peer']['id']
                serv.send_msg(t.id, 'Вы - учитель', "teacher.json")
            elif i['last_message']['text'] == 'Я - ученик':
                users += 1
                s = Student()
                s.id = i['conversation']['peer']['id']
                serv.send_msg(s.id, 'Вы - ученик', "student.json")
            print(users)
            if users == 2:
                if t.id == i['conversation']['peer']['id']:
                    if i['last_message']['text'] == 'Задать вопрос':
                        tcur = 1
                    elif i['last_message']['text'] == 'Проверить ответы':
                        if len(t.questions) != 0:
                            for p in t.questions:
                                print(p)
                                if p[1] != '':
                                    serv.send_msg(t.id, 'Ваш вопрос: ' + p[0], "teacher.json")
                                    serv.send_msg(t.id, 'Ответ ученика: ' + p[1], "teacher.json")
                    elif tcur == 1:
                        tcur = 0
                        t.questions.append([i['last_message']['text'], ''])
                        serv.send_msg(t.id, "Мы отправили ваш вопрос ученикам", "teacher.json")
                else:
                    if i['last_message']['text'] == 'Получить вопрос':
                        if len(t.questions) == 0:
                            serv.send_msg(s.id, "У нас нет новых вопросов", "student.json")
                        elif scur == 0:
                            scur = 1
                            s.questions.append([i['last_message']['text'], ''])
                            serv.send_msg(s.id, t.questions[0][0], "student.json")
                    elif scur == 1:
                        scur = 0
                        t.questions[0][1] = (i['last_message']['text'])
        except:
          continue
    time.sleep(1)
