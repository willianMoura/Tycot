from control_bot import control
from keyboard import keyboard
from decorators import *
import sql
import telepot
import random

try:
	from bs4 import BeautifulSoup
except:
	print('Precisa install BeautifulSoup4\npip install beautifulsoup4')
import urllib.request as urllib

class command_user(control, keyboard):
	def enviarAlerta(self, chat_id, data, usuario):
		chat = chat_id
		msg = data
		user = usuario
		return self.bot.sendMessage(chat, parse_mode='HTML', text='<i>sua marcação {}</i>'.format(usuario), reply_to_message_id=msg)

	def buscarAlerta(self, user_id):
		if self.chat_type=='private':
			return self.bot.sendMessage(self.UserID,('Utilização incorreta. Favor enviar no grupo'))
		else:
			if(sql.procurar(self.chat_id,user_id)=='erro ao procurar'):
				print('usuário não existe')
			else:
				resultado = sql.procurar(self.chat_id,user_id)
				if resultado[3] == 1:
					first_name = resultado[0]
					msg = int(self.msg['message_id'])
					return self.bot.forwardMessage(user_id, self.chat_id, msg), self.bot.sendMessage(user_id,('Mensagem enviada no grupo {}').format(self.msg['chat']['title']), reply_markup=self.keyboard_alert(self.chat_id, msg, first_name))
	
	@log
	def start(self):
		if self.chat_type != 'private':
			return self.bot.sendMessage(
				self.chat_id,
				('Oi! Por favor, inicie uma conversa privada.'
				' Bots funcionam apenas desta forma.'),
				reply_markup=self.start_key(),
				reply_to_message_id=self.msg_id

			)

	@decor_info_ajuda
	def info(self):
		if self.chat_type == 'private':
			return self.bot.sendMessage(
				chat_id=self.chat_id,
				parse_mode='HTML',
				text='''<b>ID INFO</b>\n<code>NOME</code>: {0}\n<code>ID</code>: {1}'''.format(
					self.user,
					self.UserID
				),
				reply_to_message_id=self.msg_id
			)
		else:
			info_chat = self.msg['chat']['title']
			return self.bot.sendMessage(
				chat_id=self.UserID,
				parse_mode='HTML',
				text='<b>ID INFO</b>\n<code>NOME</code>: {0}\n<code>ID</code>: {1}\n<code>NOME DO GRUPO</code>: {2}\n<code>ID GROUP</code>: {3}'.format(
					self.user,
					self.UserID,
					info_chat,
					self.chat_id
				),
				reply_to_message_id=self.msg_id
			)

	@decor_info_ajuda
	def ajuda(self):
		return self.bot.sendMessage(
			self.UserID, ('''
			Olá, sou o Tycot!
			Segue minha lista de comandos:
			/alert -> ativar serviço de alertas
			/alertoff -> desativar serviço de alertas
			/info -> informações do grupo
			/link -> link do grupo
			/regras -> regras do grupo
			/leave -> sair do grupo
			/verifybook -> verifica o ultimo livro do packtpub
			'''),
			reply_to_message_id=self.msg_id
		)

	def aceitarAlerta(self):
		if self.chat_type == 'private':
			return self.bot.sendMessage(
				self.UserID, ('Utilização incorreta. Favor enviar no grupo')
			)
		else:
			if(sql.procurar(self.chat_id, self.UserID) == 'erro ao procurar'):
				retornoIns = sql.inserir(self.chat_id, self.user, self.UserID)
				print(retornoIns)
				if(retornoIns == 'erro'):
					print('erro ao inserir')
				retorno = sql.alerta(self.chat_id, self.UserID)
				if(retorno == 'erro'):
					print('erro ao inserir alerta')
				return self.bot.sendMessage(self.UserID, ('Usuário adicionado. Alerta ativado'))
			else:
				retorno = sql.alerta(self.chat_id, self.UserID)
				if(retorno == 'erro'):
					print('erro ao inserir alerta')
				else:
					return self.bot.sendMessage(self.UserID, ('Alerta ativado'))

	def remAlerta(self):
		if self.chat_type == 'private':
			return self.bot.sendMessage(
				self.UserID, ('Utilização incorreta. Favor enviar no grupo')
			)
		else:
			if(sql.procurar(self.chat_id, self.UserID) == 'erro ao procurar'):
				retornoIns = sql.inserir(self.chat_id, self.user, self.UserID)
				if(retornoIns == 'erro ao inserir'):
					print('erro ao remover')
				retorno = sql.remAlerta(self.chat_id, self.UserID)
				if(retorno == 'erro ao remover alerta'):
					print('erro ao remover alerta')
				return self.bot.sendMessage(
					self.UserID, ('Usuário adicionado. Alerta desativado'))
			else:
				retorno = sql.remAlerta(self.chat_id, self.UserID)
				if(retorno == 'erro ao remover alerta'):
					print('erro ao remover alerta')
				else:
					return self.bot.sendMessage(self.UserID, ('Alerta desativado'))

	def goodbye(self):
		if('left_chat_member' in self.msg):
			user_first_name = str(self.msg['left_chat_member']['first_name'])
			self.bot.sendMessage(
				self.chat_id,
				"Tchau, {}".format(user_first_name)
			)
			self.bot.sendVideo(
				self.chat_id,
				'https://media.giphy.com/media/l3V0gpbjA6fD7ym9W/giphy.mp4'
			)
			return True

	def regras(self):
		if self.chat_type == 'private':
			return self.bot.sendMessage(
				self.UserID, ('Utilização incorreta. Favor enviar no grupo')
			)
		else:
			try:
				with open('.tmp/regras' + str(self.chat_id) + '.txt', 'r') as rules:
					rules = rules.read()
			except FileNotFoundError:
				rules = 'Sem regras!'
			return self.bot.sendMessage(self.chat_id, rules, parse_mode='HTML')

	def new_member(self):
		user_first_name = self.msg['new_chat_member']['first_name']
		id_user = self.msg['new_chat_member']['id']
		get_bot_name = self.bot.getMe()
		bot_name = get_bot_name['first_name']

		if(user_first_name == bot_name):
			self.bot.sendMessage(self.chat_id, 'Olá, sou o Tycot!')
			sql.criar_table(self.chat_id)
		else:
			try:
				retorno = sql.inserir(self.chat_id, user_first_name, id_user)
				if(retorno == 'erro ao inserir'):
					print('erro ao inserir')
				with open('.tmp/welcome' + str(self.chat_id) + '.txt', 'r') as welcome:
					welcome = welcome.read()
					welcome = welcome.replace('$name', user_first_name)
					self.bot.sendMessage(self.chat_id, welcome)
			except FileNotFoundError:
				self.bot.sendMessage(
					chat_id=self.chat_id,
					parse_mode='Markdown',
					text='Seja Bem Vindo(a) [{0}](https://telegram.me/{1}/)'.format(
						user_first_name,
						id_user
					),
					disable_web_page_preview=True,
					reply_to_message_id=self.msg_id
				)
		return True

	def link(self):
		if self.chat_type == 'private':
			return self.bot.sendMessage(
				self.UserID, ('Utilização incorreta. Favor enviar no grupo')
			)
		else:
			info_chat = self.msg['chat']['title']
			try:
				with open('.tmp/link' + str(self.chat_id) + '.txt', 'r') as link_:
					link_tg = link_.read()
			except FileNotFoundError:
				link_tg = 'Sem link!'
			link_msg = '<a href="{}">{}</a>'.format(link_tg, info_chat)
			return self.bot.sendMessage(self.chat_id, link_msg, parse_mode='HTML',reply_to_message_id=self.msg_id)

	def book_info(self):
		packt = 'https://www.packtpub.com/packt/offers/free-learning'
		page = urllib.urlopen(packt)
		soup = BeautifulSoup(page,"html.parser")

		book_url_image = soup.find(
			'img',
			class_='bookimage imagecache imagecache-dotd_main_image'
		)
		book_title = soup.find('div', class_='dotd-title').h2.text
		return book_url_image.attrs['src'], book_title.strip(), packt

	def verify_book(self):
		book_url_image, book_title, packt_url = self.book_info()
		self.bot.sendPhoto(
			self.UserID,
			'http:{}'.format(book_url_image),
			'{}:{}'.format(
				book_title,
				packt_url
			)
		)

class command_admin(control, keyboard):
	@admin
	def ban(self):
		first_name_reply = self.msg['reply_to_message']['from']['first_name']
		reply_id = self.msg['reply_to_message']['from']['id']
		id_msg_replyed = self.msg['reply_to_message']['message_id']
		if reply_id not in self.get_admin_list(user_reply=True):
			self.bot.kickChatMember(self.chat_id, reply_id)
			self.bot.sendMessage(
				self.chat_id,
				'<b>{}</b> foi retirado do grupo.'.format(first_name_reply),
				parse_mode='HTML',
				reply_to_message_id=id_msg_replyed
			)
			try:
				sql.delete(self.chat_id, reply_id)
			except BaseException:
				pass
			return True
		else:
			return self.bot.sendMessage(
				self.chat_id,
				'<b>{}</b> é um dos administradores. Não posso remover administradores.'.format(first_name_reply),
				parse_mode='HTML',
				reply_to_message_id=self.msg_id
			)

	@admin
	@log
	def warn(self):
		first_name_reply = self.msg['reply_to_message']['from']['first_name']
		user_reply_id = self.msg['reply_to_message']['from']['id']
		id_msg_replyed = self.msg['reply_to_message']['message_id']

		if user_reply_id not in self.get_admin_list(user_reply=True):
			try:
				advs = int(sql.procurar(self.chat_id, user_reply_id)[1])
			except BaseException:
				sql.inserir(self.chat_id, first_name_reply, user_reply_id)
				advs = int(sql.procurar(self.chat_id, user_reply_id)[1])
			sql.advertir(self.chat_id, user_reply_id)
			self.bot.sendMessage(
				self.chat_id,
				'{user} <b>has been warned</b> ({advs}/3).'.format(
					user=first_name_reply,
					advs=advs + 1
				),
				parse_mode='HTML',
				reply_markup=self.keyboard_warn(user_reply_id),
				reply_to_message_id=id_msg_replyed
			)
			if advs >= 3:
				self.bot.sendMessage(
					self.chat_id,
					'<b>{}</b> expulso por atingir o limite de advertencias.'.format(first_name_reply),
					parse_mode='HTML',
					reply_to_message_id=id_msg_replyed
				)
				self.bot.kickChatMember(self.chat_id, user_reply_id)
				sql.delete(self.chat_id, user_reply_id)
			else:
				pass
		else:
			return self.bot.sendMessage(
				self.chat_id,
				'<b>{}</b> é um dos administradores. Não posso advertir administradores.'.format(first_name_reply),
				parse_mode='HTML')

	@admin
	@log
	def unwarn(self, data=None):
		user_reply_id = data
		if not(data is not None):
			first_name_reply = self.msg['reply_to_message']['from']['first_name']
			user_reply_id = self.msg['reply_to_message']['from']['id']
			id_msg_replyed = self.msg['reply_to_message']['message_id']

		try:
			advs = int(sql.procurar(self.chat_id, user_reply_id)[1])
		except BaseException:
			pass

		if data is not None:
			int(data)
			sql.desadvertir(self.chat_id, data, advs)
		else:
			if user_reply_id not in self.get_admin_list(user_reply=True):
				self.bot.sendMessage(
					self.chat_id,
					'<b>{}</b> perdoado.'.format(first_name_reply),
					parse_mode='HTML',
					reply_to_message_id=id_msg_replyed
				)
				sql.desadvertir(self.chat_id, user_reply_id, advs)
			else:
				return self.bot.sendMessage(
					self.chat_id, 'Administradores não possuem advertências.',
					reply_to_message_id=self.msg_id
				)

	@admin
	@log
	def deflink(self, text):
		text = text.replace("/deflink ", "")
		with open('.tmp/link' + str(self.chat_id) + '.txt', 'w') as link_:
			link_.write(text)
		return self.bot.sendMessage(
			self.chat_id,
			'O novo link foi salvou com sucesso!',
			reply_to_message_id=self.msg_id
		)

	@admin
	@log
	def add(self):
		sql.criar_table(self.chat_id)
		if sql.procurar(
				self.chat_id,
				self.msg['from']['id']) == 'erro ao procurar':
			sql.inserir(
				self.chat_id,
				self.msg['from']['first_name'],
				self.msg['from']['id'])
		else:
			pass

	@admin
	@log
	def defregras(self, text):
		text = text.replace("/defregras ", "")
		with open('.tmp/regras' + str(self.chat_id) + '.txt', 'w') as rules:
			rules.write(text)

		return self.bot.sendMessage(
			self.chat_id,
			'As novas regras foram salvas com sucesso!',
			reply_to_message_id=self.msg_id
		)

	@admin
	@log
	def defwelcome(self, text):
		text = text.replace("/welcome ", "")
		with open('.tmp/welcome' + str(self.chat_id) + '.txt', 'w') as welcome:
			welcome.write(text)
		return self.bot.sendMessage(
			self.chat_id,
			'As mensagens de boas-vindas foram alteradas com sucesso!',
			reply_to_message_id=self.msg_id
		)
