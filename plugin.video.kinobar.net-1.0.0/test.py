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

url = 'http://kinobar.net/'
#-- genre

html = get_HTML(url)
# -- parsing web page ------------------------------------------------------
soup = BeautifulSoup(html) #, fromEncoding="windows-1251")

#find total number of pages
for rec in soup.find('div',{'id':'allEntries'}).findAll('div', {'id':re.compile('entryID*')}):
    furl = rec.find('div', {'class':'mat-title'}).find('a')['href']
    ftitle = rec.find('div', {'class':'mat-title'}).text
    
    print furl
    print ftitle
    print rec
    print "--------------------"



