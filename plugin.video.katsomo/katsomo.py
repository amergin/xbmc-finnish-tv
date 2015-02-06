# -*- coding: utf-8 -*-
import sys
from datetime import datetime, date

import xbmcplugin
import xbmcaddon
import xbmcutil as xbmcUtil
from katsomoscraper import KatsomoScraper


settings = xbmcaddon.Addon('plugin.video.katsomo')

# sets default encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf8')


class KatsomoAddon(xbmcUtil.ViewAddonAbstract):
	ADDON_ID = 'plugin.video.katsomo'
	GROUP = u'   [COLOR blue]%s[/COLOR]'
	FAVOURITE = '[COLOR yellow][B]•[/B][/COLOR] %s'

	def __init__(self):
		xbmcUtil.ViewAddonAbstract.__init__(self)
		self.addHandler(None, self.handleMain)
		self.addHandler('serie', self.handleSerie)
		self.addHandler('programs', self.handlePrograms)
		self.addHandler('live', self.handleLive)
		self.scrapper = KatsomoScraper()
		user = settings.getSetting('username')
		passwd = settings.getSetting('password')
		if user != "" and not self.scrapper.doLogin(user, passwd):
			xbmcUtil.notification('Message', 'Cannot login check your credentials')
		elif user == "":
			self.scrapper.noLogin()
		self.favourites = {}
		self.initFavourites()

		self.REMOVE = u'[COLOR red][B]•[/B][/COLOR] %s' % self.lang(30019)

	def handleMain(self, pg, args):
		#self.addViewLink('›› ' + lang(30020), 'programs', 1)
		self.addViewLink('[COLOR red]Can not play Katsomo videos (thanks to DRM)[/COLOR]', '', 1, {})
		self.addViewLink('LIVE', 'live', 1, {'link': 'http://m.mtvkatsomo.fi'})
		#self.addViewLink(lang(30028), 'serie', 1, {'link': 'http://m.katsomo.fi', 'useGroups': True})
		#self.addViewLink(lang(30021), 'serie', 1, {'link': 'http://m.katsomo.fi/?treeId=33001', 'useGroups': True})
		#self.addViewLink(lang(30027), 'serie', 1, {'link': 'http://m.katsomo.fi/?treeId=33002', 'useGroups': True})
		#self.addViewLink(lang(30023), 'serie', 1, {'link': 'http://m.katsomo.fi/?treeId=33003', 'useGroups': True})
		#for title, link in self.favourites.items():
		#	t = title
		#	cm = [(self.createContextMenuAction(self.REMOVE, 'removeFav', {'name': t}) )]
		#	self.addViewLink(self.FAVOURITE % t, 'serie', 1, {'link': link, 'pg-size': 10}, cm)

	def initFavourites(self):
		fav = self.addon.getSetting("fav")
		if fav:
			try:
				favList = eval(fav)
				for title, link in favList.items():
					self.favourites[title] = link
			except:
				pass

	def handlePrograms(self, pg, args):
		programs = self.scrapper.scrapPrograms()
		for p in programs:
			title = p['title']
			menu = [(self.createContextMenuAction(self.FAVOURITE % self.lang(30017), 'addFav', {'name': p['title'], 'link': p['link']}) )]
			if p['title'] in self.favourites:
				title = self.FAVOURITE % title
				menu = [(self.createContextMenuAction(self.REMOVE, 'removeFav', {'name': p['title']}) )]
			self.addViewLink(title, 'serie', 1, {'link': p['link']}, menu)

	def handleLive(self, pg, args):
		link = args['link']
		channels = self.scrapper.scrapLive(link)
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

		for s in channels:
			self.addVideoLink(s['title'], s['link'], s['img'])

	def handleSerie(self, pg, args):
		link = args['link']
		series = self.scrapper.scrapSerie(link)
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
		useGroups = args['useGroups'] if 'useGroups' in args else False;
		groupName = formatDate(datetime.now())

		for s in series:
			if useGroups and s['publ-ts'] != None and groupName != formatDate(s['publ-ts']):
				groupName = formatDate(s['publ-ts'])
				self.addVideoLink(self.GROUP % groupName, '', '')

			aired = s['publ-ts'].strftime('%Y-%m-%d') if s['publ-ts'] != None else ''
			self.addVideoLink(s['title'], s['link'], s['img'], infoLabels={'aired': aired})

	def handleVideo(self, link):
		vid = self.scrapper.scrapVideoLink(link)
		xbmc.log(vid)
		if vid == None:
			xbmcUtil.notification(header=lang(30070), message=lang(30071))
			return False
		else:
			return vid


	def handleAction(self, action, params):
		if action == 'addFav':
			self.favourites[params['name'].encode("utf-8")] = params['link']
			favStr = repr(self.favourites)
			self.addon.setSetting('fav', favStr)
			xbmcUtil.notification('Added', params['name'].encode("utf-8"))
		elif action == 'removeFav':
			self.favourites.pop(params['name'])
			favStr = repr(self.favourites)
			self.addon.setSetting('fav', favStr)
			xbmcUtil.notification('Removed', params['name'].encode("utf-8"))
		else:
			super(ViewAddonAbstract, self).handleAction(self, action, params)


# -----------------------------------

def formatDate(dt):
	delta = date.today() - dt.date()
	if delta.days == 0: return lang(30004)
	if delta.days == 1: return lang(30010)
	if delta.days > 1 and delta.days < 5: return dt.strftime('%A %d.%m.%Y')
	return dt.strftime('%d.%m.%Y')


katsomo = KatsomoAddon()
lang = katsomo.lang
katsomo.handle()
