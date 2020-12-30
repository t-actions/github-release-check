#!/usr/bin/env python3
import os
import sys
import json
import logging
import argparse
import requests
import urllib.parse


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', default = os.environ.get('GITHUB_TOKEN'))
    parser.add_argument('-r', '--repo', default = os.environ.get('GITHUB_REPOSITORY'))
    parser.add_argument('-s', '--stream', action = 'store_true')
    parser.add_argument('-f', '--force', action = 'store_true')
    parser.add_argument('-x', '--proxy')
    parser.add_argument('tags', nargs = '*')

    return parser.parse_args()


def download_assets(release_url: str, args: argparse.Namespace, sess: requests.Session):
    r = sess.get(release_url)
    r.raise_for_status()

    content = r.json()

    folder = content['tag_name']
    os.makedirs(folder, exist_ok = True)
    for asset in content['assets']:
        filename = os.path.join(folder, asset['name'])
        if not args.force and os.path.exists(filename):
            logging.debug(f'Skip {filename}')
            continue

        headers = {'Accept': 'application/octet-stream'}
        if os.path.exists(filename):
            if args.stream and os.path.isfile(filename):
                headers['Range'] = f'bytes={os.stat(filename).st_size}-'
            else:
                os.remove(filename)

        with sess.get(
                asset['url'],
                headers = headers,
                stream = args.stream,
        ) as response:
            response.raise_for_status()

            if args.stream:
                with open(filename, 'ab+') as fout:
                    for content in response.iter_content():
                        fout.write(content)
            else:
                with open(filename, 'wb') as fout:
                    fout.write(response.content)
            logging.info(f'Downloaded {filename}')
    
    return folder


def main():
    args = parse_arg()

    if not args.token:
        logging.error('Cannot find env "GITHUB_TOKEN"')
        sys.exit(1)

    if not args.repo:
        logging.error('Cannot find env "GITHUB_REPOSITORY"')
        sys.exit(1)

    folders = []
    with requests.session() as sess:
        sess.headers['Authorization'] = f'Bearer {args.token}'
        if args.proxy:
            sess.proxies = {
                'http': args.proxy,
                'https': args.proxy,
            }
        sess.mount('http://', requests.adapters.HTTPAdapter(max_retries = 5))
        sess.mount('https://', requests.adapters.HTTPAdapter(max_retries = 5))

        for tag in args.tags or [
                f'https://api.github.com/repos/{args.repo}/releases/latest'
        ]:
            url = urllib.parse.urljoin(
                f'https://api.github.com/repos/{args.repo}/releases/tags/',
                tag,
            )
            folders.append(download_assets(url, args, sess))

    


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
        datefmt = '%Y-%m-%d %X',
    )

    main()
