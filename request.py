import requests
import yaml

with open('config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def get(*args, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['appid'] = config['api']['appid']
    kwargs['headers']['appsecret'] = config['api']['appsecret']
    return requests.get(*args, **kwargs)
