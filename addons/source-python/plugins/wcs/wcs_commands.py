from commands.server import ServerCommand
from players.entity import Player
from cvars import ConVar
from colors import Color
from engines.server import execute_server_command,queue_command_string
from listeners.tick import Repeat, Delay
from messages import SayText2
from events import Event
from entities.entity import Entity
from mathlib import Vector
from messages import Fade, FadeFlags
import wcs
from filters.players import PlayerIter
import core

poison_dict = {}
timed_dict = {}

for player in PlayerIter('all'):
	poison_dict[player.userid] = []
	timed_dict[player.userid] = []
	
# =============================================================================
# >> SERVER COMMANDS
# =============================================================================	

@ServerCommand('wcs')
def register(command):
	if len(command) >= 4:
		todo = str(command[1]).lower()
		userid = int(command[2])
		if todo == 'damage':
			v,q,w = int(command[3]) if int(command[3]) else None, int(command[5]) if len(command) >= 6 else False, str(command[6]) if len(command) == 7 else None
			damage(userid, str(command[4]), v, q, w)

		elif todo == 'spawn':
			if len(command) in (3,4):
				spawn(userid, int(command[3]) if len(command) == 4 else False)
				
		elif todo == 'strip':
			if len(command) == 3:
				strip(userid)

		elif todo == 'drop':
			if len(command) == 4:
				drop(userid, command[3])

		elif todo == 'push':
			if len(command) >= 4:
				push(userid, command[3], command[4] if len(command) >= 5 else 0, command[5] if len(command) == 6 else 0)

		elif todo == 'pushto':
			if len(command) == 5:
				pushto(userid, command[3], command[4])

		elif todo == 'gravity':
			if len(command) == 4:
				gravity(userid, command[3])

		elif todo == 'removeweapon':
			if len(command) == 4:
				removeWeapon(userid, command[3])

		elif todo == 'getviewplayer':
			if len(command) == 4:
				v = getViewPlayer(userid)
				ConVar(str(command[3])).set_string(str(v) if v is not None else "0")

		elif todo == 'getviewentity':
			if len(command) == 4:
				v = getViewEntity(userid)
				ConVar(str(command[3])).set_string(str(v)if v is not None else "0")

		elif todo == 'keyhint':
			keyHint(userid, ' '.join(map(str, args[3:])))

		elif todo == 'give':
			if len(command) == 4:
				give(userid, command[3])

		elif todo == 'fire':
			if len(command) >= 3:
				fire(userid, float(command[3]) if len(command) == 4 else 0.0)

		elif todo == 'extinguish':
			if len(command) == 3:
				extinguish(userid)

		elif todo == 'drug':
			if len(command) >= 3:
				drug(userid, float(command[3]) if len(command) >= 4 else 0)

		elif todo == 'drunk':
			if len(command) >= 3:
				drunk(userid, float(command[3]) if len(command) >= 4 else 0, int(command[4]) if len(command) == 5 else 155)

		elif todo == 'poison':
			if len(command) == 7:
				dealPoison(userid, int(command[3]), int(command[4]), float(command[5]))
				Delay(float(command[6]),remove_poison,(userid,))
		elif todo == 'timed_damage':
			if len(command) == 7:
				dealTimed(userid, int(command[3]),int(command[4]),float(command[5]))
				Delay(float(command[6]),remove_timed,(userid,))

		elif todo == 'changeteam':
			if len(command) == 4:
				changeTeam(userid, str(command[3]))

# =============================================================================
# >> EVENTS
# =============================================================================	
	
@Event('player_spawn')
def player_spawn(ev):
	userid = int(ev['userid'])
	remove_poison(userid)
	remove_timed(userid)
	player = Player.from_userid(ev['userid'])
	player.set_property_uchar('m_iDefaultFOV', 90)
	player.set_property_uchar('m_iFOV', 90)
	player.gravity = 1.0
	player.client_command('r_screenoverlay 0')
	
@Event('round_end')
def round_end(ev):
	for player in PlayerIter('all'):
		if player.userid in poison_dict:
			for timer in poison_dict[player.userid]:
				if valid_repeat(timer):
					timer.stop()
					poison_dict[player.userid] = []
		if player.userid in timed_dict:
			for timer in timed_dict[player.userid]:
				if valid_repeat(timer):
					timer.stop()
					timed_dict[player.userid] = []
				
@Event('player_activate')
def activate(ev):
	poison_dict[int(ev['userid'])] = []
	timed_dict[int(ev['userid'])] = []
	
# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================	
	
def dealTimed(userid, attacker, dmg, time):
	if userid not in timed_dict:
		timed_dict[userid] = []
	timed_repeat = Repeat(_timed_repeat,(userid,attacker,dmg))
	timed_dict[userid].append(timed_repeat)
	timed_repeat.start(time,execute_on_start=True)
	
def fade(userid, r,g,b,a,time):
	userid = int(userid)
	color = Color(r,g,b,a)
	Fade(int(time), int(time),color,FadeFlags.PURGE).send(Player.from_userid(userid).index)	

def strip(userid):
	userid = int(userid)
	player = Player.from_userid(userid)
	entity = Entity.create('player_weaponstrip')
	entity.call_input("Strip", activator=player)
	entity.remove()

def drop(userid, weapon):
	userid = int(userid)
	player = Player.from_userid(userid)
	if str(weapon) == "1":
		wpn = player.get_weapon(is_filters='primary')
		if wpn:
			player.drop_weapon(wpn)
	elif str(weapon) == "2":
		wpn = player.get_weapon(is_filters='secondary')
		if wpn:
			player.drop_weapon(wpn)
	else:
		if player.get_weapon(is_filters='secondary'):
			if player.get_weapon(is_filters='secondary').classname == weapon:
				player.drop_weapon(player.get_weapon(is_filters='secondary'))
		if player.get_weapon(is_filters='primary'):
			if player.get_weapon(is_filters='primary').classname == weapon:
				player.drop_weapon(player.get_weapon(is_filters='primary'))

def push(userid, xm, ym=0, zm=0):
	userid = int(userid)
	vec = Vector(float(xm),float(ym),float(zm))
	player = Player.from_userid(userid)
	player.set_property_vector("m_vecBaseVelocity", vec)


def pushto(userid, coord, force):
	userid = int(userid)
	coords = coord.split(",")
	vec = Vector(coords[0],coords[1],coords[2])
	player = Player(index_from_userid(userid))
	player.teleport(None, None, vec - player.origin)

def damage(victim, dmg, attacker=None, armor=False, weapon=None, solo=None):
	queue_command_string("wcs_dealdamage %s %s %s" % (victim,attacker,dmg))
	

def gravity(userid, value):
	userid = int(userid)
	Player.from_userid(userid).gravity = float(value)


def removeWeapon(userid, weapon):
	userid = int(userid)
	slot_weapon = weapon
	player = Player.from_userid(userid)
	if slot_weapon in "1;2;3;4;5":
		if slot_weapon == "1":
			weapon = player.get_weapon(is_filters='primary')
			if weapon != None:
				player.drop_weapon(weapon)
				weapon.remove()
		if slot_weapon == "2":
			weapon = player.get_weapon(is_filters='secondary')
			if weapon != None:
				player.drop_weapon(weapon)
				weapon.remove()
	else:
		for weapon in player.weapons():
			if weapon.classname == slot_weapon:
				player.drop_weapon(weapon)
				weapon.remove()
				
def getViewEntity(userid):
	userid = int(userid)
	player = Player.from_userid(userid)
	view_ent = player.get_view_entity()
	if view_ent:
		return view_ent.index
	else:
		return 0


def getViewPlayer(userid):
	userid = int(userid)
	player = Player.from_userid(userid)
	view_player = player.get_view_player()
	if view_player:
		return view_player.userid
	else:
		return 0


def keyHint(userid, text):
	userid = int(userid)
	if not len(text):
		return

	if str(userid).startswith('#'):
		userid = getUseridList(userid)

	elif not hasattr(userid, '__iter__'):
		userid = (userid, )

	es.usermsg('create', 'keyhint', 'KeyHintText')
	es.usermsg('write', 'byte', 'keyhint', 1)
	es.usermsg('write', 'string', 'keyhint', text)

	for user in userid:
		if es.exists('userid', user):
			es.usermsg('send', 'keyhint', user)

	es.usermsg('delete', 'keyhint')

def give(userid, entity):
	userid = int(userid)
	execute_server_command('es_give', '%s %s' % (userid, entity))

def fire(userid, time=0):
	userid = int(userid)
	if time == 0:
		time = 999
	Player.from_userid(userid).ignite_lifetime(float(time))

def extinguish(userid):
	userid = int(userid)
	Player.from_userid(userid).ignite_lifetime(0.0)

def drug(userid, time=0):
	userid = int(userid)
	delay = float(time)
	Player.from_userid(userid).client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')
	Delay(delay, remove_drug, (userid,))
	
def remove_drug(userid):
	Player.from_userid(userid).client_command('r_screenoverlay 0')


def drunk(userid, time=0, value=155):
	userid = int(userid)
	player = Player.from_userid(userid)
	player.set_property_uchar('m_iDefaultFOV', value)
	player.set_property_uchar('m_iFOV', value)
	if time:
		Delay(time, remove_drunk, (player,))

def remove_drunk(player):
	player.set_property_uchar('m_iDefaultFOV', 90)
	player.set_property_uchar('m_iFOV', 90)
	
def remove_poison(userid):
	if userid in poison_dict:
		for timer in poison_dict[userid]:
			if valid_repeat(timer):
				timer.stop()
				poison_dict[userid] = []
	
def remove_timed(userid):
	if userid in timed_dict:
		for timer in timed_dict[userid]:
			if valid_repeat(timer):
				timer.stop()
				timed_dict[userid] = []

def spawn(userid, force=False):
	userid = int(userid)
	Player.from_userid(userid).spawn(force)
	
	
def _timed_repeat(userid,attacker,dmg):
	damage(userid,dmg,attacker)
	print('test')

def dealPoison(userid, attacker, dmg, time):
	userid = int(userid)
	if userid not in poison_dict:
		poison_dict[userid] = []
	poison_repeat = Repeat(_poison_repeat,(userid,attacker,dmg))
	poison_dict[userid].append(poison_repeat)
	poison_repeat.start(time,execute_on_start=True)
	
def _poison_repeat(userid,attacker,dmg):
	damage(userid,dmg,attacker)
	wcs.wcs.tell(userid,"\x04[WCS] \x05Poison did \x04%s \x05damage to you!" % (dmg))

def changeTeam(userid, team):
	Player.from_userid(userid).set_team(int(team))

	
def valid_repeat(repeat):
	try:
		if repeat.status == RepeatStatus.RUNNIN:
			return 1
	except:
		return -1