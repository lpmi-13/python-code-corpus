import requests
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-L", "--language", help="specify the programming language")

args = parser.parse_args()

if args.language is not None:
    language = sys.argv[1]
    print('language is {}'.format(language))
    r = requests.get('https://api.github.com/search/repositories?q=language:{}&stars:%3E0&sort=stars&per_page=100'.format(language))
    data = r.json()
    url_set = {result['html_url'] for result in data['items']}

    with open('{}_repo_urls.txt'.format(language), 'w') as url_file:
        for result in url_set:
            url_file.write(result)
            url_file.write('\n')
        
else:
    print('please specify a language')
    sys.exit() 

