import wcs
from wcs import levelbank


def doCommand(userid):
	userid = int(userid)
	wcs.wcs.wcsplayers[userid].save()
	levelbank.bankplayer[userid].save()

	wcs.wcs.tell(int(userid), '\x04[WCS] \x05You have saved your \x04levels.')
