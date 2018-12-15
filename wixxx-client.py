import argparse
import hashlib
import os
import requests


DEFAULT_SERVER = 'http://localhost:8000'

def parse_args():
    parser = argparse.ArgumentParser(
        description='Submit wixxx data to the wixxx app')
    parser.add_argument(
        '--server',
        dest='server',
        default=DEFAULT_SERVER,
        help='The server to submit to')
    parser.add_argument(
        'logfile',
        type=argparse.FileType('r'),
        help='''The log file containing the dump of the wixxx
        output (and nothing else)''')
    parser.add_argument(
        'user',
        nargs='?',
        help='Your username on the wixxx server',
        default=os.environ.get('WIXXX_USER'))
    parser.add_argument(
        'secret',
        nargs='?',
        help='Your user secret (not your password) on the wixxx server',
        default=os.environ.get('WIXXX_SECRET'))
    return parser.parse_args()

def main(options):
    nonce_request = requests.get('{}/request-nonce/{}/'.format(options.server, options.user))
    nonce = nonce_request.content.decode('utf-8')
    token = hashlib.sha256('{}:{}'.format(options.secret, nonce).encode()).hexdigest()
    post_request = requests.post('{}/accept-flags/{}/'.format(options.server, options.user), {
        'token': token,
        'data': options.logfile.read(),
    })
    print(post_request.content.decode('utf-8'))

if __name__ == '__main__':
    args = parse_args()
    main(args)
