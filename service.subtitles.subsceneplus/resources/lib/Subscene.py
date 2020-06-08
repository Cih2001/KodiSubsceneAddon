import requests
import html5lib
import re
from html5lib import treebuilders, treewalkers

DOMAIN_NAME = "https://www.subscene.com"

def Hello():
    print "hello world"

def SearchExactTitleMatch(stream):
    results = []
    state = 0
    for token in stream:
        if state == 0:
            if token.has_key('data'):
                if token['data'] == "Exact":
                    state = 1
        elif state == 1:
            if token.has_key('name') and token['type'] == 'StartTag':
                if token['name'] == 'h':
                    state = 99
                elif token['name'] == 'ul':
                    state = 2
        elif state == 2:
            if token.has_key('name'):
                if token['name'] == "ul" and token['type'] == 'EndTag':
                    state = 99
                elif token['name'] == "li" and token['type'] == 'StartTag':
                    state = 3
        elif state == 3:
            if token.has_key('name'):
                if token['name'] == "li" and token['type'] == 'EndTag':
                    state = 2
                elif token['name'] == "div" and token['type'] == 'StartTag' and token['data'].values()[0] == "title":
                    state = 4
        elif state == 4:
            if token.has_key('name'):
                if token['name'] == "div" and token['type'] == 'EndTag':
                    state = 3
                elif token['name'] == "a" and token['type'] == 'StartTag':
                    for (k,v) in token['data']:
                        if v == "href":
                            href = token['data'][(k,v)]
                    state = 5
        elif state == 5:
            if token.has_key('name'):
                if token['name'] == "a" and token['type'] == 'EndTag':
                    state = 4
            elif token.has_key('data'):
                name = token['data']
                results.append((name,href))
        elif state == 99:
            break

    return results

def EnumSubtitles(url):
    r = requests.get(url)
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(r.text)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)

    result = []
    state = 0
    href = ""
    lang = ""
    name = ""
    no_of_file = 0
    author = ""
    comment = ""
    for token in stream:

        if state == 0:
            if token.has_key('name') and token['name'] == "tbody":
                state = 1
        elif state == 1:
            href = ""
            lang = ""
            name = ""
            no_of_file = 0
            author = ""
            comment = ""
            if token.has_key('name') and token['name'] == "tbody" and token['type'] == 'EndTag':
                state = 99
            elif token.has_key('name') and token['name'] == "tr" and token['type'] == 'StartTag':
                state = 2
        elif state == 2:
            if token.has_key('name') and token['name'] == "tr" and token['type'] == 'EndTag':
                state = 1
            elif token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a1":
                state = 3
        elif state == 3:
            if token.has_key('name') and token['name'] == "a" and token['type'] == 'StartTag':
                for (k,v) in token['data']:
                    if v == "href":
                        # grab href
                        href = token['data'][(k,v)]
                state = 4
        elif state == 4:
            if token.has_key('name') and token['name'] == "span" and token['type'] == 'StartTag':
                state = 5
        elif state == 5:
            if token.has_key('name') and token['name'] == "span" and token['type'] == 'StartTag':
                state = 6
            elif token.has_key('data') and token['type'] == "Characters":
                # grab lang
                lang = token['data']
        elif state == 6:
            if token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a3":
                state = 7
            elif token.has_key('data') and token['type'] == "Characters":
                # grab name
                name = token['data']
        elif state == 7:
            if token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a40":
                hearing_imp = False
                state = 8
            elif token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a41":
                hearing_imp = True
                state = 9
            elif token.has_key('data') and token['type'] == "Characters":
                # grab number of files
                no_of_file = token['data']
        elif state == 8:
            if token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a5":
                state = 15
        elif state == 9:
            if token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a5":
                state = 15
        elif state == 15:
            # TODO: Read author
            author = ""
            if token.has_key('name') and token['name'] == "td" and token['type'] == 'StartTag' and token['data'].values()[0] == "a6":
                state = 16
        elif state == 16:
            # TODO: Read comment
            comment = ""
            if token.has_key('name') and token['name'] == "tr" and token['type'] == 'EndTag':
                state = 1
                result.append((href, lang, name, int(no_of_file), hearing_imp, author, comment))
        elif state == 99:
            break

    return result
    

# TODO: refactor and change item with name, year
def SearchMovie(item):
    # item['year']
    # item['title']
    # item['file_original_path']
    # item['3let_language']
    r = requests.post(DOMAIN_NAME + "/subtitles/searchbytitle", data={"query": item["title"], "l": ""})

    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(r.text)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)

    # Match for exact title
    results = SearchExactTitleMatch(stream)
    if len(results) > 0:
        # [(u'Face Off (1997)', u'/subtitles/faceoff-face-off')]
        # TODO: Match for the exact option in case we have more than one match
        url = results[0][1]
        for result in results:
            m = re.match("^.*\(([0-9\s]*)\).*", result[0])
            if item['year'].strip() == m.group(1).strip():
               url = result[1] 
        # Time to list subtitles
        subtitles = EnumSubtitles(DOMAIN_NAME + url)
        return subtitles

    return None

# subtitle_id = '/subtitles/joker-2019/english/2109631'
# subtitle_name = 'Joker.2019.WEB-DL.x264-FGT'
# subtitle_link = 'ID for the download'
# web_pdb = <module 'web_pdb' from '/storage/.kodi/addons/script.module.web-pdb/libs/web_pdb/__init__.pyo'>
def DownloadSubtitle(link):
    r = requests.get(DOMAIN_NAME + link)
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(r.text)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)
   
    href = ""
    state = 0
    for token in stream:
        if state == 0:
            if token.has_key('name') and token['name'] == "div" and token['type'] == "StartTag":
                if token.has_key('data') and len(token['data']) > 0 and token['data'].values()[0] == "download":
                    state = 1
        elif state == 1:
            if token.has_key('name') and token['name'] == "a" and token['type'] == "StartTag":
                if token.has_key('data') and len(token['data']) > 0:
                    for k,v in token['data']:
                        if v == "href":
                            # grab href
                            href = token['data'][(k,v)]
                            state = 99

            if token.has_key('name') and token['name'] == "div" and token['type'] == 'EndTag':
                state = 99 
        elif state == 99:
            break
   
    if href == "":
        return None

    return requests.get(DOMAIN_NAME + href).content


if __name__ == "__main__":
    # item = {
    #     'title' : 'Joker',
    #     'year' : '2019' 
    # }
    # subtitles = SearchMovie(item)
    # for subtitle in subtitles:
    #     print subtitle
    DownloadSubtitle('/subtitles/joker-2019/english/2109631')
    DownloadSubtitle('/subtitles/joker-2019/farsi_persian/2088995')
