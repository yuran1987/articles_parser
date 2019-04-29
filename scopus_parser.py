import requests, json, configparser
from datetime import datetime


class Elsevier(object):

    ___base_uri = "https://api.elsevier.com/content/search/scopus"
    ___api_key = '000000xdfdfdfg'
    ___article_count = 0
    articles = []

    def __init__(self, author_id, api_key, uri = ''):
        """Initializes an author given a Scopus author URI or author ID"""
        if uri:
            self.___base_uri = uri
        if not uri and not author_id:
            raise ValueError('No URI or author ID specified')
        if api_key:
            self.___api_key = api_key

        self.author_id = author_id
        resp = requests.get(url="{0}?query=AU-ID({1})&field=dc:identifier".format(self.___base_uri, author_id),
                            headers={'Accept': 'application/json',
                                     'X-ELS-APIKey': self.___api_key})
        data = resp.json()
        self.___article_count = data['search-results']['opensearch:totalResults']
        print("Получено публикаций в результате поиска: {0}".format(self.___article_count))

        for item in data['search-results']['entry']:
            d = {'url': item['prism:url'], 'scopus_id': item['dc:identifier']}
            self.articles.append(d)

    def get_article_info(self, article_url):
        url = (article_url
               + "?field=authors,title,publicationName,volume,issueIdentifier,"
               + "prism:pageRange,coverDate,article-number,prism:doi,citedby-count,prism:aggregationType")
        resp = requests.get(url, headers={'Accept': 'application/json', 'X-ELS-APIKey': self.___api_key})
        if resp.text:
            results = json.loads(resp.text.encode('utf-8'))
            coredata = results['abstracts-retrieval-response']['coredata']

            return {'authors':', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']]),
                      'title': coredata['dc:title'],
                      'pubname': coredata['prism:publicationName'],
                      'volume': coredata['prism:volume'],
                      'pages': coredata.get('prism:pageRange'),
                      'number': coredata.get('article-number'),
                      'year': datetime.strptime(coredata['prism:coverDate'], "%Y-%m-%d").year,
                      'doi': coredata['prism:doi'] if 'prism:doi' in coredata.keys() else None,
                      'cites': int(coredata['citedby-count'])
                    }
        else:
            raise ValueError("Request return empty result")

    def print_article_list(self):
        res = []
        for item in self.articles:
            res.append(self.get_article_info(article_url=item['url']))
        print("Распознано публикаций: {0}".format(len(res)))
        return res

#**************************************************************************
#
#
#                               EXAMPLE
#
#
#**************************************************************************
config = configparser.RawConfigParser()
config.read("config.conf")
api_key = config.get("scopus", "api_key")
a = Elsevier(author_id = '55409988300', api_key=api_key)
res = a.print_article_list()
for item in res:
    print(item)

#**************************************************************************