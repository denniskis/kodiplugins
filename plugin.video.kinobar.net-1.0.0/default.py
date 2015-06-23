#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *     Author: velesiK
#/*     Year: 2015
# */
import re, os, urllib, urllib2, cookielib, time
from time import gmtime, strftime
import urlparse

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.kinobar.net')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
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
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    page        = '1'
    genre       = ''
    genre_name  = ''
    max_page    = 0
    count       = 0
    url         = ''
    search      = ''
    par_url     = ''

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
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
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
    try:    p.par_url = urllib.unquote_plus(params['par_url'])
    except: p.par_url = ''

    #-----
    return p

#---------- get kinobar.net URL --------------------------------------------------
def Get_URL(par):
    url = 'http://kinobar.net/'
    #-- genre
    if par.genre <> '':
        genre = par.genre.split('|')
        url += 'news/' + '/' + genre[0] + '-0-' + genre[1] + '&'
        #+ genre[0])+'/' + str(par.page) + '-0-' + str(genre[1]) + '&'
    #-- page
    url += '?page'+par.page

    return url

#----------- get page count & number of movies ---------------------------------
def Get_Page_and_Movies_Count(par):
    url = 'http://kinobar.net/'
    #-- genre
    if par.genre <> '':
        genre = par.genre.split('|')
        url += 'news/' + '/' + genre[0] + '-0-' + genre[1] + '&'
    html = get_HTML(url)
    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html) #, fromEncoding="windows-1251")
    max_page = 0
    for rec in soup.find('div',{'id':'pagesBlock1'}).findAll('span'):
        try:
            if max_page < int(rec.text):
                max_page = int(rec.text)
        except:
            pass
    #find total number of movies. We don't take into account here the last page not to do second http request. So this number is     approximate :)
    count = max_page*len(soup.find('div',{'id':'allEntries'}).findAll('div',{'class':'mat-title'}))

    return max_page, count

#----------- get Header string -------------------------------------------------
def Get_Header(par):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(par.count) + '[/COLOR]'

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.search <> '':
        info  += ' | Поиск: ' + '[COLOR FFFFFF00]'+ par.search +'[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
    u += '&count=%s'%urllib.quote_plus(str(par.count))
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genres & search
    if par.genre == '' and par.search == '' and par.page == '1':
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

        name    = '[COLOR FFFFFF00]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        #-- filter parameters
        u += '&search=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1 and par.search == '':
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) >= 10 and par.search == '':
        name    = '[COLOR FF00FF00][PAGE -10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-10))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        # -- get total number of movies and pages if not provided
        if par.count == 0:
            (par.max_page, par.count) = Get_Page_and_Movies_Count(par)

        # -- add header info
        Get_Header(par)

        #== get movie list =====================================================
        url = Get_URL(par)
        html = get_HTML(url)#.replace('<br />','|')
        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html)
        # -- get movie info
        for rec in soup.find('div',{'id':'allEntries'}).findAll('div', {'id':re.compile('entryID*')}):
            try:
                #--
                mi.url      = rec.find('div', {'class':'mat-title'}).find('a')['href']
                mi.title    = rec.find('div', {'class':'mat-title'}).text.encode('utf-8')
                mi.img      = rec.find('div', {'class':'mat-img'}).find('img')['src']
                #--
                for r in rec.find('div', {'class':'mat-txt'}).findAll('p'):
                    if u'Год:' in r.text:
                        mi.year = int(re.findall(r'\d+',r.text)[0])
                    if u'Страна:' in r.text:
                        mi.country = r.text.split(':')[1].encode('utf-8')
                    mi.text = r.text.encode('utf-8')
                i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
                u = sys.argv[0] + '?mode=SOURCE'
                u += '&name=%s'%urllib.quote_plus(mi.title)
                u += '&url=%s'%urllib.quote_plus(mi.url)
                u += '&img=%s'%urllib.quote_plus(mi.img)
                i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                                                    'year':        mi.year,
                                                    'plot':        mi.text,
                                                    'country':     mi.country,
                                                    'genre':       mi.genre})
                xbmcplugin.addDirectoryItem(h, u, i, True)
            except:
                pass
        #-- next page link
        if int(par.page) < par.max_page :
            name    = '[COLOR FF00FF00][PAGE +1][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&count=%s'%urllib.quote_plus(str(par.count))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        if int(par.page)+10 <= par.max_page :
            name    = '[COLOR FF00FF00][PAGE +10][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+10))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&count=%s'%urllib.quote_plus(str(par.count))
            xbmcplugin.addDirectoryItem(h, u, i, True)
        #xbmc.log("** "+str(pcount)+"  :  "+str(mcount))

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
                SearchStr = skbd.getText().split(':')
                par.search = SearchStr[0]
            else:
                return False
        #-- get search url
        #searchstr = urllib.urlencode(par.search)
        xbmc.log(par.search)
        url = 'http://kinobar.net/search/?q=' + par.search
        
        #searchstr = urllib.urlencode(par.search)
        #== get movie list =====================================================
        html = get_HTML(url) 
        # -- parsing web page ------------------------------------------------------
        soup = BeautifulSoup(html)
        
        # -- add header info
        Get_Header(par)
        #!this is not working and needs to be changed!
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

#---------- source list ---------------------------------------------------------
def Source_List(params):
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    #== get movie list =====================================================
    html = get_HTML(url) #.replace('<br />','|')

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)
    # -- get movie info
    for rec in soup.find('div', {'id':'traf-zona'}).findAll('p'):
        if u'Название' in rec.text:
            mi.title = rec.text.split(':',1)[1]
        if u'Год' in rec.text:
            mi.year = rec.text.split(':', 1)[1]
        if u'Жанр' in rec.text:
            mi.genre = rec.text.split(':', 1)[1]

    #get source info
    #we can display mp4 and flv sources; for now keeping only 1
    source_number = 1
    iframe = soup.find('iframe')
    if iframe is not None: 
        if 'video_ext.php' in iframe['src']:
            s_url = iframe['src']
            s_title = '[COLOR FF00FF00] ([/COLOR][COLOR FF00FFFF]ВКонтакте[/COLOR][COLOR FF00FF00])[/COLOR]'
            i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&img=%s'%urllib.quote_plus(img)
            u += '&vtype=%s'%urllib.quote_plus('VK')
            xbmcplugin.addDirectoryItem(h, u, i, False)
        else:
            serii = soup.find('div', {'id':'serii'})
            if serii is not None:
                for r in serii.findAll('a'):
                    html = get_HTML(r['id'])
                    s_url = re.findall ( '<video width="100%" height="100%" src="(.*?)" type="video/mp4"', html, re.DOTALL)[0]	
                    s_title = '[COLOR FF00FF00] '+r.text.encode('utf-8')+' ([/COLOR][COLOR FF00FFFF].MP4[/COLOR][COLOR FF00FF00])[/COLOR]'
                    i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
                    u = sys.argv[0] + '?mode=PLAY'
                    u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
                    u += '&url=%s'%urllib.quote_plus(s_url)
                    u += '&img=%s'%urllib.quote_plus(img)
                    u += '&vtype=%s'%urllib.quote_plus('MP4')
                    xbmcplugin.addDirectoryItem(h, u, i, False)
            else:
                html = get_HTML(iframe['src'])
                s_url = re.findall ( '<video width="100%" height="100%" src="(.*?)" type="video/mp4"', html, re.DOTALL)[0]	
                s_title = '[COLOR FF00FF00]'+s_url.split('/')[-1]+' ([/COLOR][COLOR FF00FFFF][/COLOR][COLOR FF00FF00])[/COLOR]'
                source_number = source_number + 1
                i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
                u = sys.argv[0] + '?mode=PLAY'
                u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
                u += '&url=%s'%urllib.quote_plus(s_url)
                u += '&img=%s'%urllib.quote_plus(img)
                u += '&vtype=%s'%urllib.quote_plus('MP4')
                xbmcplugin.addDirectoryItem(h, u, i, False)
    iframeurl = soup.find('object', {'id':'pl'})
    if (iframeurl is not None) and (iframeurl['data'] is not None):
        html = get_HTML(iframeurl['data'])
        s_url = re.findall ( '<video width="100%" height="100%" src="(.*?)" type="video/mp4"', html, re.DOTALL)[0]	
        s_title = '[COLOR FF00FF00]SOURCE #'+s_url.split('/')[-1]+' ([/COLOR][COLOR FF00FFFF].MP4[/COLOR][COLOR FF00FF00])[/COLOR]'
        #--
        i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
        u += '&url=%s'%urllib.quote_plus(s_url)
        u += '&img=%s'%urllib.quote_plus(img)
        u += '&par_url=%s'%urllib.quote_plus(url)
        u += '&vtype=%s'%urllib.quote_plus('MP4')
        try:
            i.setInfo(type='video', infoLabels={'title':            mi.title,
                                                'year':             int(mi.year),
                                                'plot':             mi.text,
                                                'genre':            mi.genre
                                                })
        except:
            pass
        #i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://kinobar.net/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('div',{'id':'sidebarr'}).findAll('li'):
        name     = rec.find('a').text.encode('utf-8')
        pregenre = rec.find('a')['href'].split('/')
        genre_id = pregenre[-2] + '|'+ pregenre[-1].split('-')[-1]

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(genre_id)
        u += '&genre_name=%s'%urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    '''
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
    '''
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

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    Movie_List(params)

if mode == 'MOVIE':
    Movie_List(params)
elif mode == 'SEARCH':
    Movie_Search(params)
elif mode == 'SOURCE':
    Source_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
    PLAY(params)


