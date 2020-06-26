import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlparse, urljoin
import json
from fake_useragent import UserAgent
from datetime import date
import concurrent.futures
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib.parse import unquote


def getdata(url):
    domain_name = urlparse(url).netloc
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    while True:
        try:
            session = requests.Session()
            session.headers.update(headers)
            retries = Retry(total=5, backoff_factor=1,
                            status_forcelist=[429, 500, 502, 503])
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            res = session.get(
                url, allow_redirects=True, timeout=15)
            res.raise_for_status()
        except:
            pass

        else:
            internal_urls = []
            external_urls = []
            soup = BeautifulSoup(res.content, "html.parser")
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    continue
                if href == "#" or href == "/":
                    continue
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

                if (parsed_href.scheme == 'invalid-title'):
                    continue
                if not is_valid(href):
                    continue
                if href in internal_urls:
                    continue
                if domain_name not in href:
                    if href not in external_urls:
                        encode_href = unquote(href)
                        external_urls.append(encode_href)
                    continue
                encode_href = unquote(href)
                internal_urls.append(encode_href)

            print('External Urls = ', external_urls, '\n')
            print('Internal Urls = ', internal_urls, '\n')

        break


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


if __name__ == "__main__":
    start_time = time.time()

    try:
        urls = ['https://www.self.com/food',
                'https://www.britannica.com/topic/food']
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            list(tqdm(pool.map(getdata, urls), total=len(urls)))
    except Exception as e:
        print(e)

    print("--- %s seconds ---" % round(time.time() - start_time, 2))
