import argparse
import uuid
from . import readin
import sys

from .logger import logger, init_log
from urllib.parse import urlparse

from . import validators
from .printer import RespPrinter
from .requester import HTTPRequester

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Webiste path bruter to find hidden resources."
    )

    parser.add_argument(
        "base_url",
        help="URL to inspect. If none provided stdin is used",
        nargs="*"
    )

    parser.add_argument(
        "-w", "--wordlist",
        help="File with directory or files per line",
        required=False,
        nargs="*"
    )

    parser.add_argument(
        "-A", "--user-agent",
        help="User agent to use in requests",
    )

    parser.add_argument(
        "-s", "--match-codes",
        nargs="+",
        help="Status codes to accept",
        metavar="CODE",
        type=int,
        default=[]
    )

    parser.add_argument(
        "-S", "--filter-codes",
        help="Status codes to reject",
        metavar="CODE",
        nargs="+",
        type=int,
        default=[],
    )

    parser.add_argument(
        "--match-size",
        type=size_range,
        help="Size of responses to accept (e.g. 94 100-200 300-* *-600)",
        nargs="+",
        default=[],
    )

    parser.add_argument(
        "--filter-size",
        type=size_range,
        help="Size of responses to reject (e.g. 94 100-200 300-* *-600)",
        nargs="+",
        default=[],
    )

    print_group = parser.add_argument_group("Print options")

    print_group.add_argument(
        "-j", "--json",
        help="Print results in jsonl",
        action="store_true",
    )

    print_group.add_argument(
        "--print-code",
        help="Print status code of response",
        action="store_true",
    )

    print_group.add_argument(
        "--print-size",
        help="Print size of of response",
        action="store_true",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Verbosity",
        default=0
    )

    return parser.parse_args()

def size_range(v):
    parts = v.split("-")

    if len(parts) == 1:
        min_size = int(parts[0])
        max_size = min_size
        
    elif len(parts) == 2:
        if parts[0] == "*":
            min_size = 0
        else:
            min_size = int(parts[0])

        if parts[1] == "*":
            max_size = sys.maxsize
        else:
            max_size = int(parts[1])
    else:
        raise ValueError(
            "Too many parts in size {}, just specify min and max".format(v)
        )

    return (min_size, max_size)

def main():
    args = parse_args()
    init_log(args.verbose)
    
    user_validator = validators.generate_validator(
        match_status_codes=args.match_codes,
        filter_status_codes=args.filter_codes,
        match_sizes=args.match_size,
        filter_sizes=args.filter_size,
    )

    requester = HTTPRequester(
        user_agent=args.user_agent,
    )

    printer = RespPrinter(
        format_json=args.json,
        print_code=args.print_code,
        print_size=args.print_size,
    )

    paths = read_wordlist(args.wordlist)
    if not paths:
        logger.warning("No wordlist was provided, testing the URLs alone")
        paths = [""]
    else:
        logger.info("{} paths read from the wordlists".format(len(paths)))

    try:
        for base_url in readin.read_text_targets(args.base_url):
            try:
                brute_web(base_url, paths, requester, printer, user_validator)
            except InvalidValidator as e:
                logger.warning(e)
    except KeyboardInterrupt:
        pass
            
def is_valid_url(url_str):
    url = urlparse(url_str)
    if url.scheme not in ["http", "https"]:
        return False

    if not url.hostname:
        return False

    return True

def read_wordlist(wordlist):
    return list(readin.read_text_targets(
        wordlist,
        use_stdin_if_none=False,
        remove_empty=False,
        remove_comments=False,
    ))

class InvalidUrlError(Exception):
    pass

class InvalidValidator(Exception):
    pass

def brute_web(base_url, paths, requester, printer, user_validator):
    if not is_valid_url(base_url):
        raise logger.warning("Not valid url {}".format(base_url))

    if not base_url.endswith("/"):
        base_url += "/"

    validator = choose_validator(base_url, requester, user_validator)

    for path in paths:
        url = base_url + path
        logger.info("Testing {}".format(url))
        resp_url, resp = requester.request(url)
        try:
            validator.validate_response(resp)
        except validators.InvalidResponseError:
            continue

        printer.print_result(resp_url, resp)
        

def choose_validator(base_url, requester, user_validator):
    uuid = gen_random_uuid()
    url = base_url + uuid

    resp_url, resp = requester.request(url)

    if user_validator:
        logger.debug("Testing user validator: {}".format(
            user_validator.describe_condition()
        ))
        try:
            user_validator.validate_response(resp)
            logger.debug("User validator didn't work")
        except validators.InvalidResponseError:
            logger.debug("User validator works")
            return user_validator

    basic_validator = validators.StatusCodeValidator([200])
    logger.debug("Testing basic validator: {}".format(
        basic_validator.describe_condition()
    ))
    try:
        basic_validator.validate_response(resp)
        logger.debug("Default validator didn't work")
    except validators.InvalidResponseError:
        logger.debug("Default validator works")
        return basic_validator
    
    
    ai_validator = validators.AiValidator()
    logger.debug("Testing AI validator")
    try:
        ai_validator.validate_response(resp)
        logger.debug("AI validator didn't work")
    except validators.InvalidResponseError:
        logger.debug("AI validator works")
        return ai_validator

    raise InvalidValidator(
        "Your options doesn't correctly filter the test url {}."
        " Try to set --filter-size {} or --filter-code {}".format(
            url, len(resp.content), resp.status_code
        )
    )

def gen_random_uuid():
    return str(uuid.uuid4())



