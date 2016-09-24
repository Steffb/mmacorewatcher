__author__ = 'steffenfb'

import urllib2
from bs4 import BeautifulSoup
import re
import datetime
import urllib
from pprint import pprint
import pickle
import webbrowser

#test_url = 'http://mma-core.com/videos/Cezar_Ferreira_vs_Anthony_Smith_TUF_23_Finale_Part_1/10133739'
test_url = 'http://www.mma-core.com/videos/Polo_Reyes_vs_Dong_Hyun_Kim_UFC_199_Part_3/10131366'

def getContentFromURL(url):
    req = urllib2.Request(url ,headers={'User-Agent' : "Magic Browser"})
    #urllib2.urlopen('http://google.com',headers={'User-Agent' : "Magic Browser"})
    page  = urllib2.urlopen(req)
    if(page.getcode() != 200):
        print 'Error code %d when fetching page '% (page.getcode())
        return

    html = page.read()
    return html, page.getcode()

def getContentFromLocal(path):


    return open(path).read()

    #Returns the table header, the table and the whole soup


def createSoups(html):
    if (html is None):
        print 'No html in createsoups'
        return None
    soup = BeautifulSoup(html,"html.parser")
    header =  soup.find("div", { "class" : "table-header" })
    body =  soup.findAll(lambda tag: tag.name == 'table' and tag.get('class') == ['odds-table'])
    headerSoup = BeautifulSoup(str(header),"html.parser")
    tableSoup = BeautifulSoup(str(body),"html.parser")

    return headerSoup,tableSoup,soup



def get_original_videolink_from_page(url,local=False):

    if(local):
        html= getContentFromLocal(url)[0]
        print html
    else:
        html= getContentFromURL(url)[0]

    soup = createSoups(html)[2]

    scripts = soup.find_all("script")
    print len(scripts)
    for s in scripts:
        #print s.contents
        if(s.string != None and 'mmaplayer' in s.string):
            #print '\n\n\t\tNEW SCRIPT \n\n'

            #The js object containing the url
            obj =  s.contents[0]

            string = obj.replace('\'','')
            string =  string.split(',')


            for s in string:

                if('file: /' in s ):
                    url = s.replace('file:','')
                    url = url.replace('{','')
                    url = url.replace('}','')

                    url = url.strip()
                    print'Found url as: \t'+ url
                    return url

    return

#Returns (prevname,prevurl) , (nextname, nexturl)
def get_nxt_links(url):

    html= getContentFromURL(url)[0]
    soup = createSoups(html)[2]
    div = soup.find("div", { "class" : "nxpr" })

    #print 'div: \t'+str(div)
    next = None
    prev = None
    for a in  div.find_all('a'):
        if('Next' in a.contents[0]):
            next =  (a.get('data-title'), a.get('href'))

        if('Previous' in a.contents[0]):
            prev =  (a.get('data-title'), a.get('href'))

    if( next != None and prev != None):
        return prev,next
    print '[Error] \t Did not find next and previous buttons'
    return

#Returns the title of the video on the page
def get_video_title(url):
    html= getContentFromURL(url)[0]
    soup = createSoups(html)[2]
    title =  soup.find('title').contents[0]
    if(title != None):
        return title
    else:
        print '[Error] \t could not get video title'
        return

    #Returns a dict with [name, url] of the videos on the frontpage containing eventname

#Checks the page is the videos on the div contain vs and returns the name,url in a dictionary
def get_videos_from_frontpage(localpath, local = False):
    if(local):
        html = getContentFromLocal(localpath)
    else:
        html= getContentFromURL('http://mma-core.com/trending')[0]

    soup = createSoups(html)[2]
    videoDiv = soup.find('div', { "class" : "pstlst" })

    videoh1s= videoDiv.find_all('h1')
    urldict = {}
    for h1 in videoh1s:
        a= h1.find('a')
        # TODO:Add fuctionality for fightnight

        if all(x in a.string.lower() for x in [' vs','ufc']):

            if('mma-core.com' not in a['href']):
                urldict[a.string] = 'http://mma-core.com'+a['href']
            else:
                urldict[a.string] = a['href']
    #pprint(urldict)
    return urldict



# Takes in a list of urls that 
def traverse_videos(urlDict):
    collected_urls_list=[]
    for url in urlDict.values():
        print '[running traverse videos] '
        print url
        if('mma-core.com' not in url):
            rootprev,rootnext = get_nxt_links('http://mma-core.com'+url)
        else:
            rootprev,rootnext = get_nxt_links(url)

        collected_urls  = []
        prev = rootprev
        # Go backwards!!

        while(True):

            if(' vs' in prev[0].lower() and 'ufc' in prev[0].lower()):
                collected_urls.append('http://mma-core.com'+prev[1])
                prev = get_nxt_links('http://mma-core.com'+prev[1])[0]

            else:
                break
        prev = None
        collected_urls = collected_urls[::-1]
        collected_urls.append(url)

        # Go forwards
        # TODO: needs fix
        next = rootnext
        while(True):

            if(' vs' in next[0].lower()):
                collected_urls.append('http://mma-core.com'+next[1])
                next = get_nxt_links('http://mma-core.com'+next[1])[1]

            else:
                break
        for url in collected_urls:
            url = url.replace('www.','')
            if(url not in collected_urls_list):
                collected_urls_list.append(url)


    #pickle.dump(collected_urls_list, open('urllist.p','wb'))
    return sorted(collected_urls_list)


# Takes in a sorted list if full fight urls and return a dict with Name= {url1, url2 ...}
def select_fight_function(list):
    #list = pickle.load(open('urllist.p','r'))
    fight_dict = {}
    for url in list:
        fight =url.split('/')[4]

        match = re.match('^[^_]*_[^_]*_[^_]*_[^_]*_[^_]*',fight)
        fight_name =  match.group(0)

        if(fight_name in fight_dict):
            fight_dict[fight_name].append(url)

        else:
            fight_dict[fight_name]= [url]
    return fight_dict
    #pprint(fight_dict)


## TEST FUNCTIONS
    #traverse_videos('http://www.mma-core.com/videos/Cezar_Ferreira_vs_Anthony_Smith_TUF_23_Finale_Part_1/10133739')

    #print 'http://mma-core.com'+get_original_videolink_from_page(test_url)

    #buttons = get_nxt_links(test_url)


    #print getContentFromLocal('/Users/steffenfb/programming/mma-core-trending.htm')

    #print get_original_videolink_from_page('/Users/steffenfb/programming/mma-core-trending.htm', local=True)

def run_on_local(path):
    dict = get_videos_from_frontpage(path, local=True)
    list = traverse_videos(dict)
    pprint(list)
    pickle.dump(list,open('urllist.p','wb'))
    fight_dict = select_fight_function(list)
    #TODO: continue
    while(True):
        pprint(fight_dict.keys())
        selected_fight = raw_input('Type fight to see')

        urllist = fight_dict[selected_fight]
        for url in urllist:
            try:
                raw_video_url = get_original_videolink_from_page(url)
                webbrowser.open_new_tab('http://mma-core.com'+raw_video_url)
                raw_input('Press enter for next video')
            except:
                print 'Error when loading url'

def run_on_mmacore():

    #TO FETCH ALL VIDEOLINKS: ----------

    #dict = get_videos_from_frontpage('/Users/steffenfb/programming/mma-core-trending.htm', local=True)
    dict = get_videos_from_frontpage('', local=False)

    list = traverse_videos(dict)
    pickle.dump(list,open('urllist.p','wb'))


    #list = pickle.load(open('urllist.p','rb'))
    pprint(list)


    for url in list:
        raw_input('press key to start next video')
        try:
            raw_video_url = get_original_videolink_from_page(url)
            webbrowser.open_new_tab('http://mma-core.com'+raw_video_url)
        except:
            print 'Error when loading url'





run_on_local('/Users/steffenfb/programming/mma-core-videos.htm')

