def load_db():
	user_dict = {}
	notif_dict = {}
	user_db = open('user_dict.db', 'rb')
	notif_db = open('notif_dict.db', 'rb')
	try:
		obj = pickle.load(user_db)
		if obj:
			user_dict = obj
	except:
		pass
	try:
		obj = pickle.load(notif_db)
		if obj:
			notif_dict = obj
	except:
		pass
	user_db.close()
	notif_db.close()

	return user_dict, notif_dict
