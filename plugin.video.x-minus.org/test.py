# -*- coding: utf-8 -*-
#this file is done for testing functionality of some defs on PC 
import re, os, urllib, urllib2, cookielib, time, sys
#from time import gmtime, strftime
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
    new         = ''

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
    #-- new
    try:    p.new = urllib.unquote_plus(params['new'])
    except: p.new = ''

    #-----
    return p

def tknd(hd): 
    c = 0
    hd2 = ''
    for h in range(4,-1,-1): 
        c = ord(hd[h])
        if (h != 1):
            c -= 1
        hd2 += chr(c)
        print hd2
    return hd2
    
#url = 'http://kinobar.net/news/bandy_nju_jorka/2013-06-19-2317'
url = 'http://x-minus.org/track/3658/%D0%BC%D0%B0%D0%BA%D1%81%D0%B8%D0%BC-%D0%BC%D0%B0%D0%BAs%D0%B8%D0%BC-%D0%B7%D0%BD%D0%B0%D0%B5%D1%88%D1%8C-%D0%BB%D0%B8-%D1%82%D1%8B.html'
html = get_HTML(url)
#str = re.findall(r'\d+',html)[0]

#str = 'http://x-minus.org/dwlf/' + re.findall( 'minus_track.tid=(.*?);', html)[0] + '/' + re.findall( 'minus_track.stkn="(.*?)";', html)[0] + '.mp3'
s = re.findall( 'minus_track.stkn="(.*?)";', html)[0]
print s
tknd(s)
#soup = BeautifulSoup(html)
#print soup
#ls = []
#newlist = soup.find('div',{'id':'pop_artists'}).findAll('div')
#print newlist
#for rec in newlist:
#    print rec
#	mi.title  = rec.find('div',{'class':'mat-img'}).find('img')['title'].encode('utf-8')
#	mi.img = rec.find('div',{'class':'mat-img'}).find('img')['src']
	


