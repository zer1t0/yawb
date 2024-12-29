# yawb

yawb (Yet Another Web Bruter) is a website path bruteforcer that can be used to
find hidden resources.

The novelty of yawb is the use of an AI model to identify error webpages without
relying in the status code. If you are interesting in the model creation, check
https://github.com/zer1t0/tfm .

## Installation

To install yawb you must download it and install the required packages:
```
git clone https://github.com/zer1t0/yawb
cd yawb/
pip3 install -r requirements.txt
```

## Usage

Just feed yawb with URLs:
```
cat /tmp/urls.txt | ./yawb.py -w common.txt
```

Help usage:
```
$ ./yawb.py -h
usage: yawb.py [-h] [-w [WORDLIST ...]] [-A USER_AGENT] [-s CODE [CODE ...]]
               [-S CODE [CODE ...]] [--match-size MATCH_SIZE [MATCH_SIZE ...]]
               [--filter-size FILTER_SIZE [FILTER_SIZE ...]] [-j] [--print-code]
               [--print-size] [--verbose]
               base_url [base_url ...]

Webiste path bruter to find hidden resources.

positional arguments:
  base_url              URL to inspect

options:
  -h, --help            show this help message and exit
  -w [WORDLIST ...], --wordlist [WORDLIST ...]
                        File with directory or files per line
  -A USER_AGENT, --user-agent USER_AGENT
                        User agent to use in requests
  -s CODE [CODE ...], --match-codes CODE [CODE ...]
                        Status codes to accept
  -S CODE [CODE ...], --filter-codes CODE [CODE ...]
                        Status codes to reject
  --match-size MATCH_SIZE [MATCH_SIZE ...]
                        Size of responses to accept (e.g. 94 100-200 300-* *-600)
  --filter-size FILTER_SIZE [FILTER_SIZE ...]
                        Size of responses to reject (e.g. 94 100-200 300-* *-600)
  --verbose, -v         Verbosity

Print options:
  -j, --json            Print results in jsonl
  --print-code          Print status code of response
  --print-size          Print size of of response
```

## Useful dictionaries

- [SecLists/Discovery/Web-Content](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content)

## Similar tools

- [gobuster](https://github.com/OJ/gobuster)
- [wfuzz](https://github.com/xmendez/wfuzz)
- [ffuf](https://github.com/ffuf/ffuf)
- [dirbuster](https://sourceforge.net/projects/dirbuster/)
