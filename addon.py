# -*- coding: utf-8 -*-
# Copyright 2017 Leo Moll
#

# -- Imports ------------------------------------------------
import sys,urlparse
import xbmc,xbmcplugin,xbmcgui

from de.yeasoft.kodi.KodiLogger import KodiLogger
from de.yeasoft.kodi.KodiAddon import KodiPlugin

from classes.store import Store
from classes.notifier import Notifier
from classes.settings import Settings
from classes.filmui import FilmUI
from classes.channelui import ChannelUI
from classes.initialui import InitialUI
from classes.showui import ShowUI

# -- Constants ----------------------------------------------
ADDON_ID = 'plugin.video.mediathekview'

# -- Classes ------------------------------------------------
class MediathekView( KodiPlugin ):

	def __init__( self ):
		super( MediathekView, self ).__init__()
		self.settings	= Settings()
		self.db			= Store( self.addon_id, self.getNewLogger( 'Store' ), Notifier(), self.settings )

	def __del__( self ):
		del self.db

	def addChannelList( self ):
		self.db.GetChannels( ChannelUI( self.addon_handle ) )

	def addInitialListInChannel( self, channelid ):
		self.db.GetInitials( channelid, InitialUI( self.addon_handle ) )

	def addFilmlistInChannelAndCategory( self, showid ):
		self.db.GetFilms( showid, FilmUI( self.addon_handle ) )

	def addShowListInChannelAndInitial( self, channelid, initial, count ):
		self.db.GetShows( channelid, initial, ShowUI( self.addon_handle ) )

	def addLiveStreams( self ):
		self.db.GetLiveStreams( FilmUI( self.addon_handle, [ xbmcplugin.SORT_METHOD_LABEL ] ) )

	def addRecentlyAdded( self ):
		self.db.GetRecents( FilmUI( self.addon_handle ) )

	def addSearch( self ):
		keyboard = xbmc.Keyboard( '' )
		keyboard.doModal()
		if keyboard.isConfirmed():
			searchText = unicode( keyboard.getText().decode( 'UTF-8' ) )
			if len( searchText ) > 2:
				self.db.Search( searchText, FilmUI( self.addon_handle ) )
			else:
				xbmc.executebuiltin( "Action(PreviousMenu)" )
		else:
			xbmc.executebuiltin( "Action(PreviousMenu)" )

	def addSearchAll( self ):
		keyboard = xbmc.Keyboard( '' )
		keyboard.doModal()
		if keyboard.isConfirmed():
			searchText = unicode( keyboard.getText().decode( 'UTF-8' ) )
			if len( searchText ) > 2:
				self.db.SearchFull( searchText, FilmUI( self.addon_handle ) )
			else:
				xbmc.executebuiltin( "Action(PreviousMenu)" )
		else:
			xbmc.executebuiltin( "Action(PreviousMenu)" )

	def addFolderItem( self, strid, params ):
		li = xbmcgui.ListItem( self.language( strid ) )
		xbmcplugin.addDirectoryItem(
			handle		= self.addon_handle,
			url			= self.build_url( params ),
			listitem	= li,
			isFolder	= True
		)

	def addMainMenu( self ):
		# search
		self.addFolderItem( 30901, { 'mode': "main-search" } )
		# search all
		self.addFolderItem( 30902, { 'mode': "main-searchall" } )
		# livestreams
		self.addFolderItem( 30903, { 'mode': "main-livestreams" } )
		# recently added
		self.addFolderItem( 30904, { 'mode': "main-recent" } )
		# Browse by Show in all Channels
		self.addFolderItem( 30905, { 'mode': "channel", 'channel': 0 } )
		# Browse Shows by Channel
		self.addFolderItem( 30906, { 'mode': "main-channels" } )
		xbmcplugin.endOfDirectory( self.addon_handle )

	def Init( self ):
		self.args			= urlparse.parse_qs( sys.argv[2][1:] )
		self.db.Init()

	def Do( self ):
		mode = self.args.get( 'mode', None )
		if mode is None:
			self.addMainMenu()
		elif mode[0] == 'main-search':
			self.addSearch()
		elif mode[0] == 'main-searchall':
			self.addSearchAll()
		elif mode[0] == 'main-livestreams':
			self.addLiveStreams()
		elif mode[0] == 'main-recent':
			self.addRecentlyAdded()
		elif mode[0] == 'main-channels':
			self.addChannelList()
		elif mode[0] == 'channel':
			channel = self.args.get( 'channel', [0] )
			self.addInitialListInChannel( channel[0] )
		elif mode[0] == 'channel-initial':
			channel = self.args.get( 'channel', [0] )
			letter = self.args.get( 'letter', [None] )
			count = self.args.get( 'count', [0] )
			self.addShowListInChannelAndInitial( channel[0], letter[0], count[0] )
		elif mode[0] == 'show':
			show = self.args.get( 'show', [0] )
			self.addFilmlistInChannelAndCategory( show[0] )

	def Exit( self ):
		self.db.Exit()

# -- Main Code ----------------------------------------------
addon = MediathekView()
addon.Init()
addon.Do()
addon.Exit()
del addon
