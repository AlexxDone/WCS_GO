from commands.server import ServerCommand
from players.helpers import index_from_userid, playerinfo_from_userid, index_from_playerinfo, userid_from_index, edict_from_userid
from players.entity import Player
from filters.players import PlayerIter
from events import Event
from listeners.tick import Delay
from messages import Fade, FadeFlags
from colors import Color
from entities.constants import MoveType
from wcs import wcsgroup
from engines.precache import Model


@ServerCommand('wcs_setfx')
def _setfx_command(command):
	todo = str(command[1])
	userid = int(command[2])
	operator = str(command[3])
	amount = command[4]
	if len(command) > 5:
		time = float(command[5])
	else:
		time = 0
	player = Player(index_from_userid(userid))
		
	if todo == "blind":
		if operator == "=":
			if time == 0.0:
				time == 10000.0
			color = Color(255,255,255,int(amount))
			Fade(int(time), int(time),color,FadeFlags.PURGE).send(player.index)
	if todo == "flicker":
		if time == 0.0:
			time == 10000.0
		if int(amount) == 1:
			player.set_key_value_int("renderfx",13)
		if int(amount) == 0:
			player.set_key_value_int("renderfx",0)
		if time:
			Delay(time,removefx,("flicker",player,int(amount)))
			
	if todo == "1stclip":
		clip = player.get_weapon(is_filters="primary").clip
		if operator == "=":
			player.get_weapon(is_filters="primary").clip = int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(clip,))
		if operator == "+":
			player.get_weapon(is_filters="primary").clip += int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="primary").clip-int(amount),))
		if operator == "-":
			player.get_weapon(is_filters="primary").clip -= int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="primary").clip+int(amount),))				


	if todo == "2ndclip":
		clip = player.get_weapon(is_filters="secondary").clip
		if operator == "=":
			player.get_weapon(is_filters="secondary").clip = int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="secondary").set_clip,(clip,))
		if operator == "+":
			player.get_weapon(is_filters="secondary").clip += int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="secondary").clip-int(amount),))	
		if operator == "-":
			player.get_weapon(is_filters="secondary").clip -= int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="secondary").clip+int(amount),))					
				
	if todo == "1stammo":
		ammo = player.get_weapon(is_filters="primary").ammo
		if operator == "=":
			player.get_weapon(is_filters="primary").ammo = int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_ammo,(ammo,))			
		if operator == "+":
			player.get_weapon(is_filters="primary").ammo += int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="primary").ammo-int(amount),))
		if operator == "-":
			player.get_weapon(is_filters="primary").ammo -= int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="primary").set_clip,(player.get_weapon(is_filters="primary").ammo+int(amount),))				
				
	if todo == "2ndammo":
		ammo = player.get_weapon(is_filters="secondary").ammo
		if operator == "=":	
			player.get_weapon(is_filters="secondary").ammo = int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="secondary").set_ammo,(ammo,))		
		if operator == "+":
			player.get_weapon(is_filters="secondary").ammo += int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="secondary").set_ammo,(player.get_weapon(is_filters="primary").ammo-int(amount),))	
		if operator == "-":
			player.get_weapon(is_filters="secondary").ammo -= int(amount)
			if time:
				Delay(time,player.get_weapon(is_filters="secondary").set_ammo,(player.get_weapon(is_filters="primary").ammo+int(amount),))
				
	if todo == "invisp":
		old_color = player.color
		if operator == "=":
			old_invisp = float(player.color.a)/2.55
			amount = float(amount)*2.55
			amount = 255-amount
			player.color = Color(old_color[0],old_color[1],old_color[2], int(amount))
			if time:
				old_invisp = float(old_invisp)*2.55 - float(amount)
				Delay(time, removefx, ('invisp', player, old_invisp))
		if operator == "-":
			old_invisp = float(player.color.a)/2.55
			amount = float(amount)*2.55
			if (player.color.a - int(amount)) <= 0:
				player.color = Color(old_color[0],old_color[1],old_color[2], 0)
			else:
				player.color = Color(old_color[0],old_color[1],old_color[2], old_color[3] - int(amount))
			if time:
				Delay(time, removefx, ('invisp', player, old_invisp))
		if operator == "+":
			old_invisp = float(player.color.a)/2.55
			amount = float(amount)*2.55
			if (player.color.a + int(amount)) >= 255:
				player.color = Color(old_color[0],old_color[1],old_color[2], 255)
			else:
				player.color = Color(old_color[0],old_color[1],old_color[2], old_color[3] + int(amount))
			if time:
				Delay(time, removefx, ('invisp', player, -old_invisp))
				
	if todo == "invis":
		old_color = player.color
		amount = int(amount)
		if operator == "=":
			old_invisp = player.color.a
			player.color = Color(old_color[0],old_color[1],old_color[2], int(amount))
			if time:
				old_invisp = old_invisp - amount
				Delay(time, removefx, ('invis', player, old_invisp))
		if operator == "-":
			old_invisp = player.color.a
			if (player.color.a - amount) <= 0:
				player.color = Color(old_color[0],old_color[1],old_color[2], 0)
			else:
				player.color = Color(old_color[0],old_color[1],old_color[2], old_color[3] - int(amount))
			if time:
				Delay(time, removefx, ('invis', player, old_invisp))
		if operator == "+":
			old_invisp = player.color.a
			amount = amount
			if (player.color.a + amount) >= 255:
				player.color = Color(old_color[0],old_color[1],old_color[2], 255)
			else:
				player.color = Color(old_color[0],old_color[1],old_color[2], old_color[3] + int(amount))
			if time:
				Delay(time, removefx, ('invis', player, -amount))				
			
	if todo == "longjump":
		longjump = wcsgroup.getUser(userid, 'longjump')
		if longjump != None:
			longjump = float(longjump)
		else:
			longjump = 1.0
		if operator == "=":
			wcsgroup.setUser(userid, 'longjump', amount)
			if time > 0:
				Delay(time, wcsgroup.setUser,(userid,'longjump',0))
		if operator == "+":
			wcsgroup.setUser(userid, 'longjump', longjump+float(amount))
			if time > 0:
				Delay(time, wcsgroup.setUser,(userid,'longjump',float(wcsgroup.getUser(userid,'longjump'))-float(amount)))
		if operator == "-":
			wcsgroup.setUser(userid, 'longjump', longjump-float(amount))
			if time > 0:
				Delay(time, wcsgroup.setUser,(userid,'longjump',float(wcsgroup.getUser(userid,'longjump'))+float(amount)))
				
	if todo == "speed":
		current_speed = player.speed
		if time:
			time = float(time)
		if operator == "=":
			oldspeed = player.speed
			player.speed = float(amount)
			dif = oldspeed - player.speed
			if time:
				Delay(time,removefx, ('speed',player,float(dif)))
		if operator == "+":
			player.speed += float(amount)
			if time:
				Delay(time, removefx, ('speed', player, -float(amount)))
		if operator == "-":
			player.speed -= float(amount)
			if time:
				Delay(time, removefx, ('speed', player, float(amount)))		

	if todo == 'jetpack':
		if operator == "=":
			player.set_jetpack(int(amount))
			if time:
				Delay(time, removefx, ('jetpack',player,amount))
		wcsgroup.setUser(player.userid,'jetpack',int(player.jetpack))
				
	if todo == 'gravity':
		old_grav = player.gravity
		if operator == "=":
			player.gravity = float(amount)
			if time:
				return_value = float(amount) - old_grav
				Delay(time, removefx, ('gravity', player, return_value))
		if operator == "-":
			player.gravity -= float(amount)
			if time:
				Delay(time, removefx, ('gravity',player,-amount))
		if operator == "+":
			player.gravity += float(amount)
			if time:
				Delay(time, removefx, ('gravity',player,amount)	)
		wcsgroup.setUser(player.userid,'gravity',player.gravity)

	if todo == 'health':
		old_health = player.health
		if operator == "=":
			player.health = int(round(float(amount)))
			if time:
				Delay(time, removefx, ('health',player,old_health))
		if operator == "-":
			player.health -= int(round(float(amount)))
			if time:
				Delay(time, removefx, ('health',player,-amount))
		if operator == "+":
			player.health += int(round(float(amount)))
			if time:
				Delay(time, removefx, ('health',player,amount))
	if todo == 'freeze':
		if operator == "=":
			if amount == "0":
				player.move_type = MoveType.WALK
			if amount == "1":
				player.move_type = MoveType.NONE
			if time:
				Delay(time,removefx, ('freeze',player,amount))
				
	if todo in "cash;money":
		if operator == "=":
			old_amount = player.cash
			old_amount = old_amount-int(amount)
			player.cash = int(amount)
			if time:
				Delay(time,removefx, ('cash',player,old_amount))
		if operator == "-":
			old_amount = player.cash
			player.cash -= int(amount)
			if time:
				Delay(time,removefx, ('cash',player,-amount))
		if operator == "+":
			old_amount = player.cash
			player.cash += int(amount)
			if time:
				Delay(time, removefx, ('cash',player,amount))
	if todo == "burn":
		if operator == "=":
			if int(amount) == 1:
				if time:
					if time == 0:
						time = 999
				else:
					time = 999
				player.ignite_lifetime(float(time))		
			else:
				player.ignite_lifetime(0)
	if todo == "god":
		if operator == "=":
			player.godmode = int(amount)
			if time:
				Delay(time,removefx, ('god',player,int(amount)))
				
	if todo == "disguise":
		if operator == "=":
			if int(amount) == 2:
				player.model = Model("models/player/custom_player/legacy/tm_leet_variantB.mdl")
			if int(amount) == 3:
				player.model = Model("models/player/custom_player/legacy/ctm_idf_variantC.mdl")
			if time:
				Delay(time,removefx,('disguise',player,amount))
	
		
def removefx(todo,player,amount):
	if todo == 'disguise':
		if int(amount) == 3:
			player.model = Model("models/player/custom_player/legacy/tm_leet_variantB.mdl")
		if int(amount) == 2:
			player.model = Model("models/player/custom_player/legacy/ctm_idf_variantC.mdl")
	if todo == "god":
		if int(amount) == 1:
			player.godmode = 0
		else:
			player.godmode = 1
	if todo == "invis":
		player.color = Color(player.color[0], player.color[1],player.color[2],player.color[3] + int(amount))
	if todo == "invisp":
		player.color = Color(player.color[0], player.color[1],player.color[2],player.color[3] + int(amount))
	if todo == "freeze":
		if amount == "1":
			player.move_type = MoveType.WALK
		else:
			player.move_type = MoveType.NONE
	if todo == 'speed':
		player.speed += float(amount)
	if todo == 'jetpack':
		player.set_jetpack(1-int(amount))
		wcsgroup.setUser(player.userid,'jetpack',int(player.jetpack))
	if todo == 'gravity':
		player.gravity -= float(amount)
		wcsgroup.setUser(player.userid,'gravity',player.gravity)
	if todo == 'health':
		player.health -= int(amount)
	if todo == 'cash':
		player.cash -= int(amount)
	if todo == 'flicker':
		if amount == 0:
			player.set_key_value_int("renderfx", 13)
		if amount == 1:
			player.set_key_value_int("renderfx", 0)
			
			
	if todo == "size":
		if operator == "=":
			old_size = player.get_property_float("m_flModelScale")
			player.set_property_float("m_flModelScale",float(amount))
			if time:
				Delay(time,player.set_property_float,("m_flModelScale",old_size))
		if operator == "+":
			player.set_property_float("m_flModelScale",player.get_property_float("m_flModelScale")+float(amount))
			if time:
				Delay(time, player.set_property_float,("m_flModelScale",player.get_property_float("m_flModelScale")-float(amount)))
		if operator == "-":
			player.set_property_float("m_flModelScale",player.get_property_float("m_flModelScale")-float(amount))
			if time:
				Delay(time, player.set_property_float,("m_flModelScale",player.get_property_float("m_flModelScale")+float(amount)))



