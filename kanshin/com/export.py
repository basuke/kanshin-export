from kanshin.data import has_image, save_image
from robobrowser.compat import urlparse
import requests

def import_image(url):
    path = urlparse.urlparse(url).path[1:]

    if not has_image(path):
        response = requests.get(url)
        if response.status_code != 200:
            return url

        content = response.content
        content_type = response.headers['Content-Type']
        save_image(path, content_type, content)

    return 'http://s.kanshin.link' + path

