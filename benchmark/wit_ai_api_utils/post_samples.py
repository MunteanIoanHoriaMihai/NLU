import json
import requests
import argparse
import configparser
import datetime
import time

url = ''
TOKEN = ''
ACCEPTED_SAMPLES_NR = 200


def read_config_file(config_file):
    global url
    global TOKEN
    config = configparser.ConfigParser()
    config.read(config_file)
    url = config['URL']['post_samples_url']
    TOKEN = config['TOKEN']['token']


def post_samples(input_file):
    global url
    now = datetime.datetime.now()
    url = url + str(now.year) + '{num:02d}'.format(num=now.month) + '{num:02d}'.format(num=now.day)
    print(url)
    print(TOKEN)
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json'
    }

    with open(input_file) as inf:
        json_data = json.loads(inf.read())

    samples_to_post = [json_data[0]]
    print(samples_to_post)

    for sample in json_data:
        for entity in sample['entities']:
            entity['entity'] = str(entity['entity']).replace('.', '_')

    for i in range(0, int(len(json_data) / ACCEPTED_SAMPLES_NR) + 1):
        lower_limit = i * ACCEPTED_SAMPLES_NR
        upper_limit = lower_limit + ACCEPTED_SAMPLES_NR
        if upper_limit > len(json_data):
            upper_limit = len(json_data)
        samples_to_post = json_data[lower_limit:upper_limit]

        try:
            r = requests.post(url, data=json.dumps(samples_to_post), headers=headers)
            print(r.content)
            if r.status_code != 200:
                print(str(lower_limit + " : " + upper_limit))
            # wit ai imposes a limit of 200 samples per minute posted, hence the timeout
            time.sleep(60)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description="Posts samples to Wit.ai",
                usage="post_entities.py <config_file> <input_file> <failed_samples_file> <app_name>")
    parser.add_argument('config_file', help='Config file')
    parser.add_argument('input_file', help='Input file')
    args = parser.parse_args()
    read_config_file(args.config_file)
    post_samples(input_file=args.input_file)

