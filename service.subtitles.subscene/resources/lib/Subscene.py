import requests
import html5lib
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
                result.append((href, lang, name, int(no_of_file), author, comment))
        
    for r in result:
        print r
    

def SearchMovie(item):
    # item['year']
    # item['title']
    # item['file_original_path']
    # item['3let_language']
    r = requests.post(DOMAIN_NAME + "/subtitles/searchbytitle", data={"query": item["title"], "l": ""})
    # print(r.status_code, r.reason)

    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(r.text)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)

    # Match for exact title
    results = SearchExactTitleMatch(stream)
    if len(results) > 0:
        # [(u'Face Off (1997)', u'/subtitles/faceoff-face-off')]
        # TODO: Match for the exact option in case we have more than one match
        
        # Time to list subtitles
        EnumSubtitles( DOMAIN_NAME + results[0][1])


    return

if __name__ == "__main__":
    item = {
        'title' : "face off"
    }
    SearchMovie(item)
