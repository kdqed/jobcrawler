from datetime import datetime
import json
import re
from urllib.parse import urljoin
from w3lib.html import get_base_url

from bs4 import BeautifulSoup
import extruct


HTML_TAG_RE = re.compile(r"<[^>]+>")
def _strip_tags(text):
    if not text:
        return ""
    text = text.replace("&nbsp;", " ")
    return HTML_TAG_RE.sub("", text)


class Generic:

    @staticmethod
    def parse_board(board_url, html_content):
        soup = BeautifulSoup(html_content, features='html5lib')
        base_url = '/'.join(board_url.split('/')[:3])
        all_urls = [el.get('href').split("?")[0] for el in soup.find_all('a', href=True)]
        all_urls = [urljoin(base_url, url) for url in all_urls]
        return list(set(filter(
            lambda url: url.startswith(board_url) and len(url) > len(board_url),
            all_urls
        )))


    @staticmethod
    def parse_job(job_url, html_content):
        base_url = get_base_url(job_url, html_content)
        edata = extruct.extract(html_content, base_url=base_url)

        result = {'url': job_url}
        for d in edata.get('json-ld', []):
            if d.get('@type') == 'JobPosting':
                result['raw_content'] = json.dumps(d)
                result['title'] = d['title']
                result['org_name'] = d['hiringOrganization']['name']
                result['org_logo'] = d['hiringOrganization'].get('logo')
                if d.get('jobLocationType', '')=='telecommute':
                    result['is_remote'] = True
                    result['loc_locality'] = None
                    result['loc_region'] = None
                    result['loc_country'] = None
                    result['loc_postcode'] = None
                else:    
                    result['is_remote'] = False
                    job_location = d.get('jobLocation')
                    if type(job_location) is list:
                        job_location = (job_location or [{}])[0]
                    elif type(job_location) is None:
                        job_location = {}
                    address = job_location.get('address', {})
                    result['loc_locality'] = address.get('addressLocality')
                    result['loc_region'] = address.get('addressRegion')
                    result['loc_country'] = address.get('addressCountry')
                    result['loc_postcode'] = address.get('postalCode')
                result['employment_type'] = (d.get('employmentType') or '').lower() or None
                result['date_posted'] = datetime.fromisoformat(d['datePosted'])
                result['valid_through'] = datetime.fromisoformat(d['validThrough']) if 'validThrough' in d else None
                result['description'] = _strip_tags(d.get('description'))
                return result

        raise Exception('No Job Schema')


class Lever(Generic):
    pass


class Greenhouse(Generic):
    pass


class Ashby(Generic):
    pass


parsers = dict(
    ashby = Ashby,
    greenhouse = Greenhouse,
    lever = Lever,
)