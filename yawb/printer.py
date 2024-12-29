import json

class RespPrinter():

    def __init__(
            self,
            print_code=False,
            print_size=False,
            format_json=False
    ):
        self.print_size = print_size
        self.print_code = print_code
        self.format_json = format_json

    def print_result(self, url, resp):
        if self.format_json:
            self._print_json(url, resp)
        else:
            self._print_text(url, resp)

    def _print_json(self, url, resp):
        items = {
            "url": url,
        }

        if self.print_code:
            items["code"] = resp.status_code

        if self.print_size:
            items["size"] = len(resp.content)

        print(json.dumps(items), flush=True)
            
    def _print_text(self, url, resp):
        items = [url]
        if self.print_code:
            items.append(str(resp.status_code))
        if self.print_size:
            items.append(str(len(resp.content)))

        print(" ".join(items), flush=True)
        
