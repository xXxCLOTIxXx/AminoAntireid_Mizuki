try:import amino
except:
	import os
	os.system('pip install amino.py')
	import amino
	os.system('cls')


try:from rich.console import Console
except:
	import os
	os.system('pip install rich')
	from rich.console import Console
	os.system('cls')

try:import pyfiglet
except:
	import os
	os.system('pip install pyfiglet')
	import pyfiglet
	os.system('cls')

try:import requests
except:
	os.system('pip install requests')
	import requests
	os.system('cls')

import time
from threading import Thread
#========================================== Библиотеки

#Имя бота - Мизуки (Mizuki)

#====================почта и пароль========================
gmail = 'Пароль'
password = 'Почта'
#==========================================================

#Авторизация и старт бота------------------------------------
console = Console()
client = amino.Client()
console.print("[magenta]" + pyfiglet.figlet_format("Anti Reid Amino", font="slant") + "[/magenta]")
console.print("[bold cyan] made by CLOTI (Xsarz)[/] [bold yellow]Telegram: t.me/DXsarz    GITHUB: https://github.com/xXxCLOTIxXx[/]")
if requests.get("https://aminoapps.com").status_code != 200:
	console.print("\n[bold red]Амино сервера не отвечают. Попробуйте запустить позже[/]");exit()
try:
	client.login(email=gmail, password=password)
	console.print(f"\n[bold green]Бот успешно авторизован под аккаунтом {gmail} !\n[/]")
except Exception as error:
	if str(error) == 'Expecting value: line 1 column 1 (char 0)':
		console.print(f"\n[bold red]С вашего ip поступает слишком много запросов, подождите 5-10 минут[/]");exit()
	else:
		console.print(f"\n[bold red]Не удалось авторизовать бота\n\n {error}[/]");exit()

#------------------------------------------------------------
reid_users = {}
baned = []
join_users = []
admins = []
#------------------------------------------------------------


def clear(num):
	global reid_users
	while True:
		time.sleep(num)
		reid_users = {}
#чистка переменной с обычными рейд аргументами


def clear2(num):
	global reid_users
	while True:
		time.sleep(num)
		join_users = [] 
#чистка переменной с рейдом "Join-leave"


def restart_socket(num):
	while True:
		time.sleep(num)
		try:
			client.close()
			client.run_amino_socket()
			console.print(f"\n[bold green]Сокет успешно перезапущен![/]\n")
		except Exception as error:
			console.print(f"\n[bold red]Ошибка перезагрузки сокета\n {error}[/]\n")
#перезагрузка сокета (он почему-то вырубается через время, баг библиотеки)


def clear_chat(num, chatId, sub_client):
	try:
		messages = sub_client.get_chat_messages(chatId=chatId, size=num).json
		for i in range(num):
			mess_id = messages[i]['messageId']
			sub_client.delete_message(chatId=chatId, messageId=mess_id, asStaff=True, reason='Чистка чата')
	except:
		sub_client.send_message(chatId=chatId, message='Произошла ошибка при попытке очистить чат❌')
#чистка чата----------------------------------------------------------


Thread(target=clear, args=(3,)).start()
Thread(target=clear2, args=(4,)).start()
Thread(target=restart_socket, args=(90,)).start()

#запуск в потоки чистки и перезагрузку сокета


def timer(sub_client, chatId, author_n):
	global reid_users, baned
	for userId in reid_users.keys():
		reid_user = reid_users[userId]
		if len(reid_user)>=3:
			if userId in baned:
				pass
			else:
				try:
					sub_client.kick(userId=userId, chatId=chatId, allowRejoin=False)
					kick_ = 'OK.'
				except:
					kick_ = 'NO.'
				try:
					sub_client.ban(userId=userId, reason='Подозрение в рейде')
					ban_ = 'OK.'
					baned.append(userId)
				except Exception as ex:
					print(ex)
					ban_ = 'NO.'
				try:
					sub_client.edit_chat(chatId=chatId, viewOnly=True)
					edit_ = 'OK.'
				except:
					edit_ = 'NO.'
				try:
					sub_client.send_message(chatId=chatId, message=f'📣{author_n} подозревается в рейдерстве.\n\n🛑Попытка забанить: {ban_}\n\n🛑Попытка кикнуть из чата: {kick_}\n\n🛑Попытка включить режим "Только просмотр": {edit_}')
				except:
					console.print(f"\n[bold red]Не удалось Отправить сообщение о рейде[/]\n")

#Функция для проверки пользователей на рейд обычными сообщениями (5-10 сек на срабатывание)


@client.event("on_text_message")
def text_handler(data):
	global admins
	sub_client = amino.SubClient(comId=data.comId, profile=client.profile)
	chatId = data.message.chatId
	author_n = data.message.author.nickname
	author_u = data.message.author.userId
	ct = data.message.content
	content = ct.lower().split(" ")
	reid_args = {author_u: [ct]}
	if author_u in reid_users.keys():
		reid_users[author_u].append(ct)
	else:
		reid_users[author_u] = []
		reid_users[author_u].append(ct)
	Thread(target=timer, args=(sub_client,chatId, author_n)).start()
	try:
		if content[0][0] == '/':
			if content[0][1:] == "чистка":
				admins_json = sub_client.get_all_users(type='leaders', size=100).json['userProfileList']
				for i in range(len(admins_json)):
					admins.append(admins_json[i]['uid'])
				if author_u in admins:
					try:
						num = int(content[1])
						try:
							Thread(target=clear_chat, args=(num,chatId,sub_client)).start()
						except:
							sub_client.send_message(chatId=chatId, message='Произошла ошибка❌')
					except IndexError:
						sub_client.send_message(chatId=chatId, message='Укажите коло-во сообщений для удаления')
					except:
						sub_client.send_message(chatId=chatId, message='Укажите цифру')
	except Exception as ex:
		print(ex)


#Получение и вывод информации в консоль (+ запуск функции timer)

@client.event("on_avatar_chat_start")
def reid_109(data):
	global baned
	author_u = data.message.author.userId
	if author_u in baned:
		pass
	else:
		sub_client = amino.SubClient(comId=data.comId, profile=client.profile)
		chatId = data.message.chatId
		author_n = data.message.author.nickname
		try:
			sub_client.kick(userId=author_u, chatId=chatId, allowRejoin=False)
			kick_ = 'OK.'
		except:
			kick_ = 'NO.'
		try:
			sub_client.ban(userId=author_u, reason='Подозрение в рейде типом 109')
			ban_ = 'OK.'
			baned.append(author_u)
		except:
			ban_ = 'NO.'
		try:
			sub_client.edit_chat(chatId=chatId, viewOnly=True)
			edit_ = 'OK.'
		except:
			edit_ = 'NO.'
		try:
			sub_client.send_message(chatId=chatId, message=f'📣{author_n} подозревается в рейдерстве типом 109.\n\n🛑Попытка забанить: {ban_}\n\n🛑Попытка кикнуть из чата: {kick_}\n\n🛑Попытка включить режим "Только просмотр": {edit_}')
		except:
			console.print(f"\n[bold red]Не удалось Отправить сообщение о рейде[/]\n")
#Функция для бана пользователей, отправляющих сообщение с 109 типом (+- 3 сек на срабатывание)


@client.event("on_group_member_join")
def reid_join_leave(data):
	global join_users
	author_u = data.message.author.userId
	if author_u in join_users:
		if author_u in baned:
			pass
		else:
			sub_client = amino.SubClient(comId=data.comId, profile=client.profile)
			chatId = data.message.chatId
			author_n = data.message.author.nickname
			try:
				sub_client.kick(userId=author_u, chatId=chatId, allowRejoin=False)
				kick_ = 'OK.'
			except:
				kick_ = 'NO.'
			try:
				sub_client.ban(userId=author_u, reason='Подозрение в рейде типом 109')
				ban_ = 'OK.'
				baned.append(author_u)
			except:
				ban_ = 'NO.'
			try:
				sub_client.edit_chat(chatId=chatId, viewOnly=True)
				edit_ = 'OK.'
			except:
				edit_ = 'NO.'
			try:
				sub_client.send_message(chatId=chatId, message=f'📣{author_n} подозревается в рейдерстве типом join-leave.\n\n🛑Попытка забанить: {ban_}\n\n🛑Попытка кикнуть из чата: {kick_}\n\n🛑Попытка включить режим "Только просмотр": {edit_}')
			except:
				console.print(f"\n[bold red]Не удалось Отправить сообщение о рейде[/]\n")
	else:
		join_users.append(author_u)
#функция для бана рейдеров "join-leave"


"""
Важно!!!
Сокеты Amino.py конфликтуют с сокетами samino. У вас на устройстве не должна быть установлена библиотека samino, иначе бот не будет работать
"""