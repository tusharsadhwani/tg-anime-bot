start_msg = """_Nico nico nii~!_
I can help you get information and airing notificaitons of anime that you follow.
Start by using the /anime command!

_The bot is currently in Alpha Testing phase._
Report any bugs to @e\_to\_the\_i\_pie or @WeirdIndianBoi."""

help_msg = """_Nico nico nii~!_
I can help you get information and airing notifications of anime that you follow. Start by using the /anime command!

Here's the commands list~
/anime - Search Anime
/help - Get this help message
/info - Get Anime info
/schedule - Get Airing Schedule, alias /airing
/show\_watchlist - Show watchlist, alias /show
/add\_to\_watchlist - Search and add anime to watchlist, alias /add
/remove\_from\_watchlist - Removes an anime from watchlist, alias /remove
/clear\_watchlist - Clear watchlist, alias /clear
/notif\_off - Turn off watchlist notifications
/notif\_on - Turn on watchlist notifications

*Make me admin to delete spammy messages from the bot!* ^-^"""

def airing_time(time):

	days, hours, minutes = range(3)

	day_count = time // 86400
	hour_count = (time // 3600) % 24
	minute_count = (time // 60) % 60

	days = '' if not day_count else f'{day_count} day ' if day_count == 1 else  f'{day_count} days '
	hours = '' if not (hour_count or day_count) else  f'{hour_count} hour and ' if hour_count == 1 else  f'{hour_count} hours and '
	minutes = f'{minute_count} minute' if minute_count == 1 else f'{minute_count} minutes'

	return ([days, hours, minutes])