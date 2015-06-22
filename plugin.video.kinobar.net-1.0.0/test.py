# -*- coding: utf-8 -*-
#this file is done for testing functionality of some defs on PC 
import re, os, urllib, urllib2, cookielib, time, sys
from time import gmtime, strftime
import urlparse

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

import HTMLParser
hpar = HTMLParser.HTMLParser()

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

#---------- get HD720.RU URL --------------------------------------------------
def Get_URL(par):
    url = 'http://kinobar.net/'
    #-- genre
    if par.genre <> '':
        url += 'news/'+par.genre+'&'
    #-- page
    url += '?page'+par.page

    return url

#----------- get page count & number of movies ---------------------------------
def Get_Page_and_Movies_Count(par):
    url = 'http://kinobar.net/'
    #-- genre
    if par.genre <> '':
        url += 'do=cat&category='+par.genre
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
    for rec in soup.find('td', {'class':'full-story_text'}).text.split('|'):
        if rec.split(':', 1)[0] == u'Название':
            mi.tittle = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Оригинальное название':
            mi.orig = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Год':
            mi.year = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Страна':
            mi.country = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Жанр':
            mi.genre = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Режиссер':
            mi.director = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'В главных ролях':
            mi.artist = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'О фильме':
            mi.text = rec.split(':', 1)[1]

        if rec.split(':', 1)[0] == u'Продолжительность':
            mi.duration = rec.split(':', 1)[1].split(u'мин.')[0]

        if rec.split(':', 1)[0] == u'Рейтинг IMDB':
            mi.rating = rec.split(':', 1)[1].split('(')[0]

        #------------------------------------------------------
        if rec.split(':', 1)[0] == u'Сценарий':
            mi.text += '\n'+ rec

        if rec.split(':', 1)[0] == u'Продюсер':
            mi.text += '\n'+ rec

        if rec.split(':', 1)[0] == u'Оператор':
            mi.text += '\n'+ rec

        if rec.split(':', 1)[0] == u'Композитор':
            mi.text += '\n'+ rec

        if rec.split(':', 1)[0] == u'Бюджет':
            mi.text += '\n'+ rec

        if rec.split(':', 1)[0] == u'Премьера (мир)':
            mi.text += '\n'+ rec

    # -- get trailer
    try:
        s_url = re.compile('<!--dle_video_begin:(.+?)-->', re.MULTILINE|re.DOTALL).findall(html)[0]
        s_title = '[COLOR FFFF4000]Трейлер:[/COLOR]'

        #--
        i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
        u += '&url=%s'%urllib.quote_plus(s_url)
        u += '&img=%s'%urllib.quote_plus(img)
        u += '&vtype=%s'%urllib.quote_plus('MP4')
        try:
            i.setInfo(type='video', infoLabels={'title':            mi.title,
                                                'originaltitle':    mi.orig,
                        						'year':             int(mi.year),
                        						'director':         mi.director,
                                                'artist':           mi.artist,
                        						'plot':             mi.text,
                        						'country':          mi.country,
                        						'genre':            mi.genre,
                                                'rating':           float(mi.rating)
                                                })
        except:
            pass
        #i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)
    except:
        pass

    #get source info
    source_number = 1

    for rec in soup.findAll('iframe', {'src' : re.compile('video_ext.php\?')}):
        s_url   = rec['src']
        s_title = '[COLOR FF00FF00]SOURCE #'+str(source_number)+' ([/COLOR][COLOR FF00FFFF]ВКонтакте[/COLOR][COLOR FF00FF00])[/COLOR]'
        source_number = source_number + 1
        #--
        i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
        u += '&url=%s'%urllib.quote_plus(s_url)
        u += '&img=%s'%urllib.quote_plus(img)
        u += '&par_url=%s'%urllib.quote_plus(url)
        u += '&vtype=%s'%urllib.quote_plus('VK')
        try:
            i.setInfo(type='video', infoLabels={'title':            mi.title,
                                                'originaltitle':    mi.orig,
                        						'year':             int(mi.year),
                        						'director':         mi.director,
                                                'artist':           mi.artist,
                        						'plot':             mi.text,
                        						'country':          mi.country,
                        						'genre':            mi.genre,
                                                'rating':           float(mi.rating),
                                                'duration':         mi.duration
                                                })
        except:
            pass
        #i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    for rec in soup.findAll('param', {'name':'flashvars'}):
        for s in rec['value'].split('&'):
            if s.split('=',1)[0] == 'file':
                s_url = s.split('=',1)[1]
        s_title = '[COLOR FF00FF00]SOURCE #'+str(source_number)+' ([/COLOR][COLOR FFFF00FF]RuVideo[/COLOR][COLOR FF00FF00])[/COLOR]'
        source_number = source_number + 1
        #--
        i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
        u += '&url=%s'%urllib.quote_plus(s_url)
        u += '&img=%s'%urllib.quote_plus(img)
        u += '&par_url=%s'%urllib.quote_plus(url)
        u += '&vtype=%s'%urllib.quote_plus('RV')
        try:
            i.setInfo(type='video', infoLabels={'title':            mi.title,
                                                'originaltitle':    mi.orig,
                        						'year':             int(mi.year),
                        						'director':         mi.director,
                                                'artist':           mi.artist,
                        						'plot':             mi.text,
                        						'country':          mi.country,
                        						'genre':            mi.genre,
                                                'rating':           float(mi.rating),
                                                'duration':         mi.duration
                                                })
        except:
            pass
        #i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#url = 'http://kinobar.net/news/bandy_nju_jorka/2013-06-19-2317'
url = 'http://kinobar.net/news/vragi_sredi_nas_film_2010/2012-08-12-87'
html = get_HTML(url)
soup = BeautifulSoup(html)
mi = Info()
for rec in soup.find('div', {'id':'traf-zona'}).findAll('p'):
    if u'Название' in rec.text:
        mi.title = rec.text.split(':',1)[1]
    if u'Год' in rec.text:
        mi.year = rec.text.split(':', 1)[1]
    if u'Жанр' in rec.text:
        mi.genre = rec.text.split(':', 1)[1]
try:
    mi.text = soup.find('div', {'id':'traf-zona'}).find('span', {'itemprop':'description'}).text
except:
    mi.text = soup.find('div', {'id':'traf-zona'}).text
iframe = soup.find('iframe')
print iframe
iframeurl = soup.find('object', {'id':'pl'})
#if (iframeurl is not None) and (iframeurlis['data'] is not None):
    #html = get_HTML(iframeurl['data'])
    #m = re.findall ( '<video width="100%" height="100%" src="(.*?)" type="video/mp4"', html, re.DOTALL)[0]    
