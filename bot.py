from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
SEARCH, CHOICE, ACTIONS, AIRING, BUTTONS, WATCHLIST, REMOVE, GENRE_INPUT, GENRE_CHOICE = range(9)
conv_handler = None

def load_databases():
	from load_databases import load_databases
	user_dict, notif_dict = load_databases()

def start(bot, update):
	from misc import start_msg
	bot.send_message(chat_id = update.message.chat_id, text = start_msg, parse_mode = 'Markdown')

def help(bot, update):
	bot.send_message(chat_id = update.message.chat_id, text = help_msg, reply_to_message_id = update.message.message_id, parse_mode = "Markdown")

def anime(bot, update, user_data):
	user_data['first_message']=update.message.message_id
	command = update.message.text.split()[0].lstrip('/')
	if '@' in command:
		index = command.index('@')
		command = command[:index]

	if command in ['add_to_watchlist', 'add']:
		user_data['choice'] = 'add_to_watchlist'

	elif command == 'info':
		user_data['choice'] = 'info'

	elif command in ['airing', 'schedule']:
		user_data['choice'] = 'airing_schedule'

	query = ' '.join(update.message.text.split()[1:])
	if query:
		user_data['name'] = query
		user_data['method']='D'
		return anime_search(bot, update, user_data)

	user_data['prev_message'] = bot.send_message(chat_id = update.message.chat_id, text = "Type anime name", reply_to_message_id = update.message.message_id)
	return SEARCH

def anime_search(bot, update, user_data):
	try:
		bot.delete_message(chat_id = update.message.chat_id, message_id = user_data['prev_message'].message_id)
	except:
		pass
	from api import anime_query

	if 'name' not in user_data.keys():
		user_data['name'] = update.message.text
	anime_name = user_data['name']

	if 'curr_page' not in user_data.keys():
		user_data['curr_page'] = 1
	curr_page = user_data['curr_page']

	if 'sent_message' not in user_data.keys():
		user_data['sent_message'] = bot.send_message(chat_id = update.message.chat_id, text = "Searching, wait a second...", reply_to_message_id = update.message.message_id)

	sent_message = user_data['sent_message']

	data, anime_list, anime_dict, eng_dict = anime_query(anime_name, curr_page)

	if not data['data']['Page']['media']:
		bot.edit_message_text(chat_id = update.message.chat_id, text = "No Anime found, try again.", message_id = sent_message.message_id)
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return done(bot, update, user_data)

	user_data['anime_dict'] = anime_dict
	user_data['anime_list'] = anime_list

	if update.message:
		user_data['user_id'] = update.message.from_user.id

	if len(anime_dict.keys()) == 1:
		user_data['anime_id'] = anime_dict[anime_list[0]]
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = sent_message.message_id)
		except:
			pass
		if 'choice' in user_data.keys() and user_data['choice'] in ['add_to_watchlist', 'info', 'airing_schedule']:
			return intermediate(bot, update, user_data)
		else:
			keyboard = [[InlineKeyboardButton("Anime Info", callback_data = 'info')],
						[InlineKeyboardButton("Add to Watchlist", callback_data = 'add_to_watchlist')],
						[InlineKeyboardButton("Airing Schedule", callback_data = 'airing_schedule')]
					   ]

			markup = InlineKeyboardMarkup(keyboard)
			bot.send_message(chat_id = update.message.chat_id, text = "Enter your choice:", reply_to_message_id =user_data['first_message'], reply_markup = markup, parse_mode = 'Markdown')
			return BUTTONS

	msg = (f"Choose Anime:\n\n")

	for index, anime in enumerate(anime_dict, 1):
		if eng_dict[anime]:
			msg += (f"/{index}. {eng_dict[anime]}\n  ({anime})\n")
		else:
			msg += (f"/{index}. {anime}\n")

	if data['data']['Page']['pageInfo']['hasNextPage']:
		inline_button = InlineKeyboardMarkup([[InlineKeyboardButton("More...", callback_data = 'search')]])
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id, reply_markup = inline_button)
	else:
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id)
	try:
		if 'method' not in user_data.keys():
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
	except:
		pass
	return CHOICE

def anime_choice(bot, update, user_data):
	msg = update.message.text
	choice = int(msg[1])

	if choice > len(user_data['anime_list']):
		bot.send_message(chat_id = update.message.chat_id, text = "Invalid choice, try again.", reply_to_message_id = update.message.message_id)
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return CHOICE

	else:
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = user_data['sent_message'].message_id)
		except:
			pass
		anime_dict = user_data['anime_dict']
		anime_list = user_data['anime_list']
		anime_id = anime_dict[anime_list[choice - 1]]
		user_data['anime_id'] = anime_id

		if 'choice' in user_data.keys() and user_data['choice'] in ['add_to_watchlist', 'info', 'airing_schedule']:
			return intermediate(bot, update, user_data)

		keyboard = [[InlineKeyboardButton("Anime Info", callback_data = 'info')],
					[InlineKeyboardButton("Add to Watchlist", callback_data = 'add_to_watchlist')],
					[InlineKeyboardButton("Airing Schedule", callback_data = 'airing_schedule')]
				   ]

		markup = InlineKeyboardMarkup(keyboard)

		bot.send_message(chat_id = update.message.chat_id, text = "Enter your choice:", reply_to_message_id =user_data['first_message'], reply_markup = markup, parse_mode = 'Markdown')
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return BUTTONS

def buttons(bot, update, user_data):
	query = update.callback_query
	choice = query.data
	user_id = update.callback_query.from_user.id

	if choice == 'genre_choice':
		sent_message = bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		user_data['sent_message'] = query.message
		user_data['curr_page'] += 1
		return genre_choice(bot, update, user_data)
	
	if choice == 'search':
		sent_message = bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		user_data['sent_message'] = query.message
		user_data['curr_page'] += 1
		return anime_search(bot, update, user_data)
	
	anime_id = user_data['anime_id']

	if choice == 'info':
		bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		msg, site_url, trailer_url = anime_info(bot, update, anime_id)

		if trailer_url:
			info_buttons = [[InlineKeyboardButton("Trailer", url = trailer_url),
							 InlineKeyboardButton("Full Anime Page", url = site_url)]]
		else:
			info_buttons = [[InlineKeyboardButton("Full Anime Page", url = site_url)]]

		markup = InlineKeyboardMarkup(info_buttons)

		bot.edit_message_text(text = msg,
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id,
							  reply_markup = markup,
							  parse_mode = "Markdown")

	elif choice == 'add_to_watchlist':
		bot.edit_message_text(text = watchlist(user_id, anime_id),
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

	elif choice == 'airing_schedule':
		bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		bot.edit_message_text(text = anime_airing(bot, update, anime_id),
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

	return done(bot, update, user_data, query)

def watchlist(user_id, anime_id):
	if user_id in user_dict.keys():
		if anime_id in user_dict[user_id]:
			return "You already have this anime in your watchlist!"

		user_dict[user_id].append(anime_id)
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		return "Anime added Successfully!"

	user_dict[user_id] = [anime_id]
	user_db = open('user_dict.db', 'wb')
	pickle.dump(user_dict, user_db)
	user_db.close()
	return "Anime added Successfully!"

def anime_info(bot, update, anime_id):
	from api import info
	return info(anime_id)

def anime_airing(bot, update, anime_id):
	from api import airing
	return airing(anime_id)

def intermediate(bot, update, user_data):
	user_id = update.message.from_user.id
	anime_id = user_data['anime_id']

	choice = user_data['choice']

	if choice == 'info':
		msg, site_url, trailer_url = anime_info(bot, update, anime_id)

		if trailer_url:
			info_buttons = [[InlineKeyboardButton("Trailer", url = trailer_url),
							 InlineKeyboardButton("Full Anime Page", url = site_url)]]
		else:
			info_buttons = [[InlineKeyboardButton("Full Anime Page", url = site_url)]]

		markup = InlineKeyboardMarkup(info_buttons)

		bot.send_message(text = msg,
						 chat_id = update.message.chat_id,
						 reply_to_message_id=user_data['first_message'],
						 reply_markup = markup,
						 parse_mode = "Markdown")

	elif choice == 'add_to_watchlist':
		bot.send_message(text = watchlist(user_id, anime_id),
						 chat_id = update.message.chat_id,
						 reply_to_message_id=user_data['first_message'])

	elif choice == 'airing_schedule':
		bot.send_message(text = anime_airing(bot, update, anime_id),
						 chat_id = update.message.chat_id,
						 reply_to_message_id=user_data['first_message'])

	if 'direct' not in user_data.keys():
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
	return done(bot, update, user_data)

def done(bot, update, user_data, query = None):
	#if query:
	#	bot.send_message(chat_id = query.message.chat_id, text = "Convo ended.", reply_to_message_id = query.message.message_id)
	#else:
	#	bot.send_message(chat_id = update.message.chat_id, text = "Convo ended.", reply_to_message_id = update.message.message_id)
	user_data.clear()
	return conv_handler.END

def search(bot, update, user_data):
		user_data['com'] = update.message.message_id
		from api import show_watchlist
		from api import anime_title
		user_id = update.message.from_user.id
		msg = "Select which anime you would like to remove:\n"
		if user_id in user_dict.keys():
				for index, anime in enumerate(user_dict[user_id]):
					anime_name = show_watchlist(anime)
					msg += (f'/{index + 1}. {anime_name}\n')
				user_data['message2'] = bot.send_message(chat_id = update.message.chat_id, text = msg, reply_to_message_id = update.message.message_id, parse_mode='MARKDOWN')
				return REMOVE
		else:
			bot.send_message(chat_id = update.message.chat_id, text = "You don't seem to have a watchlist. Add something to your watchlist using the /anime function.", reply_to_message_id = update.message.message_id)
			return done(bot, update, user_data)

def remove(bot, update, user_data):
	bot.delete_message(chat_id = update.message.chat_id, message_id=user_data['message2'].message_id)
	command = update.message.text.split()[0].lstrip('/')
	if '@' in command:
		index = command.index('@')
		command = command[:index]
	command = int(command) - 1
	user_id = update.message.from_user.id
	if len(user_dict[user_id]) >= command:
		user_dict[user_id].remove(user_dict[user_id][command])
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		bot.send_message(chat_id=update.message.chat_id, text="Successfully removed.", reply_to_message_id=user_data['com'])
		bot.delete_message(chat_id = update.message.chat_id, message_id=update.message.message_id)
		return done(bot, update, user_data)
	else:
		return REMOVE

def genres(bot, update, user_data):
	user_data['com'] = update.message.message_id
	user_data['chat_id'] = update.message.chat_id
	msg = "Enter the genre of your choice:\n"
	user_data['genres'] = ["Action", "Adventure", "Comedy", "Drama", "Ecchi", "Fantasy", "Horror", 'Music', 'Mystery', 'Psychological', 'Romance', 'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural', 'Thriller']
	for index, gen in enumerate(user_data['genres'], 1):
		msg += f'/{index}. {gen}\n'
	user_data['message1'] = bot.send_message(chat_id = update.message.chat_id, text = msg)
	return GENRE_CHOICE

def genre_choice(bot, update, user_data):
	if 'cd' not in user_data.keys():
		try:
			bot.delete_message(chat_id=update.message.chat_id, message_id=user_data['message1'].message_id)
		except:
			pass
		user_data['cd']=update.message.text
		okimoutofvariables=user_data['cd']
		if '@' in okimoutofvariables:
			index = okimoutofvariables.index('@')
			okimoutofvariables = okimoutofvariables[1:index]
		else:
			okimoutofvariables = okimoutofvariables[1:]
		user_data['cd']=okimoutofvariables
	command = int(user_data['cd'])-1


	if 'curr_page' not in user_data.keys():
		user_data['curr_page'] = 1
	curr_page = user_data['curr_page']

	if 'sent_message' not in user_data.keys():
		user_data['sent_message'] = bot.send_message(chat_id = update.message.chat_id, text = "Searching, wait a second...", reply_to_message_id = update.message.message_id)

	sent_message = user_data['sent_message']
	#try:
		#bot.delete_message(chat_id = update.message.chat_id, message_id = user_data['prev_message'].message_id)
	#except:
		#pass
	from info_of_anime import genr

	genre_input=user_data['genres'][command]

	data, anime_list, anime_dict, eng_dict=genr(genre_input, curr_page)

	if 'curr_page' not in user_data.keys():
		user_data['curr_page'] = 1
	curr_page = user_data['curr_page']

	user_data['anime_dict'] = anime_dict
	user_data['anime_list'] = anime_list

	msg = (f"Choose Anime:\n\n")

	for index, anime in enumerate(anime_dict, 1):
		if eng_dict[anime]:
			msg += (f"/{index}. {eng_dict[anime]}\n  ({anime})\n")
		else:
			msg += (f"/{index}. {anime}\n")

	if data['data']['Page']['pageInfo']['hasNextPage']:
		inline_button = InlineKeyboardMarkup([[InlineKeyboardButton("More...", callback_data = 'genre_choice')]])
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id, reply_markup = inline_button)
	else:
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id)
	try:
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	except:
		pass
	return GENRE_INPUT

def genre_input(bot, update, user_data):
	try:
		bot.delete_message(chat_id=update.message.chat_id, message_id=user_data['sent_message'].message_id)
	except:
		pass
	command = update.message.text.split()[0].lstrip('/')
	if '@' in command:
		index = command.index('@')
		command = command[:index]
	command=int(command)-1
	anime_dict=user_data['anime_dict']
	anime_list=user_data['anime_list']
	anime_id = anime_dict[anime_list[command]]
	user_data['anime_id']=anime_id
	user_data['user_id']=update.message.from_user.id
	from api import info
	msg, site_url, trailer_url = info(anime_id)

	if trailer_url:
		info_buttons = [[InlineKeyboardButton("Trailer", url = trailer_url),
					InlineKeyboardButton("Full Anime Page", url = site_url)],[InlineKeyboardButton('Add to watchlist', callback_data='add_to_watchlist')]]
	else:
		info_buttons = [[InlineKeyboardButton("Full Anime Page", url = site_url)]]

	markup = InlineKeyboardMarkup(info_buttons)
	bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MARKDOWN', reply_to_message_id=user_data['com'], reply_markup=markup)
	try:
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	except:
		pass
	return done(bot, update, user_data)

def watchlist_commands(bot, update):
	bot.send_message(chat_id = update.message.chat_id, reply_to_message_id = update.message.message_id, text = """Here's the watchlist commands:

/show_watchlist - Show watchlist, alias /show
/add_to_watchlist - Search and add anime to watchlist, alias /add
/remove_from_watchlist - Removes an anime from watchlist, alias /remove
/clear_watchlist - Clear watchlist, alias /clear""")

def show_watchlist(bot, update):
		from api import show_watchlist
		user_id = update.message.from_user.id
		user_name = update.message.from_user.username
		user_name=user_name.replace('_','\_')


		msg = (f"Watch list for @{user_name}:\n\n")

		if user_id in user_dict.keys() and user_dict[user_id]:
				for index, anime in enumerate(user_dict[user_id]):
						anime_name = show_watchlist(anime)
						msg += (f'{index+1}. {anime_name}\n')
				bot.send_message(chat_id = update.message.chat_id, text = msg, reply_to_message_id = update.message.message_id, parse_mode='Markdown')
		else:
			bot.send_message(chat_id = update.message.chat_id, text = "You don't seem to have a watchlist. Add something to your watchlist using the /anime function.", reply_to_message_id = update.message.message_id)

		if user_id not in notif_dict.keys() or notif_dict[user_id] == 'off':
			bot.send_message(chat_id = update.message.chat_id, text = 'Btw, remember to turn /notif_on to get notifications.', reply_to_message_id = update.message.message_id)

def clear_watchlist(bot, update):
	user_id = update.message.from_user.id

	if user_id in user_dict.keys() and user_dict[user_id]:
		del user_dict[user_id]
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		bot.send_message(chat_id = update.message.chat_id, text = "Successfully cleared watchlist!", reply_to_message_id = update.message.message_id)
	else:
		bot.send_message(chat_id = update.message.chat_id, text = "Your watchlist is already empty...", reply_to_message_id = update.message.message_id)


def update_anime_list(bot, job):
	from notif import anime_query
	anime_list = anime_query(7200)
	return callback(bot, job, anime_list)
 
def airing_today(bot, update):
	from notif import anime_query, today
	anime_list = anime_query(86400)

	msg = 'Anime airing today are:\n'
	for anime in anime_list:
		text = today(anime)
		msg += f'\n{text}\n'
	bot.send_message(chat_id = update.message.chat_id, text = msg, parse_mode = "Markdown")


def callback(bot, update, anime_list):
	from notif import anime_notification
	
	for anime in anime_list:
		text = anime_notification(anime)

		from notif import timeUntilAiring
		if timeUntilAiring > 0:
			sleep(timeUntilAiring)
		for person in user_dict.keys():
			if anime in user_dict[person]:
							if person in notif_dict.keys() and notif_dict[person] == 'on':
								try:
									bot.send_message(chat_id = person, text = text)
									print(f"Sent message to {person} about anime {anime}:")
									print(user_dict[person])
								except:
									print("COULDN'T SEND NOTIFICATION!")

def notif_on(bot, update):
	user_id = update.message.from_user.id
	if user_id not in notif_dict.keys() or notif_dict[user_id] == 'off':
		notif_dict[user_id] = 'on'
		notif_db = open('notif_dict.db', 'wb')
		pickle.dump(notif_dict, notif_db)
		notif_db.close()

		try:
			bot.send_message(chat_id = update.message.from_user.id, text = "Your notifications have been enabled.")
		except:
			bot.send_message(chat_id = update.message.chat_id, text = "Your notifications have been enabled. Please [start me in pm](t.me/nico_anime_bot) to recieve notifications.", reply_to_message_id = update.message.message_id, parse_mode = "Markdown")
	
	elif notif_dict[user_id] == 'on':
		try:
			bot.send_message(chat_id = update.message.chat_id, text = "Your notifications are already enabled.", reply_to_message_id = update.message.message_id)
		except:
			bot.send_message(chat_id = update.message.chat_id, text = "Your notifications are already enabled. Please [start me in pm](t.me/nico_anime_bot) to recieve notifications.", reply_to_message_id = update.message.message_id, parse_mode = "Markdown")
	

def notif_off(bot, update):
	user_id = update.message.from_user.id
	if user_id not in notif_dict.keys():
		bot.send_message(chat_id = update.message.chat_id, text = "You aren't registered in our database yet.", reply_to_message_id = update.message.message_id)
	elif notif_dict[user_id] == 'on':
		notif_dict[user_id] = 'off'
		notif_db = open('notif_dict.db', 'wb')
		pickle.dump(notif_dict, notif_db)
		notif_db.close()
		bot.send_message(chat_id=update.message.chat_id, text="Your notifications have been disabled", reply_to_message_id = update.message.message_id)
	elif notif_dict[user_id] == 'off':
		bot.send_message(chat_id=update.message.chat_id, text="Your notifications are already disabled", reply_to_message_id = update.message.message_id)


def inlinequery(bot, update):
	query = update.inline_query.query
	from api import anime_query, info
	from info_of_anime import info_anime
	data, anime_list, anime_dict, eng_dict = anime_query(query, 1, 50)
	results = []

	for anime in anime_list:
		animes = anime_dict[anime]
		animeinfo = info_anime(animes)
		image = animeinfo['coverImage']['medium']
		status = animeinfo['status']
		status = status.capitalize()
		status = status.replace('_',' ')

		typee = animeinfo['type']
		typee = typee.capitalize()

		string = f'{status} {typee}'

		text, site_url, trailer_url = info(animes)
		if trailer_url:
			info_buttons = [[InlineKeyboardButton("Trailer", url = trailer_url),
					InlineKeyboardButton("Full Anime Page", url = site_url)]]
		else:
			info_buttons = [[InlineKeyboardButton("Full Anime Page", url = site_url)]]
		markup = InlineKeyboardMarkup(info_buttons)

		results.append(
			InlineQueryResultArticle(
				id = str(uuid4()),
				title = anime,
				input_message_content = (InputTextMessageContent(text, parse_mode='Markdown')),
				thumb_url = image,
				description = string,
				reply_markup=markup))
	update.inline_query.answer(results)

def main():
	from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, InlineQueryHandler,
							  ConversationHandler, RegexHandler, CallbackQueryHandler)
	import logging
	import pprint
	import pickle
	from time import sleep
	from uuid import uuid4

	pp = pprint.PrettyPrinter(indent = 4)

	logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	updater = Updater(token="TOKEN")

	dispatcher = updater.dispatcher
	j = updater.job_queue
	job = j.run_repeating(update_anime_list, interval = 3600, first = 0)

	global conv_handler
	conv_handler = ConversationHandler(
		entry_points = [CommandHandler(['anime', 'add', 'add_to_watchlist', 'info', 'airing', 'schedule'], anime, pass_user_data = True),
						CommandHandler(['remove_from_watchlist', 'remove'], search, pass_user_data = True),
						CommandHandler('genres',genres, pass_user_data = True)],

		states = {
			SEARCH: [MessageHandler(Filters.text,
									anime_search,
									pass_user_data = True)
					],
			CHOICE: [CommandHandler(['1', '2', '3', '4', '5'],
									anime_choice,
									pass_user_data = True),

					CallbackQueryHandler(buttons,
										  pass_user_data = True)
					],
			AIRING: [MessageHandler(Filters.text,
									anime_airing,
									pass_user_data = True)
					],
			BUTTONS: [CallbackQueryHandler(buttons,
										   pass_user_data = True)
					 ],
			WATCHLIST: [MessageHandler(Filters.text,
									   watchlist,
									   pass_user_data = True)
					   ],
			REMOVE: [CommandHandler([str(i) for i in range(1, 51)],
									remove, 
									pass_user_data = True)
					],
			GENRE_CHOICE: [CommandHandler([str(i) for i in range(1, 17)], 
						   genre_choice,
						   pass_user_data=True),

						   CallbackQueryHandler(buttons,
												pass_user_data = True)
						  ],
			GENRE_INPUT : [CommandHandler(['1','2','3','4','5'],
						   genre_input, 
						   pass_user_data = True), 
			
						   CallbackQueryHandler(buttons,
												pass_user_data = True)
						  ]
		},

		fallbacks = [RegexHandler('^Band hogya$', done, pass_user_data = True)],

		conversation_timeout = 20
	)

	start_handler = CommandHandler('start', start)
	help_handler = CommandHandler('help', help)
	watchlist_handler = CommandHandler("watchlist", watchlist_commands)
	showWatchlistHandler = CommandHandler(["show_watchlist", 'show'], show_watchlist)
	clearWatchlistHandler = CommandHandler(['clear_watchlist', 'clear'], clear_watchlist)
	airinghandler = CommandHandler('airing_today', airing_today)
	notif_on_handler = CommandHandler('notif_on', notif_on)
	notif_off_handler = CommandHandler('notif_off', notif_off)

	dispatcher.add_handler(conv_handler)
	dispatcher.add_handler(InlineQueryHandler(inlinequery))

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(watchlist_handler)
	dispatcher.add_handler(showWatchlistHandler)
	dispatcher.add_handler(clearWatchlistHandler)
	dispatcher.add_handler(airinghandler)
	dispatcher.add_handler(notif_on_handler)
	dispatcher.add_handler(notif_off_handler)
	
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()