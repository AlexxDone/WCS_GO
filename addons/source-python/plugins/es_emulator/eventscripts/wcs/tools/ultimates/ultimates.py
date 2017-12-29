import es
from listeners.tick import Delay
from players.entity import Player
from filters.players import PlayerIter
from colors import Color
from wcs import wcs_commands
from wcs import wcsgroup
from mathlib import Vector
import core

def remove_freeze(player):
	player.freeze = 0

def cancel(userid, what):
	wcsgroup.setUser(userid, what+'_cooldown', wcsgroup.getUser(userid, what+'_pre_cooldown'))


def wcs_ulti_roots():
	userid = int(es.ServerVar('wcs_userid'))
	core.console_message("\nTest\n")
	player = Player.from_userid(userid)
	if player.team >= 2:
		core.console_message("\nTest2\n")
		count = 0
		wcs_commands.fade(userid,10,55,5,200,1)
		radius = float(es.ServerVar('wcs_radius'))
		time = float(es.ServerVar('wcs_duration'))
		atk_origin = player.origin
		for play in PlayerIter('alive'):
			if play.team != player.team:
				vic_origin = play.origin
				if vic_origin.get_distance(atk_origin) <= radius:
					if not wcsgroup.getUser(play.userid, 'ulti_immunity'):
						play.freeze = 1
						count += 1
						Delay(time, remove_freeze, (play,))
						es.server.queuecmd('es est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 1 5 5 10 3.8 0 160 0 155 2')
						es.server.queuecmd('es est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 1 4 4 10 2.3 0 108 0 180 2')
						es.server.queuecmd('es est_effect_06 #a 0 sprites/laser.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 1 5 5 10 4.1 0 80 0 190 2')
						es.server.queuecmd('es est_effect 10 #a 0 sprites/laser.vmt '+str(atk_origin[0])+' '+str(atk_origin[1])+' '+str(atk_origin[2]+10)+' 60 20 1 3 3 5 0 80 0 155 0')
						es.server.queuecmd('es est_effect 10 #a 0 sprites/laser.vmt '+str(atk_origin[0])+' '+str(atk_origin[1])+' '+str(atk_origin[2]+25)+' 75 35 1 3 3 6 0 108 0 190 0')
					else:
						es.tell(player.userid, '#multi', '#lightgreenYour ultimate was blocked, the enemy is #greenimmune.')
						es.tell(play.userid, '#multi', '#lightgreenYou #greenblocked #lightgreenan ultimate skill.')
	if count > 0:
		es.centertell(userid, 'Entangling Roots: %s' % (count))
	else:
		es.tell(userid, '#multi','#lightgreenEntangling Roots #greenfailed#lightgreen, because no enemy is close enough.')
		cancel(userid,'player_ultimate')
			
			
def wcs_ulti_chain():
	userid = int(es.ServerVar('wcs_userid'))
	player = Player.from_userid(userid)
	if player.team >= 2:
		count = 0
		wcs_commands.fade(userid,10,55,5,200,1)
		radius = float(es.ServerVar('wcs_radius'))	
		atk_origin = player.origin
		for play in PlayerIter('alive'):
			if play.team != player.team:
				vic_origin = play.origin
				if vic_origin.get_distance(atk_origin) <= radius:
					if not wcsgroup.getUser(play.userid, 'ulti_immunity'):
						wcs_commands.damage(play.userid,32,userid)
						count += 1
						es.server.queuecmd('es est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 .2 10 1 1 13 160 160 230 255 11')
						es.server.queuecmd('es est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 .2 10 2 2 12 150 150 255 220 8')
						es.server.queuecmd('es est_effect_06 #a 0 sprites/lgtning.vmt '+str(Vector(atk_origin[0],atk_origin[1],atk_origin[2]+35))+' '+str(Vector(vic_origin[0],vic_origin[1],vic_origin[2]+35))+' 10 .2 10 1 1 14 200 200 255 235 10')
					else:
						es.tell(userid, '#multi', '#lightgreenYour ultimate was blocked, the enemy is #greenimmune.')
						es.tell(play.userid, '#multi', '#lightgreenYou #greenblocked #lightgreenan ultimate skill.')
	if count > 0:
		es.centertell(userid, 'Chain Lightning: %s players damaged' % (count))
	else:
		es.tell(userid, '#multi', '#lightgreenChain Lightning #greenfailed#lightgreen, because no enemy is close enough to be damaged.')
		cancel(userid,'player_ultimate')