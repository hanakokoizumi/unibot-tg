import datetime
import hashlib
import json
import time

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from zhconv import convert

import requests
from requests.adapters import HTTPAdapter
import os
import threading
import subprocess


def time_printer(string):
    time_array = time.localtime(time.time())
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    print(time_str, string)


def detect_play_data():
    time_printer('检查playdata更新')
    try:
        json_data = requests.get('https://gitlab.com/pjsekai/database/musics/-/raw/main/musicDifficulties.json')
        json.loads(json_data.text)
    except:
        print('playdata下载失败')
        return

    with open('./assets/static/masterdata/realtime/musicDifficulties.json',
              'rb') as f:
        data = f.read()
    if hashlib.md5(data).hexdigest() != hashlib.md5(json_data.content).hexdigest():
        print('更新musicDifficulties.json')
        with open("./assets/static/masterdata/realtime/musicDifficulties.json",
                  "wb") as f:
            f.write(json_data.content)

    try:
        json_data = requests.get('https://gitlab.com/pjsekai/database/musics/-/raw/main/musics.json')
        json.loads(json_data.text)
    except:
        print('playdata下载失败')
        return

    with open('./assets/static/masterdata/realtime/musics.json', 'rb') as f:
        data = f.read()
    if hashlib.md5(data).hexdigest() != hashlib.md5(json_data.content).hexdigest():
        print('更新musics.json')
        with open("./assets/static/masterdata/realtime/musics.json", "wb") as f:
            f.write(json_data.content)


def get_file_ctime(file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file))


def clean_cache(path='temp/'):
    now_time = datetime.datetime.now()
    del_time = datetime.timedelta(seconds=300)
    nd = now_time - del_time
    for file in os.listdir('temp/'):
        if file[-4:] == '.png' or file[-4:] == '.mp3' or file[-4:] == '.jpg':
            file_ctime = get_file_ctime(path + file)
            if file_ctime < nd:
                os.remove(path + file)


def update_translate(raw, value):
    with open('./data/translate.yaml', encoding='utf-8') as f:
        translation = yaml.load(f, Loader=yaml.FullLoader)
    if translation[value] is None:
        translation[value] = {}
    try:
        request = requests.get(f'https://raw.githubusercontent.com/Sekai-World/sekai-i18n/main/zh-TW/{raw}.json')
        data = request.json()
    except:
        print(raw + '翻译下载失败')
        return

    for i in data:
        try:
            translation[value][int(i)]
        except (KeyError, IndexError):
            zh_translate = convert(data[i], 'zh-cn')
            translation[value][int(i)] = zh_translate
            print('更新翻译', value, i, zh_translate)
    with open('./data/translate.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(translation, f, allow_unicode=True)


def update_all_trans():
    time_printer('检查新增翻译')
    update_translate('music_titles', 'musics')
    update_translate('event_name', 'events')
    update_translate('card_prefix', 'card_prefix')
    update_translate('cheerful_carnival_teams', 'cheerfulCarnivalTeams')
    time_printer('完成')


def update_master_data():
    if os.path.exists('./assets/static/masterdata/'):
        p = subprocess.Popen('git pull', shell=True, cwd='./assets/static/masterdata/')
    else:
        p = subprocess.Popen('git clone https://github.com/Sekai-World/sekai-master-db-diff masterdata', shell=True, cwd='./assets/static/')
    p.wait()


def download_online_data():

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    url = 'https://api.pjsek.ai/assets?parent=%s&$limit=10000&$sort[isDir]=-1&$sort[path]=1'
    asset_url = 'https://assets.pjsek.ai/file/pjsekai-assets/%s'
    files = []

    pool = [('', 'dir')]
    base = './assets/online/'

    def download(path, type):
        global pool
        if type == 'dir':
            data = s.get(url % path).json()['data']
            if path and not os.path.exists(os.path.join(base, path)):
                os.mkdir(os.path.join(base, path))
            pool.extend([(item['path'], item['isDir'] and 'dir' or 'file') for item in data if
                         item['path'].endswith('.png') or item['isDir']])
        else:
            files.append(path)
            if os.path.exists(os.path.join(base, path)):
                return
            print('Downloading: %s' % path)
            resp = s.get(asset_url % path)
            if resp.status_code == 200:
                with open(os.path.join(base, path), 'wb') as f:
                    f.write(resp.content)

    if __name__ == '__main__':
        threads = []
        while len(pool) > 0:
            print(f'Pool size: {len(pool)}')
            for i in range(len(pool[:150])):
                path, type = pool.pop(0)
                t = threading.Thread(target=download, args=(path, type))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            threads = []


if __name__ == '__main__':
    # clean_cache()
    update_master_data()
    detect_play_data()
    update_all_trans()
    scheduler = BlockingScheduler()
    scheduler.add_job(update_master_data, 'interval', hours=2, id='update_master_data')
    scheduler.add_job(detect_play_data, 'interval', seconds=300, id='play_info_check')
    # scheduler.add_job(clean_cache, 'interval', seconds=300, id='clean_cache')
    scheduler.add_job(update_all_trans, 'interval', hours=2, id='update_all_trans')
    scheduler.start()
