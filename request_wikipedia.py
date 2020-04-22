from requests import RequestException
import requests
import time

API_URL = 'http://en.wikipedia.org/w/api.php'  # Wikipedia web
WIKI_PAGE_PREFIX = 'https://en.wikipedia.org/wiki/'

# INFO:https://en.wikipedia.org/wiki/Wikipedia:Namespace
name_space = {0: "", 1: "Talk:", 2: "User:", 3: "User_talk:", 4: "Wikipedia:", 5: "Wikipedia_talk:", 6: "File:",
              7: "File_talk:", 8: "MediaWiki:", 9: "MediaWiki_talk:", 10: "Template:", 11: "Template_talk:",
              12: "Help:", 12: "Help_talk:", 14: "Category:",
              15: "Category_talk:", 100: "Portal:", 101: "Portal_talk:", 118: "Draft:", 119: 'Draft_talk:',
              710: "TimedText:", 711: "TimedText_talk:", 828: "Module:",
              828: "Module_talk:", 108: "Book:", 109: "Book_talk:", 446: "Education_Program:",
              447: "Education_Program_talk:",
              2300: "Gadget:", 2301: "Gadget_talk:", 2302: "Gadget_definition:", 2303: "Gadget_definition_talk:"}


def db_search_subcat(main_category_title, connection):
    all_title_category = []
    number_query= 0
    query = 'SELECT cl_from FROM categorylinks WHERE cl_type ="subcat" AND cl_to=%s'
    number_query +=1
    subcat_results = connection.query_request2(query, (main_category_title[9:],))
    for subcat_result in subcat_results:
        query = 'SELECT page_title FROM page WHERE page_id=%s'
        number_query += 1
        result = connection.query_request2(query, (str(subcat_result[0]),))
        try:
            all_title_category.append('Category:' + str(result[0][0], 'utf-8'))
        except IndexError:
            print("DATABASE: page whit page id:" + (str(subcat_result)[1:-2]) + " Not found!")
    return all_title_category, number_query


def db_search_subpage(main_category_title, connection):
    all_title_page = []
    number_query= 0
    query = 'SELECT cl_from FROM categorylinks WHERE cl_type ="page" AND cl_to=%s'
    number_query +=1
    subpage_results = connection.query_request2(query, (main_category_title[9:],))
    for subpage_result in subpage_results:
        query = "SELECT page_title, page_namespace FROM page WHERE page_id=%s"
        number_query += 1
        result = connection.query_request2(query, (str(subpage_result[0]),))
        try:
            page_title = name_space[result[0][1]]+str(result[0][0], 'utf-8')
            page_url = WIKI_PAGE_PREFIX + page_title
            all_title_page.append([page_url, page_title])
        except IndexError:
            print("DATABASE: page whit page id:" + (str(subpage_result)[1:-2]) + " Not found!")
    return all_title_page, number_query




def wiki_search_subcat(category_title):
    search_params_subcat = {
        'list': 'categorymembers',
        'cmtype': 'subcat',
        'cmprop': 'ids|title',
        'cmlimit': 500,
        'cmtitle': category_title}

    subcat_results = _wiki_request(search_params_subcat)['query']['categorymembers']
    return list(subcat['title'] for subcat in subcat_results)


def wiki_search_subpage(category_title, ):
    page_info = []
    search_params_subpages = {
        'list': 'categorymembers',
        'cmtype': 'page',
        'cmprop': 'ids|title',
        'cmlimit': 500,
        'cmtitle': category_title}

    subpage_results = _wiki_request(search_params_subpages)['query']['categorymembers']

    for info in subpage_results:
        page_info.append([WIKI_PAGE_PREFIX + (info['title']).replace(" ", "_"), info['title']])
    return page_info


def _wiki_request(params):
    '''
    Make a request to the Wikipedia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''

    params['format'] = 'json'
    if not 'action' in params:
        params['action'] = 'query'
    try:
        r = requests.get(API_URL, params=params, timeout=5)
    except RequestException as e:
        print("Sleep 10 secondi")
        time.sleep(10)
        _wiki_request(params)
    return r.json()


def _wiki_search_url_by_ID(page_ID):
    search_page_ID = {
        'prop': 'info',
        'pageids': page_ID,
        'inprop': 'url'
    }  # This function search the URL of the main wikipedia page of a certain category

    return _wiki_request(search_page_ID)['query']['pages']


def _wiki_search_cat_ID_by_name(cat_name):
    # Example: https://www.mediawiki.org/w/api.php?action=query&titles=Category:Artificial%20intelligence

    search_cat_ID = {
        'titles': cat_name
    }

    # This searches the first element in the returned json dictionary
    return next(iter(_wiki_request(search_cat_ID)['query']['pages']))


# This function search the URL of the main wikipedia page of a certain category
# by inspecting the content of the category page
def _wiki_search_main_page_for_cat(cat_ID):
    params_cat_content = {
        'action': 'parse',
        'pageid': cat_ID,
        'prop': 'text'
    }