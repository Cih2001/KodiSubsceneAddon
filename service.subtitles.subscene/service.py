# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import urllib
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import shutil
import unicodedata

ADD_ON = xbmcaddon.Addon()
AUTHOR = ADD_ON.getAddonInfo('author')
SCRIPT_ID = ADD_ON.getAddonInfo('id')
SCRIPT_NAME = ADD_ON.getAddonInfo('name').encode('utf-8')
VERSION = ADD_ON.getAddonInfo('version')

CWD = unicode(xbmc.translatePath(ADD_ON.getAddonInfo('path')), 'utf-8')
PROFILE = unicode(xbmc.translatePath(ADD_ON.getAddonInfo('profile')), 'utf-8')
RESOURCE = unicode(xbmc.translatePath(os.path.join(CWD, 'resources', 'lib')), 'utf-8')
TEMP = unicode(xbmc.translatePath(os.path.join(PROFILE, 'temp', '')), 'utf-8')

sys.path.append(RESOURCE)

from Subscene import *

def Search(item):

  #### Do whats needed to get the list of subtitles from service site
  #### use item["some_property"] that was set earlier
  #### once done, set xbmcgui.ListItem() below and pass it to xbmcplugin.addDirectoryItem()
  
  listitem = xbmcgui.ListItem(label="English",                                   # language name for the found subtitle
                              label2="Some_SubtitleFile_name.srt",               # file name for the found subtitle
                              iconImage="4",                                     # rating for the subtitle, string 0-5
                              thumbnailImage="en.gif"                            # language flag, ISO_639_1 language + gif extention, e.g - "en.gif"
                              )
                              
  listitem.setProperty( "sync",        '{0}'.format("true").lower() )  # set to "true" if subtitle is matched by hash,
                                                                       # indicates that sub is 100 Comaptible
                                                                      
  listitem.setProperty( "hearing_imp", '{0}'.format("false").lower() ) # set to "true" if subtitle is for hearing impared
  
  
  ## below arguments are optional, it can be used to pass any info needed in download function
  ## anything after "action=download&" will be sent to addon once user clicks listed subtitle to downlaod
  url = "plugin://%s/?action=download&link=%s&ID=%s&filename=%s" % (SCRIPT_ID,
                                                                    "some url for subtitle downlaod",
                                                                    "ID for the downlaod",
                                                                    "filename of the subtitle")
  ## add it to list, this can be done as many times as needed for all subtitles found
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False) 


def Download():
  subtitle_list = []
  ## Cleanup temp dir, we recomend you download/unzip your subs in temp folder and
  ## pass that to XBMC to copy and activate
  if xbmcvfs.exists(TEMP):
    shutil.rmtree(TEMP)
  xbmcvfs.mkdirs(TEMP)

  subtitle_list.append("/Path/Of/Subtitle.srt") # this can be url, local path or network path.
  
  return subtitle_list
 
def normalizeString(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')    
 
def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
                                
  return param

def GetCurrentItem():
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                           # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                   # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")) # try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path of a playing file
  item['3let_language']      = []
  
  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    item['3let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_2))
  
  if item['title'] == "":
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title
    
  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]
  
  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]
  
  return item


# PLUGIN STARTS HERE
import web_pdb; web_pdb.set_trace()
Hello()
params = get_params()
print params

if params['action'] == 'search':
  item = GetCurrentItem() 
  Search(item)  

elif params['action'] == 'download':
  ## we pickup all our arguments sent from def Search()
  subs = Download(params["ID"],params["link"],params["filename"])
  ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that in XBMC core
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
  
  
xbmcplugin.endOfDirectory(int(sys.argv[1])) ## send end of directory to XBMC
