import es
from wcs import wcsgroup
from wcs.xtell import tell


def trap():
	userid = str(es.ServerVar('wcs_userid'))
	count = int(wcsgroup.getUser(userid, 'ability_count'))
	if count:
		param = str(wcsgroup.getUser(userid, 'ability_parameter'))

		if param:
			param = param.split('_')
			team = int(es.getplayerteam(userid))

			if team == 2:
				teamtarget = '3'
				teamtargetn = '#ct'
				color = '255 0 10 150'

			elif team == 3:
				teamtarget = '2'
				teamtargetn = '#t'
				color = '10 0 255 150'

			x,y,z = es.getplayerlocation(userid)
			es.server.queuecmd('wcs_trap '+userid+' '+param[0]+' '+param[1]+' '+param[2]+' '+teamtarget+' '+teamtargetn+' '+str(x)+' '+str(y)+' '+str(z)+' '+str(es.ServerVar('wcs_roundcounter')))

			tell(userid, 'a_trapcreated')

		if count and not count == -1:
			wcsgroup.setUser(userid, 'ability_count', count-1)

	else:
		tell(userid, 'a_failed')
