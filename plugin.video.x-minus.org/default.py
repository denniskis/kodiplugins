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
    u = sys.argv[0] + '?mode=GENRES'
    xbmcplugin.addDirectoryItem(h, u, i, True)
    
    i = xbmcgui.ListItem('[COLOR FFFFFF00]' + 'Поиск' + '[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SEARCH'
    #u += '&search=%s'%urllib.quote_plus('Y')
    xbmcplugin.addDirectoryItem(h, u, i, True)
            
    i = xbmcgui.ListItem('[COLOR FFFF0000]' + 'Новинки' + '[/COLOR]', iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=NEW'
    xbmcplugin.addDirectoryItem(h, u, i, True)
    
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
    return hd2
    
def play(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(par.url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    lyrics = ''
    try:
        lyrics = soup.find('div',{'id':'song_texts'}).text.encode('utf-8')
    except:
        pass
    #xbmc.log(lyrics)
    i = xbmcgui.ListItem(par.name, par.song_url, thumbnailImage=par.img)
    i.setInfo(type='music', infoLabels={ 'title':par.name, 'lyrics': '(lklkslkdflksfdljk)',
    'artist': par.artist})
    
    window = xbmcgui.WindowDialog()
    textbox =xbmcgui.ControlLabel(340, 30, 600, 800, lyrics,'font10','0xFFFFFFFF' )
    window.addControl(textbox)
    
    xbmc.Player().play(par.song_url, i)
    window.doModal()
    #xbmcgui.Dialog().ok('Test',lyrics)
    
    
    
def list(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    html = get_HTML(par.url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    for rec in soup.find('ul',{'id':'minusovki'}).findAll('li'):
        mi.url = URL+rec.find('a',{'class':'tt'})['href'].encode('utf-8')
        mi.title = rec.find('a',{'class':'tt'}).text.encode('utf-8')
        songID = rec.s['id'][1:]
        songToken = tknd(rec.s['data-s'])
        song_url = URL+'/dwlf/'+songID+'/'+songToken+'.mp3'
        i = xbmcgui.ListItem(mi.title, song_url, thumbnailImage=par.img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(mi.title)
        u += '&artist=%s'%urllib.quote_plus(par.name)
        u += '&url='+urllib.quote_plus(mi.url)
        u += '&img=%s'%urllib.quote_plus(par.img)
        u += '&song_url=%s'%urllib.quote_plus(song_url)
        i.setInfo(type='music', infoLabels={ 'title':mi.title})
        xbmcplugin.addDirectoryItem(h, u, i, False)
        
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
            mi.img = URL+'/'+rec.a.img['src']

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

#---------- movie search list --------------------------------------------------
def Movie_Search(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    if par.search == 'Y':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов.')
        skbd.doModal()
        if skbd.isConfirmed():
            xbmc.log(str(skbd.getText()))
            SearchStr = skbd.getText().split(':')
            par.search = SearchStr[0]
        else:
            return False
    #-- get search url
    
    url = 'http://kinobar.net/search/?q=' + urllib.quote_plus(par.search)
    
    #== get movie list =====================================================
    html = get_HTML(url) 
    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    
    # -- add header info
    Get_Header(par)
    
    for rec in soup.find('div',{'id':'searchText'}).findAll('div'):
        try:
            if rec['class'] == 'mat-img':
                mi.img      = rec.find('img')['src']
                #extract url from img also
                mi.url      = rec.find('a')['href']
            if rec['class'] == 'mat-title':
                mi.title = rec.find('a').text.encode('utf-8')
            if rec['class'] == 'mat-txt':
                mi.text = rec.text.encode('utf-8')
            if mi.img != '' and mi.url != '' and mi.title != '' and mi.text != '':
                i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
                u = sys.argv[0] + '?mode=SOURCE'
                u += '&name=%s'%urllib.quote_plus(mi.title)
                u += '&url=%s'%urllib.quote_plus(mi.url)
                u += '&img=%s'%urllib.quote_plus(mi.img)
                i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                                                    'plot':        mi.text
                                                    })
                xbmcplugin.addDirectoryItem(h, u, i, True)
                mi.img, mi.url, mi.title, mi.text = '','','',''
                
        except:
            pass

    xbmcplugin.endOfDirectory(h)

def PLAYbak(params):
    try:
        # -- parameters
        url   = urllib.unquote_plus(params['url'])
        img   = urllib.unquote_plus(params['img'])
        name  = urllib.unquote_plus(params['name'])
        vtype = urllib.unquote_plus(params['vtype'])

        if url == '*':
            return False

        video = url
        # -- get VKontakte video url
        if vtype == 'VK':
            url = url.replace('vkontakte.ru', 'vk.com')
            html = get_HTML(url)

            soup = BeautifulSoup(html, fromEncoding="windows-1251")

            for rec in soup.findAll('script', {'type':'text/javascript'}):
                if 'video_host' in rec.text:
                    for r in re.compile('var (.+?) = \'(.+?)\';').findall(html):
                        if r[0] == 'video_host':
                            video_host = r[1]#.replace('userapi', 'vk')
                        if r[0] == 'video_uid':
                            video_uid = r[1]
                        if r[0] == 'video_vtag':
                            video_vtag = r[1]
            video = '%su%s/videos/%s.720.mp4'%(video_host, video_uid, video_vtag)
            html = get_HTML(video, None, None, 1000)


            for rec in soup.findAll('param', {'name':'flashvars'}):
                for s in rec['value'].split('&'):
                    if s.split('=',1)[0] == 'uid':
                        uid = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'vtag':
                        vtag = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'host':
                        host = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'vid':
                        vid = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'oid':
                        oid = s.split('=',1)[1]

            url = 'http://vk.com/videostats.php?act=view&oid='+oid+'&vid='+vid+'&quality=720'
            print url
            ref = 'http://vk.com'+soup.find('param',{'name':'movie'})['value']
            print ref
            html = get_HTML(url, None, ref)

        # -- play video
        i = xbmcgui.ListItem(name, video, thumbnailImage=img)
        xbmc.Player().play(video, i)
    except:
        pass
#-------------------------------------------------------------------------------

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

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

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

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    menu(params)

if mode == 'LIST':
    list(params)
elif mode == 'NEW':
	New_List(params)
elif mode == 'MENU':
	menu(params)    
elif mode == 'SEARCH':
    Movie_Search(params)
elif mode == 'SOURCE':
    Source_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'POPULAR':
    popularSingers(params)
elif mode == 'PLAY':
    play(params)
