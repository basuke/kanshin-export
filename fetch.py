import sys
from kanshin.keyword import DetailPage as KeywordPage, ListPage as KeywordListPage
import json
import re

def fetch_keywords(user_id, offset=0, limit=10000):
    list_page = KeywordListPage(user_id)
    keywords = []
    for url in list_page.keyword_pages()[offset:limit]:
        print(url)
        match = re.search('''^/keyword/(\d+)''', url)
        if match:
            keyword_id = int(match.group(1))
            keyword = KeywordPage(keyword_id)
            print(keyword_id, keyword.title)
            keywords.append(keyword.record)

    return keywords

def main(user_id=0):
    user_id = int(user_id)
    if user_id <= 0:
        usage()
        sys.exit()

    keywords = fetch_keywords(user_id)
    print(json.dumps(keywords, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main(*sys.argv[1:])
