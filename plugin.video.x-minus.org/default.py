#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *     Author: velesiK
#/*     Year: 2015
# */
import re, os, urllib, urllib2, cookielib, time
#from time import gmtime, strftime
import urlparse

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.x-minus.org')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.jpg'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.jpg'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    artist      = ''
    genre       = ''
    genre_name  = ''
    max_page    = 0
    count       = 0
    url         = ''
    search      = ''
    song_url    = ''
    new         = ''
    img         = ''
    name        = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    year        = ''
    genre       = ''
    country     = ''
    director    = ''
    text        = ''
    artist      = ''
    orig        = ''
    duration    = ''
    rating      = ''

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None, l = None):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    print url

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    if l == None:
        html = f.read()
    else:
        html = f.read(l)

    return html

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    
    try:    p.artist = urllib.unquote_plus(params['artist'])
    except: p.artist = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''

    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = ''
    # movie count
    try:    p.max_page = int(urllib.unquote_plus(params['max_page']))
    except: p.max_page = 0
    # movie count
    try:    p.count = int(urllib.unquote_plus(params['count']))
    except: p.count = 0
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- par_url
    try:    p.song_url = urllib.unquote_plus(params['song_url'])
    except: p.song_url = ''
    #-- new
    try:    p.new = urllib.unquote_plus(params['new'])
    except: p.new = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-----
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.img = ''
    
    return p

#----------- get Header string -------------------------------------------------
def menu(par):
    #if we are in new films mode then we don't need header
    i = xbmcgui.ListItem('[COLOR FF00FF00]Популярные исполнители[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=POPULAR'
    xbmcplugin.addDirectoryItem(h, u, i, True)
            
    i = xbmcgui.ListItem('[COLOR FF00FFF0]Подборки[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=PODBORKI'
    xbmcplugin.addDirectoryItem(h, u, i, True)
    
    i = xbmcgui.ListItem('[COLOR FF00BFF0]Языки[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=LANGUAGES'
    xbmcplugin.addDirectoryItem(h, u, i, True)
    
    i = xbmcgui.ListItem('[COLOR FFFFFFFF]Жанры[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=GENRES'
    xbmcplugin.addDirectoryItem(h, u, i, True)
    
    
    i = xbmcgui.ListItem('[COLOR FFFFFF00]' + 'Поиск' + '[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SEARCH'
    #u += '&search=%s'%urllib.quote_plus('Y')
    xbmcplugin.addDirectoryItem(h, u, i, True)
     
    #will be added later
    #i = xbmcgui.ListItem('[COLOR FFFF0000]' + 'Новинки' + '[/COLOR]', iconImage=icon, thumbnailImage=icon)
    #u = sys.argv[0] + '?mode=NEW'
    #xbmcplugin.addDirectoryItem(h, u, i, True)
    
    xbmcplugin.endOfDirectory(h)

def Empty():
    return False

#"detokenize" the song :)
def tknd(hd): 
    c = 0
    hd2 = ''
    for h in range(4,-1,-1): 
        c = ord(hd[h])
        if (h != 1):
            c -= 1
        hd2 += chr(c)
    #if we have brackets char convert it to z
    if '{' in hd2:
        hd2 = hd2.replace('{','z')
    return hd2
    
def play(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(par.url)
    xbmc.log(str(par.song_url))
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    lyrics = ''
    try:
        lyrics = soup.find('div',{'id':'song_texts'}).text.encode('utf-8')
    except:
        pass
    
    i = xbmcgui.ListItem(par.name, par.song_url, thumbnailImage=par.img)
    i.setInfo(type='music', infoLabels={ 'title':par.name, 'lyrics ': '(lklkslkdflksfdljk)\n',
    'rating': '4',
    'artist': par.artist})
    
    window = xbmcgui.WindowDialog()
    textbox =xbmcgui.ControlLabel(340, 30, 600, 800, lyrics,'font10','0xFFFFFFFF' )
    window.addControl(textbox)
    
    xbmc.Player().play(par.song_url, i)
    window.doModal()
    #xbmcgui.Dialog().ok('Test',lyrics)
    
def drawList(soup,par):
    try:
        for rec in soup.find('ul',{'id':'minusovki'}).findAll('li'):
            mi.url = URL+rec.find('a',{'class':'tt'})['href'].encode('utf-8')
            mi.title = rec.find('a',{'class':'tt'}).text.encode('utf-8')
            mi.img = 'DefaultAudio.png'
            if par.img != '':
                mi.img = par.img
            #check if we can grab the image from the table
            if rec.find('a',{'class':'ar'}) != None:
                mi.img = urlToImgUrl(URL+rec.find('a',{'class':'ar'})['href'])
            songID = rec.s['id'][1:]
            songToken = tknd(rec.s['data-t'])
            song_url = URL+'/dwlf/'+songID+'/'+songToken+'.mp3'
            i = xbmcgui.ListItem(mi.title, song_url, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&artist=%s'%urllib.quote_plus(par.name)
            u += '&url='+urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            u += '&song_url=%s'%urllib.quote_plus(song_url)
            i.setInfo(type='music', infoLabels={ 'title':mi.title})
            xbmcplugin.addDirectoryItem(h, u, i, False)
    except:
        pass        
    xbmcplugin.endOfDirectory(h)    
    
def list(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(par.url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    drawList(soup,par)

def podborki(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(URL+'?tag_cloud=1')
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    
    for rec in soup.find('div',{'id':'tag-cloud-theme'}).findAll('a'):
        try:
            mi.url = URL+'/'+rec['href']
            mi.title  = rec.text.encode('utf-8')
            i = xbmcgui.ListItem(mi.title, iconImage='DefaultAudio.png', thumbnailImage='DefaultAudio.png')
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            
            i.setInfo(type='video', infoLabels={ 'title':mi.title})
            
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            pass
    
    xbmcplugin.endOfDirectory(h)

def languages(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(URL+'?tag_cloud=1')
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    
    for rec in soup.find('div',{'id':'tag-cloud-lang'}).findAll('a'):
        try:
            mi.url = URL+'/'+rec['href']
            mi.title  = rec.text.encode('utf-8')
            i = xbmcgui.ListItem(mi.title, iconImage='DefaultAudio.png', thumbnailImage='DefaultAudio.png')
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            
            i.setInfo(type='video', infoLabels={ 'title':mi.title})
            
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            pass
    
    xbmcplugin.endOfDirectory(h)

def genres(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(URL+'?tag_cloud=1')
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    
    for rec in soup.find('div',{'id':'tag-cloud-genre'}).findAll('a'):
        try:
            mi.url = URL+'/'+rec['href']
            mi.title  = rec.text.encode('utf-8')
            i = xbmcgui.ListItem(mi.title, iconImage='DefaultAudio.png', thumbnailImage='DefaultAudio.png')
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            
            i.setInfo(type='video', infoLabels={ 'title':mi.title})
            
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            pass
    
    xbmcplugin.endOfDirectory(h)

    
def popularSingers(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(URL)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    
    for rec in soup.find('div',{'id':'pop_artists'}).findAll('div'):
        try:
            mi.url = URL+'/'+rec.a['href']
            mi.title  = rec.a.text.encode('utf-8')
            #mi.img = urlToImgUrl(mi.url)
            mi.img = URL+'/'+rec.a.img[src]

            i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={ 'title':mi.title})
            
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            pass
    
    xbmcplugin.endOfDirectory(h)


def search(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    #if par.search == 'Y':
    skbd = xbmc.Keyboard()
    skbd.setHeading('Поиск минусовок.')
    skbd.doModal()
    if skbd.isConfirmed():
        xbmc.log(str(skbd.getText()))
        SearchStr = skbd.getText().split(':')
        par.search = SearchStr[0]
    else:
        return False
    
    url = URL+'/search/' #+ urllib.quote_plus(par.search)
    #check later if we need to encode chars here
    data = urllib.urlencode({'q': par.search})
    f = urllib.urlopen(url, data)
    html = f.read()
    soup = BeautifulSoup(html)
    
    drawList(soup,par)

def urlToImgUrl(url):
    #check if the last char is '/'
    if url[-1] == '/':
        return 'http://x-minus.org/img/artists/' + url.split('/')[-2] + 'mid.jpg'
    else:
        return 'http://x-minus.org/img/artists/' + url.split('/')[-1] + 'mid.jpg'

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

#-------------------------------------------------------------------------------
def get_params(paramstring):
    param=[]
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
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

URL = 'http://x-minus.org'
IMG_URL = 'http://x-minus.org/img/artists/'
mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    menu(params)

if mode == 'LIST':
    list(params)
elif mode == 'MENU':
    menu(params)    
elif mode == 'SEARCH':
    search(params)
elif mode == 'LANGUAGES':
    languages(params)
elif mode == 'GENRES':
    genres(params)
elif mode == 'POPULAR':
    popularSingers(params)
elif mode == 'PODBORKI':
    podborki(params)    
elif mode == 'PLAY':
    play(params)
