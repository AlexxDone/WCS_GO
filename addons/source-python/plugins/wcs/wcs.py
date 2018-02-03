import os
import random
from random import choice
import time
import sys


from core import SOURCE_ENGINE_BRANCH

from path import Path
from sqlite3 import dbapi2 as sqlite
from base64 import encodestring as estr, decodestring as dstr
from configobj import ConfigObj
import string
import re
from messages import HudMsg
from menus import PagedMenu
from menus import PagedOption
from listeners import OnTick
import core

from translations.strings import LangStrings

#Source Python
from commands.say import SayCommand
from commands.client import ClientCommand
from commands.server import ServerCommand
from players.helpers import index_from_userid, userid_from_index,userid_from_edict
from entities.helpers import index_from_edict
from players.entity import Player
from players.dictionary import PlayerDictionary
from events import Event
from engines.server import execute_server_command, queue_command_string
from filters.players import PlayerIter

from menus import SimpleMenu
from menus import SimpleOption
from menus import Text

from commands import CommandReturn

from messages import SayText2, HintText
from listeners import OnLevelInit, OnLevelShutdown, OnClientActive
from listeners.tick import Delay, Repeat
import es
from colors import Color
#WCS Imports
from wcs import admin
from wcs import changerace
from wcs import commands
from wcs import config
from wcs.database import database
from wcs import downloader
from wcs import effects
import wcs.events
from wcs import firefix
from wcs import ladderfix
from wcs import levelbank
from wcs import logging
from wcs import longjump
from wcs import myinfo
from wcs import playerinfo
from wcs import raceinfo
from wcs import randomrace
from wcs import resetskills
from wcs import restrictions
from wcs import savexp
from wcs import setfx
from wcs import shopinfo
from wcs import shopmenu
from wcs import showitems
from wcs import showskills
from wcs import spendskills
from wcs import svar
from wcs import teamrestrictions
from wcs import wcs_commands
from wcs import wcsgroup
from wcs import wcshelp
from wcs import wcsmenu
from wcs import wcstop
from wcs import xtell


#	Config
from config.manager import ConfigManager
#	Cvars
from cvars.flags import ConVarFlags
from cvars import ConVar

color_codes = ['\x03', '\x04', '\x05', '\x06', '\x07']


#Config Part
tmp = {}

gamestarted = 0




	
#Helper Functions
def get_addon_path():
	path = os.path.dirname(os.path.abspath(__file__))
	return path

if os.path.isfile(os.path.join(get_addon_path(), 'strings', 'strings.ini')):
	strings = LangStrings(os.path.join(get_addon_path(), 'strings', 'strings'))	
	
def find_between(s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return ""
		
def get_cooldown(userid):
	player = getPlayer(userid)
	race = player.player.currace
	race1 = racedb.getRace(race)
	if 'player_ultimate' in raceevents[race]:
		skills = player.race.skills.split('|')
		index = raceevents[race]['player_ultimate'][0]
		skill = 'skill'+str(int(index)+1)
		try:
			level = int(skills[int(index)])
		except IndexError:
			level = None
		if level:
			downtime = str(race1[skill]['cooldown']).split('|')
			if len(downtime) == int(player.race.racedb['numberoflevels']):
				downtime = int(downtime[level-1])
				if not downtime:
					downtime = str(race1[skill]['cooldown']).split('|')
					downtime = int(downtime[0])
				return downtime
			else:
				return int(downtime[len(downtime)-1])

	
def format_message(message):
	for color in color_codes:
		if color in message:
			message = message.replace(color, '')
	return message
	
def tell(userid, message):
	text_message = 1
	index = index_from_userid(userid)
	if text_message == 1:
		if SOURCE_ENGINE_BRANCH == "css":
			message = message.replace('\x05','\x03')
		SayText2(message).send(index)
	if text_message == 2:
		message = format_message(message)
		HintText(message).send(index)
		
def centertell(userid,message):
	index = index_from_userid(userid)
	if SOURCE_ENGINE_BRANCH == "css":
		queue_command_string("es_centertell %s %s" %(userid,message))
	else:
		HudMsg(message, -1, 0.35,hold_time=5.0).send(index)
		
		
#Ini Manager	
class InI(object):
	def __init__(self):
		self.path = get_addon_path()

		self.races = os.path.join(self.path, 'races', 'races.ini')
		self.items = os.path.join(self.path, 'items', 'items.ini')

	@property
	def getRaces(self):
		try:
			return ConfigObj(self.races)
		except:
			sys.excepthook(*sys.exc_info())
			return ConfigObj(self._races)

	@property
	def getItems(self):
		return ConfigObj(self.items)
	
	@property
	def getCats(self):
		return ConfigObj(self.cats)			
ini = InI()

#Item Databse
class itemDatabase(object):
	def __init__(self):
		self.items = ini.getItems
		self.sectionlist = []
		self.itemlist = []
		self.itemtosection = {}

		for section in self.items:
			self.sectionlist.append(section)
			for item in self.items[section]:
				if item == 'desc':
					continue

				self.itemlist.append(item)
				self.itemtosection[item] = section

	def __contains__(self, item):
		return item in self.items

	def __iter__(self):
		for x in self.items:
			yield x

	def __getitem__(self, item):
		return self.items[item]

	def keys(self):
		return self.items.keys()

	def getSection(self, section):
		return dict(self.items[section])

	def getItem(self, item):
		return dict(self.items[self.getSectionFromItem(item)][item])

	def getSections(self):
		return list(self.sectionlist)

	def getItems(self):
		return list(self.itemlist)

	def getSectionFromItem(self, item):
		if item in self.itemtosection:
			return self.itemtosection[item]

		return None

	def getAll(self):
		return dict(self.items)
itemdb = itemDatabase()

#Race Database
class raceDatabase(object):
	def __init__(self):
		self.races = ini.getRaces

	def __contains__(self, race):
		return race in self.races

	def __iter__(self):
		for x in self.races:
			yield x

	def getRace(self, race):
		return self.races[race]

	def getAll(self):
		return self.races

	def getAlias(self):
		return aliass

	def index(self, race):
		return self.races.keys().index(race)	 
racedb = raceDatabase()


if len(racedb.getAll()):
	standardrace = racedb.getAll().keys()[0]
	ConVar('wcs_default_race').set_string(standardrace)
	
#PlayerObject Functions
def getPlayer(userid):
	userid = int(userid)
	if not userid in tmp:
		tmp[userid] = PlayerObject(userid)
	return tmp[userid]
	
class PlayerObject(object):
	def __init__(self, userid):
		self.userid				= userid
		self.index				= index_from_userid(self.userid)
		self.player_entity		= Player(self.index)
		self.steamid			= self.player_entity.steamid
		if self.steamid == 'BOT':
			self.steamid = 'BOT_'+str(self.player_entity.name)
		self.UserID				= database.getUserIdFromSteamId(self.steamid)
		
		if self.UserID is None:
			self.UserID			= database.addPlayer(self.steamid, self.player_entity.name)

		self.player				= _getPlayer(self.userid, self.UserID)
		self.race				= _getRace(self.UserID, self.player.currace, self.userid)

	def __del__(self):
		self.save()

	def __str__(self):
		return str(self.userid)

	def __int__(self):
		return self.userid

	def save(self):
		self.player.save()
		self.race.save()

	def changeRace(self, race, kill=True,who=None):
		self.race.save()

		if self.race.racedb['onchange']:
			command = self.race.racedb['onchange']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)
		oldrace = self.player.currace

		self.player.currace = str(race)

		self.race = _getRace(self.UserID, race, self.userid)
		self.race.update()
		self.race.refresh()
		self.race.save()
		if kill:
			self.player_entity.client_command("kill", True)
		if who == None:
			tell(self.player_entity.userid, '\x04[WCS] \x05You changed your race to \x04%s.' % race)
		if who == 'admin':
			tell(self.player_entity.userid,'\x04[WCS] \x05An admin set your race to \x04%s.' % race)
		if config.coredata['race_in_tag'] == 1:
			self.player_entity.clan_tag = race
		event_instance = wcs.events.wcs_changerace(userid=self.userid, oldrace=oldrace, newrace=race)
		event_instance.fire()

	def giveXp(self, amount, reason=''):
		return self.race.addXp(amount, reason)

	def giveLevel(self, amount):
		return self.race.addLevel(amount)

	def giveUnused(self, amount):
		return self.race.addUnused(amount)

	def givePoint(self, skill):
		return self.race.addPoint(skill)

	def showXp(self):
		xp		   = self.race.xp
		level	   = self.race.level
		if config.cfgdata['experience_system'] == 0:
			needed	   = config.cfgdata['interval']*level if level else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if level < len(level_string):
				needed = int(level_string[level])
			else:
				needed = int(level_string[len(level_string)-1])
		race	   = self.player.currace

		tell(self.userid, '\x04[WCS] \x04%s \x05 - Level: \x04%s \x05 - XP: \x04%s/%s' % (race, level, xp, needed))

	def showRank(self):
		name	   = self.player.name
		race	   = self.player.currace
		level	   = self.race.level
		place	   = database.getRank(self.steamid)
		total	   = str(len(database))
		xp		   = self.race.xp
		if config.cfgdata['experience_system'] == 0:
			needed	   = config.cfgdata['interval']*level if level else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if level < len(level_string):
				needed = int(level_string[level])
			else:
				needed = int(level_string[len(level_string)-1])
		unused	   = self.race.unused

		for player in PlayerIter():
			tell(player.userid, "\x05[WCS] \x05%s \x04is on race \x05%s \x04level\x05 %s\x04, ranked \x05%s/%s \x04with\x05 %s/%s \x04XP and \x05%s \x04Unused." % (name, race, level, place, total, xp, needed, unused))

	def delRace(self):
		self.player.totallevel -= int(self.race.level)
		database.delRace(self.UserID,self.player.currace)
		self.race.level = 0
		self.race.xp = 0
		self.race.skills = ''
		self.race.unused = 0
		self.race.refresh()
		self.race.save()

	def delPlayer(self):
		database.delPlayer(self.UserID)

		del tmp1[self.userid]
		del tmp2[self.userid]

		self.player = _getPlayer(self.userid, self.UserID)
		self.race = _getRace(self.UserID, self.player.currace, self.userid)

		self.race.refresh()

#Player Functions
tmp1 = {}
def _getPlayer(userid, UserID):
	userid = int(userid)
	if not userid in tmp1:
		tmp1[userid] = Player_WCS(userid, UserID)

	return tmp1[userid]
	

class Player_WCS(object):
	def __init__(self, userid, UserID):
		self.userid = userid
		self.UserID = UserID
		self.update()

	def update(self):
		self.steamid, self.currace, self.name, self.totallevel, self.lastconnect = self._getInfo(('steamid',
																								  'currace',
																								  'name',
																								  'totallevel',
																								  'lastconnect'))

		self.name = database.removeWarnings(self.name)

	def save(self):
		try:
			self._setInfo((self.steamid,self.currace,self.name,self.totallevel,self.lastconnect))
		except:
			return
			
	def _getInfo(self, what):
		if not hasattr(what, '__iter__'):
			what = (what, )

		v = database.getInfoPlayer(what,self.UserID)
		if v is None:
			player_entity = Player(index_from_userid(self.userid))
			return (player_entity.steamid, standardrace, player_entity.name, 0, time.time())

		return v

	def _setInfo(self, options):
		database.setInfoPlayer(options,self.UserID)

#Race functions
tmp2 = {}
def _getRace(userid, race, user):
	user = int(user)
	if not user in tmp2:
		tmp2[user] = {}

	if not race in tmp2[user]:
		tmp2[user][race] = Race(userid, race, user)

	return tmp2[user][race]

class Race(object):
	def __init__(self, UserID, race, user):
		self.userid		= user
		self.index = index_from_userid(self.userid)
		self.player_entity = Player(self.index)
		self.steamid	= self.player_entity.steamid
		if self.steamid == 'BOT':
			self.steamid == 'BOT_'+str(self.player_entity.name)
		self.UserID		= UserID
		self.player		= _getPlayer(self.userid, self.UserID)

		if not race in racedb:
			race = standardrace
			self.player.currace = standardrace

		self.RaceID		= database.getRaceIdFromUserIdAndRace(self.UserID, race)
		if self.RaceID is None:
			self.RaceID = database.addRaceIntoPlayer(self.UserID, race)

		self.racedb = racedb.getRace(race)

		self.update()
		self.refresh()

	def update(self):
		self.name, self.skills, self.level, self.xp, self.unused = self._getInfo(('name',
																				  'skills',
																				  'level',
																				  'xp',
																				  'unused'))

	def save(self):
		try:
			self._setInfo((self.name,self.skills,self.level,self.xp,self.unused))
		except:
			return

	def refresh(self):
		if not self.skills or self.skills is None or self.skills == 'None':
			skills = []
			for x in range(1,10):
				skill = 'skill'+str(x)
				if skill in self.racedb:
					skills.append('0')

			self.skills = '|'.join(skills)

	def _getInfo(self, what):
		if not hasattr(what, '__iter__'):
			what = (what, )
			
		v = database.getInfoRace(what,self.UserID,self.RaceID)			
		if v is None:
			return (self.player.currace, '', 0, 0, 0)

		return v

	def _setInfo(self, options):
		database.setInfoRace(options,self.UserID,self.RaceID)


	def addXp(self, amount, reason=''):
		amount = int(amount)
		if not amount:
			return

		maximumlevel = config.cfgdata['maximum_level']

		if 'maximumlevel' in self.racedb: #Tha Pwned
			maximumlevel = int(self.racedb['maximumlevel']) #Tha Pwned

		if self.level >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		currentXp = self.xp + amount

		amountOfLevels = 0
		
		
		if config.cfgdata['experience_system'] == 0:
			nextLevelXp = config.cfgdata['interval']*self.level if self.level else config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			level_string = config.cfgdata['custom_system'].split(',')
			if self.level < len(level_string):
				nextLevelXp = int(level_string[self.level])
			else:
				nextLevelXp = int(level_string[len(level_string)-1])
				
				
		if config.cfgdata['experience_system'] == 0:
			while currentXp >= nextLevelXp:
				amountOfLevels += 1
				currentXp -= nextLevelXp
				nextLevelXp += config.cfgdata['interval']
		elif config.cfgdata['experience_system'] == 1:
			x = 0
			level_string = config.cfgdata['custom_system'].split(',')
			while currentXp >=nextLevelXp:
				amountOfLevels += 1
				currentXp -= nextLevelXp
				if self.level+x < len(level_string):
					nextLevelXp += int(level_string[self.level+x])
				else:
					nextLevelXp += int(level_string[len(level_string)-1])
				x += 1

		self.xp = currentXp
		if not reason:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP.' % amount)
		else:
			tell(self.userid, '\x04[WCS] \x05You have gained \x04%s XP %s' % (amount, reason))

		if amountOfLevels+self.level >= maximumlevel: #Tha Pwned
			amountOfLevels = maximumlevel-self.level #Tha Pwned
			
		if amountOfLevels:
			self.addLevel(amountOfLevels)

		event_instance = wcs.events.wcs_gainxp(userid=self.userid, amount=amount, levels=amountOfLevels, currentxp=self.xp,reason=reason)
		event_instance.fire()		
		
		return currentXp

	def addLevel(self, amount):
		amount = int(amount)
		if not amount:
			return
			
		maximumlevel = config.cfgdata['maximum_level']

		if 'maximumlevel' in self.racedb: #Tha Pwned
			maximumlevel = int(self.racedb['maximumlevel']) #Tha Pwned

		if self.level >= maximumlevel: #Tha Pwned
			return #Tha Pwned

		if amount+self.level >= maximumlevel: #Tha Pwned
			amount = maximumlevel-self.level #Tha Pwned
			
		self.level += amount
		self.unused += amount
		self.player.totallevel += amount

		if 'BOT' in self.steamid:
			maxlevel = int(self.racedb['numberoflevels'])

			while True:
				if not self.unused:
					break

				possibleChoices = []
				skills = self.skills.split('|')

				if len(skills):
					if skills[0] == '':
						self.raceUpdate()

				for skill, level in enumerate(skills):
					if int(skills[skill]) < maxlevel:
						possibleChoices.append(str(skill+1))

				if not len(possibleChoices):
					break

				choice = random.choice(possibleChoices)
				self.addPoint(choice)

		else:
			if config.cfgdata['experience_system'] == 0:
				needed = config.cfgdata['interval']*self.level
			elif config.cfgdata['experience_system'] == 1:
				level_string = config.cfgdata['custom_system'].split(',')
				if self.level < len(level_string):
					needed = int(level_string[self.level])
				else:
					needed = int(level_string[len(level_string)-1])			
			tell(self.userid, '\x04[WCS] \x05You are on level \x04%s\x05 XP: \x04%s/%s' % (self.level, self.xp, needed))
			Delay(2.0, spendskills.doCommand, (self.userid,))
			return
		oldlevel = self.level - amount
		event_instance = wcs.events.wcs_levelup(userid=self.userid, race=self.name, oldlevel=oldlevel, newlevel=self.level,amount=amount)
		event_instance.fire()	

		return self.level

	def addUnused(self, amount):
		self.unused += amount
		return self.unused

	def addPoint(self, skill):
		skills = self.skills.split('|')
		index = int(skill)-1
		level = int(skills[index])

		if self.unused:
			skills.pop(index)
			skills.insert(index, str(level+1))

			self.skills = '|'.join(skills)

			self.unused -= 1

			return level+1
			
@SayCommand(config.ultimate_list)
@ClientCommand(config.ultimate_list)
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player = getPlayer(userid)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		returned = checkEvent1(userid, 'player_ultimate')
		if returned is not None:
			if returned is False:
				tell(userid, 'You cannot activate your ultimate now.')
			elif len(returned) == 3 and not returned[0]:
				tell(userid, '\x04[WCS] \x05You cannot use your \x04ultimate! \x05Cooldown time is \x04'+str(returned[1])+' \x05seconds, \x04'+str(returned[1]-returned[2])+' \x05left!')
	return CommandReturn.BLOCK

@Event('round_freeze_end')
def _event_freeze(ev):
	global gamestarted
	gamestarted = 1
	

				
@SayCommand(config.ability_list)
@ClientCommand(config.ability_list)
def _ultimate_command(command, index, team=None):
	userid = userid_from_index(index)
	player = getPlayer(userid)
	player_entity = Player(index)
	if int(player_entity.team) > 1 and not int(player_entity.dead):
		value = wcsgroup.getUser(userid, 'ability')
		if value == None:
			returned = checkEvent1(userid, 'player_ability')
			if returned is not None:
				if returned is False:
					tell(userid, '\x04[WCS] \x05You cannot activate your ability now.')
				elif len(returned) == 3 and not returned[0]:
					tell(userid, '\x04[WCS] \x05You cannot use your \x04ability! \x05Cooldown time is \x04'+str(returned[1])+' \x05seconds, \x04'+str(returned[1]-returned[2])+' \x05left!')
		else:
			if gamestarted == 1:
				es.ServerVar('wcs_userid').set(userid)
				es.doblock('wcs/tools/abilities/'+str(value)+'/'+str(value))
			else:
				tell(userid, '\x04[WCS] \x05You cannot activate your ability now.')
	return CommandReturn.BLOCK
	
@SayCommand(config.wcsrank_list)
@ClientCommand(config.wcsrank_list)
def _wcs_rank_command(command, index, team=None):
	userid = userid_from_index(index)
	wcstop.wcsRank(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.wcstop_list)
@ClientCommand(config.wcstop_list)
def _wcs_top_command(command, index, team=None):
	userid = userid_from_index(index)
	wcstop.doCommand(userid)
	return CommandReturn.BLOCK

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
	
@ServerCommand('wcs_changerace')
def _wcs_changerace(command):
	userid = int(command[1])
	if len(command) > 3:
		race = command[2]
		for x in command:
			if x != "wcs_changerace" and not is_number(x) and x != command[2]:
				race = race+" "+x
	else:
		race = str(command[2])
	player = getPlayer(userid)
	player.changeRace(race)
	
@ServerCommand('wcs_reload')
def _wcs_reload_command(command):
	load_races()
	
@ServerCommand('wcs_givexp')
def _wcs_givexp_command(command):
	userid = int(command[1])
	amount = int(command[2])
	player = getPlayer(userid)
	player.giveXp(amount)

@ServerCommand('wcs_givelevel')
def _wcs_givelevel_command(command):
	userid = int(command[1])
	amount = int(command[2])
	player = getPlayer(userid)
	player.giveLevel(amount)

@SayCommand(config.showxp_list)
@ClientCommand(config.showxp_list)
def _showxp_command(command, index, team=None):
		userid = userid_from_index(index)
		getPlayer(userid).showXp()


@SayCommand(config.wcsmenu_list)
@ClientCommand(config.wcsmenu_list)
def _wcsmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	wcsmenu.doCommand(userid)
	return CommandReturn.BLOCK
		
@SayCommand(config.raceinfo_list)
@ClientCommand(config.raceinfo_list)
def _raceinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	raceinfo.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.shopinfo_list)
@ClientCommand(config.shopinfo_list)
def _shopinfo_command(command, index, team= None):
	userid = userid_from_index(index)
	shopinfo.doCommand(userid)
	return CommandReturn.BLOCK
		
@SayCommand(config.spendskills_list)
@ClientCommand(config.spendskills_list)
def _spendskills_command(command, index, team= None):
	userid = userid_from_index(index)
	spendskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.changerace_list)
@ClientCommand(config.changerace_list)
def _changerace_command(command, index, team=None):
	userid = userid_from_index(index)
	if not command.arg_string:
		changerace.HowChange(userid)
	else:
		changerace.HowChange(userid,command.arg_string)
	return CommandReturn.BLOCK
	
@SayCommand(config.resetskills_list)
@ClientCommand(config.resetskills_list)
def _resetskills_command(command, index, team=None):
	userid = userid_from_index(index)
	resetskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.savexp_list)
@ClientCommand(config.savexp_list)
def _savexp_command(command, index, team=None):
	userid = userid_from_index(index)
	savexp.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.showskills_list)
@ClientCommand(config.showskills_list)
def _showskills_command(command, index, team=None):
	userid = userid_from_index(index)
	showskills.doCommand(userid)
	return CommandReturn.BLOCK

@SayCommand(config.wcshelp_list)
@ClientCommand(config.wcshelp_list)
def _wcshlep_command(command, index, team=None):
	userid = userid_from_index(index)
	wcshelp.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.shopmenu_list)
@ClientCommand(config.shopmenu_list)
def _shopmenu_command(command, index, team=None):
	userid = userid_from_index(index)
	shopmenu.doCommand(userid)
	return CommandReturn.BLOCK
	
@SayCommand(config.playerinfo_list)
@ClientCommand(config.playerinfo_list)
def _playerinfo_command(command, index, team=None):
	userid = userid_from_index(index)
	playerinfo.doCommand(userid)
	return CommandReturn.BLOCK
	
	
def buyitem_menu_select(menu, index, choice):
	userid = userid_from_index(index)
	shopmenu.addItem(userid, choice.value, pay=True, tell=True,close_menu=True)
	
	
@SayCommand(config.wcsbuyitem_list)
@ClientCommand(config.wcsbuyitem_list)
def wcs_buy_item(command,index,team=None):
	userid = userid_from_index(index)
	if len(command) < 2:
		return
	if len(command) > 2:
		item = command[1]
		for x in command:
			if x != "wcsbuyitem" and x != command[1]:
				item = item+" "+x
	else:
		item = str(command[1])
	items = find_items(item)
	if items != -1:
		if len(items) == 1:
			shopmenu.addItem(userid, items[0], pay=True, tell=True,close_menu=True)
		if len(items) > 1:
			buyitem_menu = PagedMenu(title='Choose item',select_callback=buyitem_menu_select,fill=False)
			buyitem_menu.clear()
			for i in items:
				iteminfo = itemdb.getItem(i)
				option = PagedOption('%s - %s$' % (str(iteminfo['name']), str(iteminfo['cost'])), i)
				buyitem_menu.append(option)
			buyitem_menu.send(index)
	return CommandReturn.BLOCK
	
item_names = []	

def find_items(name):
	item_list = []
	items_all = wcs.wcs.ini.getItems
	items_all.walk(gather_subsection)
	for item in item_names:
		item_sec = itemdb.getSectionFromItem(item)
		iteminfo = itemdb.getItem(item)
		if name.lower() in iteminfo['name'].lower():
			item_list.append(item)
	if len(item_list):
		return item_list
	else:
		return -1
	
def gather_subsection(section, key):
	if section.depth > 1:
		if section.name not in item_names:
			item_names.append(section.name)
	
#Events
@Event('player_changename')
def _player_changename(event):
	userid = event.get_int('userid')
	getPlayer(userid).player.name = database.removeWarnings(ev['newname'])
	
@Event('player_activate')	
def _player_activate(event):
	userid = int(event['userid'])
	player = getPlayer(userid)
	player_entity = Player(index_from_userid(userid))
	player.player.name = database.removeWarnings(player_entity.name)

	if not player_entity.steamid == 'BOT':
		Delay(10.0, tell, (userid, '\x04[WCS] \x05Welcome to this \x04WCS server\x05. Try \x04"wcshelp" \x05and bind mouse3 ultimate'))
	race = player.player.currace
	raceinfo = racedb.getRace(race)
	if raceinfo['allowonly'] != "":
		if not player_entity.steamid in raceinfo['allowonly']:
			rand_race = get_random_race(int(userid))
			player.changeRace(rand_race)
	player_entity.clan_tag = player.player.currace
	wcsgroup.addUser(userid)
	delay = ConVar('mp_force_pick_time').get_int()
	Delay(float(delay),set_team,(event['userid'],))


	
def get_random_race(userid):
	race_list = []
	races = racedb.getAll()
	allraces = races.keys()
	for number, race in enumerate(allraces):
		v = changerace.canUse(userid,race)
		if not v:
			race_list.append(race)
	if len(race_list):
		chosen = str(choice(race_list))
		return chosen
	else:
		return -1
		
def exists(userid):
	try:
		index_from_userid(userid)
	except ValueError:
		return 0
	
def set_team(userid):
	if exists(userid):
		player = Player.from_userid(userid)
		if player.team == 0:
			Player.from_userid(userid).team = 1

@Event('player_disconnect')	
def player_disconnect(event):
	userid = event.get_int('userid')
	player_entity = Player(index_from_userid(userid))

	if userid in tmp:
		tmp[userid].player.lastconnect = time.time()
		tmp[userid].player.name = database.removeWarnings(player_entity.name)
		tmp[userid].save()
		tmp1[userid].save()
		for x in tmp2[userid]:
			tmp2[userid][x].save()

		del tmp[userid]
		del tmp1[userid]
		del tmp2[userid]

	wcsgroup.delUser(userid)

@Event('round_start')
def round_start(event):
	freezetime = ConVar('mp_freezetime').get_int()
	if freezetime == 0:
		global gamestarted
		gamestarted = 1
	for player in PlayerIter():
		userid = player.userid
		if player.team >= 2:
			race = getPlayer(userid).player.currace
			raceinfo = racedb.getRace(race)
			if raceinfo['roundstartcmd']:
				command = raceinfo['roundstartcmd']
				command = command.split(";")
				ConVar("wcs_userid").set_int(userid)
				for com in command:
					execute_server_command('es', com)
saved = 0


def remove_effects():
	for player in PlayerIter():
		userid = player.userid
		queue_command_string('wcs_color %s 255 255 255 255' % userid)
		queue_command_string('wcs_setgravity %s 1.0' % userid)
		queue_command_string('es playerset speed %s 1.0' % userid)
		queue_command_string('es wcsgroup set regeneration_active %s 0' % userid)

		

@Event('round_end')
def round_end(event):
	global gamestarted
	gamestarted = 0
	delay = ConVar('mp_round_restart_delay').get_int()
	Delay(float(delay)-0.2,remove_effects)
	for player in PlayerIter():
		userid = player.userid
		if player.team >= 2:
			race = getPlayer(userid).player.currace
			raceinfo = racedb.getRace(race)
			if raceinfo['roundendcmd']:
				command = raceinfo['roundendcmd']
				command = command.split(";")
				for com in command:
					execute_server_command('es', com)
				
	xpsaver = config.coredata['xpsaver']
	if xpsaver:
		global saved
		if xpsaver <= saved:
			for x in tmp:
				tmp[x].save()

			for x in tmp1:
				tmp1[x].save()

			for x in tmp2:
				for q in tmp2[x]:
					tmp2[x][q].save()

			database.save()
			levelbank.database.save()
			saved = 0

		else:
			saved += 1
			
	if int(event['winner']) == 3:
		team = 'ct'
		other = ['t','alive']
	if int(event['winner']) == 2:
		team = 't'
		other = ['ct','alive']
	if str(event['winner']) not in "2;3":
		return
	for player in PlayerIter(team):
		if player.steamid == 'BOT':
			winxp = config.cfgdata['bot_roundwxp']
		else:
			winxp = config.cfgdata['player_roundwxp']
		wcs_player = getPlayer(player.userid)
		Delay(1, wcs_player.giveXp, (winxp, 'for winning the round'))
	for player in PlayerIter(other):
		if player.steamid == 'BOT':
			surxp = config.cfgdata['bot_roundsxp']
		else:
			surxp = config.cfgdata['player_roundsxp']		
		wcs_player = getPlayer(player.userid)
		Delay(1, wcs_player.giveXp, (surxp, 'for surviving the round'))			

			
			
			
@Event('player_death')			
def player_death(event):
	#player_death variables
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	if SOURCE_ENGINE_BRANCH == 'csgo':
		assister = event.get_int('assister')
	else:
		assister = 0
	headshot = event.get_int('headshot')
	weapon = event.get_string('weapon')
	queue_command_string('es wcsgroup set regeneration_active %s 0' % victim)
	#player_death execution
	victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))
				
	if attacker and victim:
		player = getPlayer(victim)

		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				player1 = getPlayer(attacker)
				bonus = 0
				if player1.race.level < player.race.level:
					diffience = player.race.level - player1.race.level
					#Bonus XP
					if attacker_entity.steamid == 'BOT':
						limit = config.cfgdata['bot_levellimit']
						if limit:
							if diffience > limit:
								diffience = limit
						bonus = config.cfgdata['bot_difxp']*diffience
					else:
						limit = config.cfgdata['player_levellimit']
						if limit:
							if diffience > limit:
								diffience = limit
						bonus = config.cfgdata['player_difxp']*diffience
				#Normal XP Gain
				if attacker_entity.steamid == 'BOT':
					killxp = config.cfgdata['bot_killxp']
					headshotxp = config.cfgdata['bot_headshotxp']
					knifexp = config.cfgdata['bot_knifexp']
					hexp = config.cfgdata['bot_hexp']
					flashxp = config.cfgdata['bot_flashxp']
					smokexp = config.cfgdata['bot_smokexp']
					if SOURCE_ENGINE_BRANCH == 'csgo':
						molotovxp = config.cfgdata['bot_molotovxp']
				else:
					killxp = config.cfgdata['player_killxp']
					headshotxp = config.cfgdata['player_headshotxp']
					knifexp = config.cfgdata['player_knifexp']
					hexp = config.cfgdata['player_hexp']
					flashxp = config.cfgdata['player_flashxp']
					smokexp = config.cfgdata['player_smokexp']
					if SOURCE_ENGINE_BRANCH == 'csgo':
						molotovxp = config.cfgdata['player_molotovxp']
				if bonus:
					Delay(1, player1.giveXp, (killxp+bonus, 'for killing a higher-level enemy. (\x04%s level difference bonus xp!)' % diffience))
				else:
					Delay(1, player1.giveXp, (killxp, 'for making a kill'))

				if headshot == 1:
					Delay(1, player1.giveXp, (headshotxp, 'for making a headshot'))
					
				elif 'knife' in weapon:
					Delay(1, player1.giveXp, (knifexp, 'for making a knife kill'))
				elif weapon == 'hegrenade':
					Delay(1, player1.giveXp, (hexp, 'for making a explosive grenade kill'))
				elif weapon == 'smokegrenade':
					Delay(1, player1.giveXp, (smokexp, 'for making a smoke grenade kill'))
				elif weapon == 'flashbang':
					Delay(1, player1.giveXp, (flashbangxp, 'for making a flashbang grenade kill'))
				elif weapon == 'inferno':
					Delay(1, player1.giveXp, (molotovxp, 'for making a fire kill'))
			

			checkEvent(victim,	'player_death',other_userid=attacker, assister=assister, headshot=headshot,weapon=weapon)
			checkEvent(attacker, 'player_kill', other_userid=victim, assister=assister, headshot=headshot,weapon=weapon)

		if player.race.racedb['deathcmd']:
			command = player.race.racedb['deathcmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)
			#queue_command_string(command)

	if victim and not attacker:
		checkEvent(victim,	'player_death')
	if assister:
		assist_player = Player.from_userid(int(assister))
		if assist_player.steamid == 'BOT':
			assistxp = config.cfgdata('bot_assistxp')
		else:
			assistxp = config.cfgdata('player_assistxp')
		wcs_player = getPlayer(assister)
		Delay(1, wcs_player.giveXp, (assistxp, 'for assisting in a kill'))
		checkEvent(assister,'player_assister')


@Event('player_hurt')
def _player_hurt(event):
	#player_hurt variables
	victim = event.get_int('userid')
	attacker = event.get_int('attacker')
	health = event.get_int('health')
	armor = event.get_int('armor')
	weapon = event.get_string('weapon')
	dmg_health = event.get_int('dmg_health')
	dmg_armor = event.get_int('dmg_armor')
	hitgroup = event.get_int('hitgroup')
	
	if victim:
		victim_entity = Player(index_from_userid(victim))
	if attacker:
		attacker_entity = Player(index_from_userid(attacker))
	if attacker and victim and not weapon.lower() in ('point_hurt') and not weapon.lower() in ('worldspawn'):
		if not victim == attacker:
			if not victim_entity.team == attacker_entity.team:
				checkEvent(victim, 'player_victim', other_userid=attacker, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
				if health > 0:
					checkEvent(attacker, 'player_attacker', other_userid=victim, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
				
			checkEvent(victim, 'player_hurt', other_userid=attacker, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
			if health > 0:
				checkEvent(attacker, 'player_hurt', other_userid=victim, health=health, armor=armor, weapon=weapon, dmg_health=dmg_health, dmg_armor=dmg_armor, hitgroup=hitgroup)
				
@Event('bomb_planted')
def bomb_planted(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		plantxp = config.cfgdata['bot_plantxp']
	else:
		plantxp = config.cfgdata['player_plantxp']
	wcs_player = getPlayer(userid)
	Delay(1, wcs_player.giveXp, (plantxp, 'for planting the bomb!'))
		
@Event('bomb_defused')
def bomb_planted(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		defusexp = config.cfgdata['bot_defusexp']
	else:
		defusexp = config.cfgdata['player_defusexp']
	wcs_player = getPlayer(userid)
	Delay(1, wcs_player.giveXp, (defusexp, 'for defusing the bomb!'))

@Event('bomb_exploded')
def bomb_exploded(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		explodexp = config.cfgdata['bot_explodexp']
	else:
		explodexp = config.cfgdata['player_explodexp']
	wcs_player = getPlayer(userid)
	Delay(1, wcs_player.giveXp, (explodexp, 'for letting the bomb explode!'))

@Event('hostage_rescued')
def hostage_rescued(event):
	userid = int(event['userid'])
	player = Player.from_userid(userid)
	if player.steamid == 'BOT':
		rescuexp = config.cfgdata['bot_rescuexp']
	else:
		rescuexp = config.cfgdata['player_rescuexp']
	wcs_player = getPlayer(userid)
	Delay(1, wcs_player.giveXp, (rescuexp, 'for rescuing a hostage!'))		

@OnClientActive
def on_client_active(index):
	player = getPlayer(userid_from_index(index))
	race = player.player.currace
	Player(index).clan_tag = race				
				
@Event('player_spawn')			
def _player_spawn(event):
	userid = event.get_int('userid')
	index = index_from_userid(userid)
	players = PlayerDictionary()
	player = getPlayer(userid)
	race = player.player.currace
	players[index].clan_tag = race
	if userid and players[index].team >= 2:
		for i, v in {'gravity':1.0,'speed':1.0,'longjump':1.0}.items():
			wcsgroup.setUser(userid, i, v)

		players[index].gravity = 1.0
		players[index].color = Color(255,255,255,255)


		player = getPlayer(userid)


		wcsgroup.addUser(userid)

		player.showXp()

		checkEvent(userid, 'player_spawn')

		race = player.player.currace
		raceinfo = racedb.getRace(race)
		if int(raceinfo['restrictteam']) and not players[index].steamid == 'BOT':
			if players[index].team == int(raceinfo['restrictteam']) and players[index].team >= 2 and not players[index].steamid == 'BOT':
				players[index].team = 1
				changerace.HowChange(userid)

		elif 'teamlimit' in raceinfo and not players[index].steamid == 'BOT':
			q = int(raceinfo['teamlimit'])
			if q:
				v = wcsgroup.getUser({2:'T',3:'CT'}[players[index].team], 'restricted')
				if v == None:
					v = 0
				if v > q:
					players[index].team = 1
					changerace.HowChange(userid)

		elif curmap in raceinfo['restrictmap'].split('|'):
			if not players[index].steamid == 'BOT':
					players[index].team = 1
					changerace.HowChange(userid)

		if raceinfo['spawncmd'] != "":
			command = raceinfo['spawncmd']
			command = command.split(";")
			for com in command:
				execute_server_command('es', com)


@Event('player_say')			
def player_say(event):
	userid = event.get_int('userid')
	checkEvent(userid, 'player_say')


raceevents = {}
aliass = {}

def unload():
	tmp.clear()
	tmp1.clear()
	tmp2.clear()
	aliass.clear()
	database.save()
	levelbank.database.save()
	database.close()
	levelbank.database.close()

def load_races():
	races = racedb.getAll()	
	for race in races:
		for section in races[race]:
			if section == 'skillcfg':
				global raceevents
				raceevents = {}
				if not race in raceevents:
					raceevents[race] = {}

				events = races[race]['skillcfg'].split('|')

				for index, cfg in enumerate(events):
					if not cfg in raceevents[race]:
						raceevents[race][cfg] = []

					raceevents[race][cfg].append(str(index))

			elif section == 'preloadcmd':
				if races[race]['preloadcmd'] != "":
					command = races[race]['preloadcmd']
					command = command.split(";")
					for com in command:
						execute_server_command('es', com)

def load():
	database.updateRank()
	global curmap
	curmap = ConVar("host_map").get_string().strip('.bsp')
	races = racedb.getAll()
	global aliass
	for race in races:
		for section in races[race]:
			if 'racealias_' in section:
				if section not in aliass:
					aliass[section] = str(races[race][section])

			if section == 'skillcfg':
				global raceevents
				if not race in raceevents:
					raceevents[race] = {}

				events = races[race]['skillcfg'].split('|')

				for index, cfg in enumerate(events):
					if not cfg in raceevents[race]:
						raceevents[race][cfg] = []

					raceevents[race][cfg].append(str(index))

			elif section == 'preloadcmd':
				if races[race]['preloadcmd'] != "":
					command = races[race]['preloadcmd']
					command = command.split(";")
					for com in command:
						execute_server_command('es', com)

			if 'skill' in section:
				for y in races[race][section]:
					if 'racealias_' in y:
						if y not in aliass:
							aliass[y] = str(races[race][section][y])

	items = ini.getItems
	for section in items:
		for item in items[section]:
			for q in items[section][item]:
				if 'shopalias_' in q:
					if q not in aliass:
						aliass[q] = str(items[section][item][q])
	if config.coredata['saving'] == 1:
		repeat_delay = config.coredata['save_time']*60
		repeat = Repeat(do_save)
		repeat.start(repeat_delay)

@OnLevelShutdown
def level_shutdown_listener():
	for player in PlayerIter():
		userid = player.userid
		savexp.doCommand(userid)
	
	database.save()
	levelbank.database.save()
	database.updateRank()
	
def do_save():
	for x in tmp:
		tmp[x].save()

	for x in tmp1:
		tmp1[x].save()

	for x in tmp2:
		for q in tmp2[x]:
			tmp2[x][q].save()
	database.save()
	levelbank.database.save()
	
@OnLevelInit
def level_init_listener(mapname):
	allow_alpha = ConVar('sv_disable_immunity_alpha')
	allow_alpha.set_int(1)
	autokick = ConVar('mp_autokick')
	autokick.set_int(0)
	tmp.clear()
	queue_command_string('sp reload wcs')
	global curmap
	if ".bsp" in mapname:
		mapname = mapname.strip('.bsp')
	curmap = mapname
	if config.coredata['saving'] == 1:
		repeat_delay = float(config.coredata['save_time'])*60.0
		repeat = Repeat(do_save)
		repeat.start(repeat_delay)
		
	
def checkEvent(userid, event, other_userid=0, health=0, armor=0, weapon='', dmg_health=0, dmg_armor=0, hitgroup=0,assister=0,headshot=0):
	if userid is not None:
		player_entity = Player(index_from_userid(userid))
		if int(player_entity.team) > 1:
			player = getPlayer(userid)
			race = player.player.currace
			race1 = racedb.getRace(race)
			if event in raceevents[race]:
				skills = player.race.skills.split('|')
				for index in raceevents[race][event]:
					try:
						level = int(skills[int(index)])
					except IndexError:
						level = None
					if level:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						skill = 'skill'+str(int(index)+1)

						try:
							if race1[skill]['setting'].split('|')[level-1]:
								settings = race1[skill]['setting'].split('|')[level-1]
								if ';' in settings:
									sub_settings = settings.split(';')
									for com in sub_settings:
										execute_server_command('es', com)
								else:
									execute_server_command('es', settings)
						except IndexError:
							continue

						if 'cmd' in race1[skill]:
							if race1[skill]['cmd']:
								command = race1[skill]['cmd']
								command = command.split(";")
								for com in command:
									execute_server_command('es', com)					
						else:
							continue
						if 'sfx' in race1[skill]:
							if race1[skill]['sfx']:
								command = race1[skill]['sfx']
								command = command.split(";")
								for com in command:
									execute_server_command('es', com)	
							

def checkEvent1(userid, event):
	if userid is not None:
		player_entity = Player(index_from_userid(userid))
		if int(player_entity.team) > 1:
			player = getPlayer(userid)
			race = player.player.currace
			race1 = racedb.getRace(race)
			if event in raceevents[race]:
				skills = player.race.skills.split('|')
				index = raceevents[race][event][0]

				try:
					level = int(skills[int(index)])
				except IndexError:
					level = None
				if level:
					gamestarted = 1
					if gamestarted:
						wcs_dice = ConVar('wcs_dice')
						wcs_dice.set_int(random.randint(0, 100))
						skill = 'skill'+str(int(index)+1)
						cooldown = wcsgroup.getUser(userid, event+'_cooldown')
						if cooldown is None:
							cooldown = 0
						cooldown = int(cooldown)
						wcsgroup.setUser(userid, event+'_pre_cooldown', cooldown)
						timed = int(float(time.time()))
						downtime = str(race1[skill]['cooldown']).split('|')
						if len(downtime) == int(player.race.racedb['numberoflevels']):
							downtime = int(downtime[level-1])
						else:
							downtime = int(downtime[0])

						if not downtime or (timed - cooldown >= downtime):
							if race1[skill]['setting']:
								try:
									if race1[skill]['setting'].split('|')[level-1]:
										settings = race1[skill]['setting'].split('|')[level-1]
										if ';' in settings:
											sub_settings = settings.split(';')
											for com in sub_settings:
												execute_server_command('es', com)
										else:
											execute_server_command('es', settings)
								except IndexError:
									return

							if 'cmd' in race1[skill]:
								ConVar("wcs_userid").set_int(userid)
								if race1[skill]['cmd']:
									command = race1[skill]['cmd']
									command = command.split(";")
									for com in command:
										execute_server_command('es', com)
									#command = re.sub(r"\bes\b","",command)
									#queue_command_string(command)
							else:
								return
							if 'sfx' in race1[skill]:
								ConVar("wcs_userid").set_int(userid)
								if race1[skill]['sfx']:
									command = race1[skill]['sfx']
									command = command.split(";")
									for com in command:
										execute_server_command('es', com)

							wcsgroup.setUser(userid, event+'_cooldown', timed)
							#Success
							return (1, downtime, timed-cooldown)
						#Cooldown
						return (0, downtime, timed-cooldown)
					#Game has not started
					return False
	return None

@ServerCommand('wcs_xalias')
def _wcs_xalias_command(command):
	alias = str(command[1])
	if alias in aliass:
		todo = aliass[alias].split(";")
		for com in todo:
			execute_server_command('es', com)
	
@ServerCommand('wcs_reload_races')
def _wcs_reload_races_command(command):
	if not 'reload' in time:
		time['reload'] = time.time()

	if time.time()-time['reload'] <= 180:
		racedb.races = ini.getRaces
		time['reload'] = time.time()
	load_races()
	
	
@ServerCommand('wcs_get_skill_level')
def get_skill_level(command):
	userid = str(command[1])
	var = str(command[2])
	skillnum = int(command[3])
	
	player = getPlayer(userid)
	skills = player.race.skills.split('|')
	if skillnum <= len(skills):
		ConVar(var).set_string(skills[skillnum-1])
	
@ServerCommand('wcs_getinfo')
def getInfoRegister(command):
	if len(command) == 5:
		userid = str(command[1])
		var = str(command[2])
		info = str(command[3])
		where = str(command[4])
 
		player = getPlayer(userid)
 
		if where == 'race':
			if hasattr(player.race, info):
				returned = getattr(player.race, info)
				ConVar(var).set_string(str(returned))
 
		elif where == 'player':
			if hasattr(player.player, info):
				returned = getattr(player.player, info)
				ConVar(var).set_string(str(returned))
		else:
			if not where in racedb:
				return
 
			v = _getRace(player.player.UserID, info, userid)
			if hasattr(v, info):
				returned = getattr(v, info)
				ConVar(var).set_string(str(returned))
				
@OnTick
def on_tick():
	if config.coredata['keyinfo'] == 1:
		for player in PlayerIter('all'):
			user_queue = PagedMenu.get_user_queue(player.index)
			if user_queue.active_menu is None:
				userid = player.userid
				p = getPlayer(userid)

				race = p.player.currace
				totallevel = p.player.totallevel
				level = p.race.level
				xp = p.race.xp
				if config.cfgdata['experience_system'] == 0:
					needed = config.cfgdata['interval']*level if level else config.cfgdata['interval']
				elif config.cfgdata['experience_system'] == 1:
					level_string = config.cfgdata['custom_system'].split(',')
					if level < len(level_string):
						needed = int(level_string[level])
					else:
						needed = int(level_string[len(level_string)-1])
				steamid = player.steamid
				if steamid == 'BOT':
					steamid == 'BOT_'+str(player.name)
				rank = database.getRank(steamid)
				text = str(race)+'\n--------------------\nTotallevel: '+str(totallevel)+'\nLevel: '+str(level)+'\nXp: '+str(xp)+'/'+str(needed)+'\n--------------------\nWCS rank: '+str(rank)+'/'+str(len(database))
				HudMsg(text, 0.025, 0.4,hold_time=0.2).send(player.index)
				


