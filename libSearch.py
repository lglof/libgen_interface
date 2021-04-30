#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import argparse
import os
import sys
import requests
from tqdm import tqdm
from libgen_api import LibgenSearch
from PyInquirer import prompt, print_json, Separator


s = LibgenSearch()
parser = argparse.ArgumentParser(
    prog='libSearch',
    usage='%(prog)s [options] query',
    description='working with libgen from command line')


parser.add_argument('query',
                    type=str,
                    help='title to search')
parser.add_argument('-p', '--pdf',
                    action='store_true',
                    help='pdf flag')
parser.add_argument('-a', '--author',
                    action='store_true',
                    help='search by author flag')

args = parser.parse_args()
filters = {'Extension': 'pdf' if args.pdf else 'epub', 'Language': 'English'}

if args.author:
    # search by author
    titles = s.search_author_filtered(args.query, filters, exact_match=True)
else:
    # search by title
    titles = s.search_title_filtered(args.query, filters, exact_match=True)

choices = []

for i in range(len(titles)):
    index = str(i).zfill(2)
    author = "{:<30}".format(titles[i]["Author"][0:30])
    title = "{:<70}".format(titles[i]["Title"][0:70])
    out = f"{index} | {author} | {title}"
    choices.append(out)

questions = [
    {
        'type': 'list',
        'name': 'chosen_book',
        'message': 'Available books:',
        'choices': choices
    },
]

answer = prompt(questions)
chosen_book = titles[int(answer["chosen_book"][0:2])]
chosen_url = s.resolve_download_links(chosen_book)['GET']

file_name = f"downloaded/{chosen_book['Title']}.{filters['Extension']}"
print(f"Downloading to: {file_name}")

chunk_size = 1024
r = requests.get(chosen_url, stream=True)
total_length = int(r.headers.get('content-length'))

with open(file_name, 'wb') as out:
    for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size), total=total_length/chunk_size, unit='KB'):
        out.write(data)

print("Download complete!")
