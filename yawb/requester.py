from urllib.parse import urljoin
import requests
            
class HTTPRequester():

    def __init__(self, verify=False, user_agent=None):
        self.verify = verify
        self.headers = {}
        if user_agent:
            self.headers["User-Agent"] = user_agent

    def request(self, url):
        while True:
            resp = self._req(url)

            if resp.status_code in [301, 302, 303, 307, 308]:
                redir_url = resp.headers["Location"]
                new_url = urljoin(url, redir_url)

                if is_url_to_the_same_resource(url, new_url):
                    url = new_url
                    continue
            else:
                return url, resp

    def _req(self, url):
        return requests.get(
            url,
            verify=self.verify,
            headers=self.headers,
        )

def is_url_to_the_same_resource(url1, url2):
    url1 = url1.lower()
    url2 = url2.lower()
    
    # Is just adding a slash?
    if url1 == url2 + "/":
        return True

    # Is just removing a slash?
    if url2 == url1 + "/":
        return True


    # Is a change of scheme? Like from HTTP to HTTPS
    scheme1, rest1 = url1.split("://", 1)
    scheme2, rest2 = url2.split("://", 1)
    if rest1 == rest2:
        return True

    return False
