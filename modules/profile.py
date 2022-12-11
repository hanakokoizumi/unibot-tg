import io
import json
import os.path
import time
from PIL import Image as PILImage
from PIL import ImageFont, ImageDraw
import request as requests
import yaml

asset_path = 'assets/online'
rank_match_grades = {
    1: 'ビギナー(初学者)',
    2: 'ブロンズ(青铜)',
    3: 'シルバー(白银)',
    4: 'ゴールド(黄金)',
    5: 'プラチナ(白金)',
    6: 'ダイヤモンド(钻石)',
    7: 'マスター(大师)'
}

with open('config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class Image:
    @classmethod
    def open(cls, *args, **kwargs):
        try:
            return PILImage.open(*args, **kwargs)
        except FileNotFoundError as e:
            print(e.filename + " not found")
            if e.filename.startswith(asset_path):
                filename = e.filename.replace(asset_path + '/', '')
                if not os.path.exists(os.path.abspath(os.path.join(e.filename, '..'))):
                    os.makedirs(os.path.abspath(os.path.join(e.filename, '..')))
                resp = requests.get('https://assets.pjsek.ai/file/pjsekai-assets/%s' % filename)
                if resp.status_code == 200:
                    with open(e.filename, 'wb') as f:
                        f.write(resp.content)
                    return PILImage.open(*args, **kwargs)
            else:
                raise e


class UserProfile(object):
    def __init__(self):
        self.name = ''
        self.rank = 0
        self.userid = ''
        self.twitterId = ''
        self.word = ''
        self.userDecks = [0, 0, 0, 0, 0]
        self.special_training = [False, False, False, False, False]
        self.full_perfect = [0, 0, 0, 0, 0]
        self.full_combo = [0, 0, 0, 0, 0]
        self.clear = [0, 0, 0, 0, 0]
        self.mvpCount = 0
        self.superStarCount = 0
        self.userProfileHonors = {}
        self.characterRank = {}
        self.characterId = 0
        self.highScore = 0
        self.masterscore = {}
        self.expertscore = {}
        for i in range(26, 37):
            self.masterscore[i] = [0, 0, 0, 0]
        for i in range(21, 32):
            self.expertscore[i] = [0, 0, 0, 0]

    def getprofile(self, userid, server):
        masterdatadir = 'assets/static/masterdata'
        if server == 'jp':
            url = config['api']['base'] + '/jp/api'
        elif server == 'en':
            url = config['api']['base'] + '/en/api'
        elif server == 'tw':
            url = config['api']['base'] + '/tw/api'
        elif server == 'kr':
            url = config['api']['base'] + '/kr/api'
        resp = requests.get(f'{url}/user/{userid}/profile')
        data = json.loads(resp.content)
        self.name = data['user']['userGamedata']['name']
        try:
            self.twitterId = data['userProfile']['twitterId']
        except:
            pass

        self.userid = userid

        try:
            self.word = data['userProfile']['word']
        except:
            pass

        self.rank = data['user']['userGamedata']['rank']
        try:
            self.characterId = data['userChallengeLiveSoloResults'][0]['characterId']
            self.highScore = data['userChallengeLiveSoloResults'][0]['highScore']
        except:
            pass
        self.characterRank = data['userCharacters']

        self.userProfileHonors = data['userProfileHonors']
        # print(self.userProfileHonors)
        with open(f'{masterdatadir}/musics.json', 'r', encoding='utf-8') as f:
            allmusic = json.load(f)
        with open(f'{masterdatadir}/musicDifficulties.json', 'r', encoding='utf-8') as f:
            musicDifficulties = json.load(f)
        result = {}
        now = int(time.time() * 1000)
        for music in allmusic:
            result[music['id']] = [0, 0, 0, 0, 0]
            if music['publishedAt'] < now:
                found = [0, 0]
                for diff in musicDifficulties:
                    if music['id'] == diff['musicId'] and diff['musicDifficulty'] == 'expert':
                        playLevel = diff['playLevel']
                        self.expertscore[playLevel][3] = self.expertscore[playLevel][3] + 1
                        found[0] = 1
                    elif music['id'] == diff['musicId'] and diff['musicDifficulty'] == 'master':
                        playLevel = diff['playLevel']
                        self.masterscore[playLevel][3] = self.masterscore[playLevel][3] + 1
                        found[1] = 1
                    if found == [1, 1]:
                        break
        for music in data['userMusicResults']:
            musicId = music['musicId']
            musicDifficulty = music['musicDifficulty']
            playResult = music['playResult']
            self.mvpCount = self.mvpCount + music['mvpCount']
            self.superStarCount = self.superStarCount + music['superStarCount']
            if musicDifficulty == 'easy':
                diffculty = 0
            elif musicDifficulty == 'normal':
                diffculty = 1
            elif musicDifficulty == 'hard':
                diffculty = 2
            elif musicDifficulty == 'expert':
                diffculty = 3
            else:
                diffculty = 4
            if playResult == 'full_perfect':
                if result[musicId][diffculty] < 3:
                    result[musicId][diffculty] = 3
            elif playResult == 'full_combo':
                if result[musicId][diffculty] < 2:
                    result[musicId][diffculty] = 2
            elif playResult == 'clear':
                if result[musicId][diffculty] < 1:
                    result[musicId][diffculty] = 1
        for music in result:
            for i in range(0, 5):
                if result[music][i] == 3:
                    self.full_perfect[i] = self.full_perfect[i] + 1
                    self.full_combo[i] = self.full_combo[i] + 1
                    self.clear[i] = self.clear[i] + 1
                elif result[music][i] == 2:
                    self.full_combo[i] = self.full_combo[i] + 1
                    self.clear[i] = self.clear[i] + 1
                elif result[music][i] == 1:
                    self.clear[i] = self.clear[i] + 1
                if i == 4:
                    for diff in musicDifficulties:
                        if music == diff['musicId'] and diff['musicDifficulty'] == 'master':
                            playLevel = diff['playLevel']
                            break
                    if result[music][i] == 3:
                        self.masterscore[playLevel][0] += 1
                        self.masterscore[playLevel][1] += 1
                        self.masterscore[playLevel][2] += 1
                    elif result[music][i] == 2:
                        self.masterscore[playLevel][1] += 1
                        self.masterscore[playLevel][2] += 1
                    elif result[music][i] == 1:
                        self.masterscore[playLevel][2] += 1
                elif i == 3:
                    for diff in musicDifficulties:
                        if music == diff['musicId'] and diff['musicDifficulty'] == 'expert':
                            playLevel = diff['playLevel']
                            break
                    if result[music][i] == 3:
                        self.expertscore[playLevel][0] += 1
                        self.expertscore[playLevel][1] += 1
                        self.expertscore[playLevel][2] += 1
                    elif result[music][i] == 2:
                        self.expertscore[playLevel][1] += 1
                        self.expertscore[playLevel][2] += 1
                    elif result[music][i] == 1:
                        self.expertscore[playLevel][2] += 1
        for i in range(0, 5):
            self.userDecks[i] = data['userDecks'][0][f'member{i + 1}']
            for userCards in data['userCards']:
                if userCards['cardId'] != self.userDecks[i]:
                    continue
                if userCards['defaultImage'] == "special_training":
                    self.special_training[i] = True


def pjsk_process(userid, private=False, diff='master', server='jp'):
    profile = UserProfile()
    profile.getprofile(userid, server)
    if private:
        id = '保密'
    else:
        id = userid
    if diff == 'master':
        img = Image.open('assets/static/pics/bgmaster.png')
    else:
        img = Image.open('assets/static/pics/bgexpert.png')
    with open('assets/static/masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    assetbundleName = ''
    for i in cards:
        if i['id'] == profile.userDecks[0]:
            assetbundleName = i['assetbundleName']
    if profile.special_training[0]:
        cardimg = Image.open('assets/online'
                             f'/startapp/thumbnail/chara/{assetbundleName}_after_training.png')
    else:
        cardimg = Image.open('assets/online'
                             f'/startapp/thumbnail/chara/{assetbundleName}_normal.png')
    cardimg = cardimg.resize((117, 117))
    r, g, b, mask = cardimg.split()
    img.paste(cardimg, (67, 57), mask)
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype("assets/static/fonts/SourceHanSansCN-Bold.otf", 31)
    draw.text((216, 55), profile.name, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 15)
    draw.text((216, 105), 'id:' + id, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 26)
    draw.text((314, 138), str(profile.rank), fill=(255, 255, 255), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/SourceHanSansCN-Bold.otf", 35)
    if diff == 'master':
        levelmin = 26
    else:
        levelmin = 21
        profile.masterscore = profile.expertscore
    for i in range(0, 6):
        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][0]))
        text_coordinate = (int(183 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][0]), fill=(228, 159, 251), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][1]))
        text_coordinate = (int(183 + 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][1]), fill=(254, 143, 249), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][2]))
        text_coordinate = (int(183 + 2 * 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][2]), fill=(255, 227, 113), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][3]))
        text_coordinate = (int(183 + 3 * 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][3]), fill=(108, 237, 226), font=font_style)

    for i in range(0, 5):
        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][0]))
        text_coordinate = (int(683 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][0]), fill=(228, 159, 251), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][1]))
        text_coordinate = (int(683 + 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][1]), fill=(254, 143, 249), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][2]))
        text_coordinate = (int(683 + 2 * 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][2]), fill=(255, 227, 113), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][3]))
        text_coordinate = (int(683 + 3 * 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][3]), fill=(108, 237, 226), font=font_style)
    img_byte = io.BytesIO()
    img.save(img_byte, format='PNG')
    return img_byte.getvalue()


def pjsk_profile(userid, private=False, server='jp'):
    profile = UserProfile()
    profile.getprofile(userid, server)
    if private:
        id = '保密'
    else:
        id = userid
    img = Image.open('assets/static/pics/bg.png')
    with open('./assets/static/masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    assetbundleName = ''
    for i in cards:
        if i['id'] == profile.userDecks[0]:
            assetbundleName = i['assetbundleName']
    if profile.special_training[0]:
        cardimg = Image.open('assets/online'
                             f'/startapp/thumbnail/chara/{assetbundleName}_after_training.png')
    else:
        cardimg = Image.open('assets/online'
                             f'/startapp/thumbnail/chara/{assetbundleName}_normal.png')
    cardimg = cardimg.resize((151, 151))
    r, g, b, mask = cardimg.split()
    img.paste(cardimg, (118, 51), mask)
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype("assets/static/fonts/SourceHanSansCN-Bold.otf", 45)
    draw.text((295, 45), profile.name, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 20)
    draw.text((298, 116), 'id:' + id, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 34)
    draw.text((415, 157), str(profile.rank), fill=(255, 255, 255), font=font_style)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 22)
    draw.text((182, 318), str(profile.twitterId), fill=(0, 0, 0), font=font_style)

    font_style = ImageFont.truetype("assets/static/fonts/SourceHanSansCN-Medium.otf", 24)
    size = font_style.getsize(profile.word)
    if size[0] > 480:
        draw.text((132, 388), profile.word[:int(len(profile.word) * (460 / size[0]))], fill=(0, 0, 0), font=font_style)
        draw.text((132, 424), profile.word[int(len(profile.word) * (460 / size[0])):], fill=(0, 0, 0), font=font_style)
    else:
        draw.text((132, 388), profile.word, fill=(0, 0, 0), font=font_style)

    for i in range(0, 5):
        assetbundleName = ''
        for j in cards:
            if j['id'] == profile.userDecks[i]:
                assetbundleName = j['assetbundleName']
        if profile.special_training[i]:
            cardimg = Image.open('assets/online'
                                 f'/startapp/thumbnail/chara/{assetbundleName}_after_training.png')
        else:
            cardimg = Image.open('assets/online'
                                 f'/startapp/thumbnail/chara/{assetbundleName}_normal.png')
        # cardimg = cardimg.resize((151, 151))
        r, g, b, mask = cardimg.split()
        img.paste(cardimg, (111 + 128 * i, 488), mask)
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 27)
    for i in range(0, 5):
        text_width = font_style.getsize(str(profile.clear[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.clear[i]), fill=(0, 0, 0), font=font_style)

        text_width = font_style.getsize(str(profile.full_combo[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 + 133 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.full_combo[i]), fill=(0, 0, 0), font=font_style)

        text_width = font_style.getsize(str(profile.full_perfect[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 + 2 * 133 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.full_perfect[i]), fill=(0, 0, 0), font=font_style)

    character = 0
    font_style = ImageFont.truetype("assets/static/fonts/FOT-RodinNTLGPro-DB.ttf", 29)
    for i in range(0, 5):
        for j in range(0, 4):
            character = character + 1
            characterRank = 0
            for charas in profile.characterRank:
                if charas['characterId'] == character:
                    characterRank = charas['characterRank']
                    break
            text_width = font_style.getsize(str(characterRank))
            text_coordinate = (int(920 + 183 * j - text_width[0] / 2), int(686 + 88 * i - text_width[1] / 2))
            draw.text(text_coordinate, str(characterRank), fill=(0, 0, 0), font=font_style)
    for i in range(0, 2):
        for j in range(0, 4):
            character = character + 1
            characterRank = 0
            for charas in profile.characterRank:
                if charas['characterId'] == character:
                    characterRank = charas['characterRank']
                    break
            text_width = font_style.getsize(str(characterRank))
            text_coordinate = (int(920 + 183 * j - text_width[0] / 2), int(510 + 88 * i - text_width[1] / 2))
            draw.text(text_coordinate, str(characterRank), fill=(0, 0, 0), font=font_style)
            if character == 26:
                break
    draw.text((952, 141), f'{profile.mvpCount}回', fill=(0, 0, 0), font=font_style)
    draw.text((1259, 141), f'{profile.superStarCount}回', fill=(0, 0, 0), font=font_style)
    try:
        chara = Image.open(f'assets/static/chara/chr_ts_{profile.characterId}.png')
        chara = chara.resize((70, 70))
        r, g, b, mask = chara.split()
        img.paste(chara, (952, 293), mask)
        draw.text((1032, 315), str(profile.highScore), fill=(0, 0, 0), font=font_style)
    except:
        pass
    for i in profile.userProfileHonors:
        if i['seq'] == 1:
            try:
                honorpic = generate_honor(i, True, server)
                honorpic = honorpic.resize((266, 56))
                r, g, b, mask = honorpic.split()
                img.paste(honorpic, (104, 228), mask)
            except:
                pass

    for i in profile.userProfileHonors:
        if i['seq'] == 2:
            try:
                honorpic = generate_honor(i, False, server)
                honorpic = honorpic.resize((126, 56))
                r, g, b, mask = honorpic.split()
                img.paste(honorpic, (375, 228), mask)
            except:
                pass

    for i in profile.userProfileHonors:
        if i['seq'] == 3:
            try:
                honorpic = generate_honor(i, False, server)
                honorpic = honorpic.resize((126, 56))
                r, g, b, mask = honorpic.split()
                img.paste(honorpic, (508, 228), mask)
            except:
                pass
    img = img.convert('RGB')
    img_byte = io.BytesIO()
    img.save(img_byte, format='PNG', quality=80)
    return img_byte.getvalue()


def generate_honor(honor, ismain=True, server='jp'):
    star = False
    backgroundAssetbundleName = ''
    assetbundleName = ''
    groupId = 0
    honorRarity = 0
    honorType = ''
    try:
        honor['profileHonorType']
    except:
        honor['profileHonorType'] = 'normal'
    if server == 'jp':
        masterdatadir = './assets/static/masterdata'
    elif server == 'en':
        masterdatadir = './assets/static/masterdata'
    elif server == 'tw':
        masterdatadir = './assets/static/masterdata'
    if honor['profileHonorType'] == 'normal':
        # 普通牌子
        with open(f'{masterdatadir}/honors.json', 'r', encoding='utf-8') as f:
            honors = json.load(f)
        with open(f'{masterdatadir}/honorGroups.json', 'r', encoding='utf-8') as f:
            honorGroups = json.load(f)
        for i in honors:
            if i['id'] == honor['honorId']:
                assetbundleName = i['assetbundleName']
                groupId = i['groupId']
                honorRarity = i['honorRarity']
                try:
                    level2 = i['levels'][1]['level']
                    star = True
                except IndexError:
                    pass
                for j in honorGroups:
                    if j['id'] == i['groupId']:
                        try:
                            backgroundAssetbundleName = j['backgroundAssetbundleName']
                        except KeyError:
                            backgroundAssetbundleName = ''
                        honorType = j['honorType']
                        break
        filename = 'honor'
        mainname = 'rank_main.png'
        subname = 'rank_sub.png'
        if honorType == 'rank_match':
            filename = 'rank_live/honor'
            mainname = 'main.png'
            subname = 'sub.png'
        # 数据读取完成
        if ismain:
            # 大图
            if honorRarity == 'low':
                frame = Image.open('assets/static/pics/frame_degree_m_1.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_m_2.png')
            elif honorRarity == 'high':
                frame = Image.open('assets/static/pics/frame_degree_m_3.png')
            else:
                frame = Image.open('assets/static/pics/frame_degree_m_4.png')
            if backgroundAssetbundleName == '':
                rankpic = None
                pic = get_honor_asset(server, 'assets/online'
                                            f'/startapp/{filename}/{assetbundleName}/degree_main.png')
                rankpic = get_honor_asset(server, 'assets/online'
                                                f'/startapp/{filename}/{assetbundleName}/{mainname}')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                if rankpic is not None:
                    r, g, b, mask = rankpic.split()
                    pic.paste(rankpic, (190, 0), mask)
            else:
                pic = get_honor_asset(server, 'assets/online'
                                            f'/startapp/{filename}/{backgroundAssetbundleName}/degree_main.png')
                rankpic = get_honor_asset(server, 'assets/online'
                                                f'/startapp/{filename}/{assetbundleName}/{mainname}')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                r, g, b, mask = rankpic.split()
                pic.paste(rankpic, (190, 0), mask)
            if honorType == 'character' or honorType == 'achievement':
                honorlevel = honor['honorLevel']
                if star is True:
                    if honorlevel > 10:
                        honorlevel = honorlevel - 10
                    if honorlevel < 5:
                        for i in range(0, honorlevel):
                            lv = Image.open('assets/static/pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                    else:
                        for i in range(0, 5):
                            lv = Image.open('assets/static/pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                        for i in range(0, honorlevel - 5):
                            lv = Image.open('assets/static/pics/icon_degreeLv6.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
        else:
            # 小图
            if honorRarity == 'low':
                frame = Image.open('assets/static/pics/frame_degree_s_1.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_s_2.png')
            elif honorRarity == 'high':
                frame = Image.open('assets/static/pics/frame_degree_s_3.png')
            else:
                frame = Image.open('assets/static/pics/frame_degree_s_4.png')
            if backgroundAssetbundleName == '':
                rankpic = None
                pic = get_honor_asset(server, 'assets/online'
                                            f'/startapp/{filename}/{assetbundleName}/degree_sub.png')
                rankpic = get_honor_asset(server, 'assets/online'
                                                f'/startapp/{filename}/{assetbundleName}/{subname}')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                if rankpic is not None:
                    r, g, b, mask = rankpic.split()
                    pic.paste(rankpic, (34, 42), mask)
            else:
                pic = get_honor_asset(server, 'assets/online'
                                            f'/startapp/{filename}/{backgroundAssetbundleName}/degree_sub.png')
                rankpic = get_honor_asset(server, 'assets/online'
                                                f'/startapp/{filename}/{assetbundleName}/{subname}')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                r, g, b, mask = rankpic.split()
                pic.paste(rankpic, (34, 42), mask)
            if honorType == 'character' or honorType == 'achievement':
                if star is True:
                    honorlevel = honor['honorLevel']
                    if honorlevel > 10:
                        honorlevel = honorlevel - 10
                    if honorlevel < 5:
                        for i in range(0, honorlevel):
                            lv = Image.open('assets/static/pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                    else:
                        for i in range(0, 5):
                            lv = Image.open('assets/static/pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                        for i in range(0, honorlevel - 5):
                            lv = Image.open('assets/static/pics/icon_degreeLv6.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
    elif honor['profileHonorType'] == 'bonds':
        # cp牌子
        with open(f'{masterdatadir}/bondsHonors.json', 'r', encoding='utf-8') as f:
            bondsHonors = json.load(f)
            for i in bondsHonors:
                if i['id'] == honor['honorId']:
                    gameCharacterUnitId1 = i['gameCharacterUnitId1']
                    gameCharacterUnitId2 = i['gameCharacterUnitId2']
                    honorRarity = i['honorRarity']
                    break
        if ismain:
            # 大图
            if honor['bondsHonorViewType'] == 'reverse':
                pic = bonds_background(gameCharacterUnitId2, gameCharacterUnitId1)
            else:
                pic = bonds_background(gameCharacterUnitId1, gameCharacterUnitId2)
            chara1 = Image.open(f'assets/static/chara/chr_sd_{str(gameCharacterUnitId1).zfill(2)}_01/chr_sd_'
                                f'{str(gameCharacterUnitId1).zfill(2)}_01.png')
            chara2 = Image.open(f'assets/static/chara/chr_sd_{str(gameCharacterUnitId2).zfill(2)}_01/chr_sd_'
                                f'{str(gameCharacterUnitId2).zfill(2)}_01.png')
            if honor['bondsHonorViewType'] == 'reverse':
                chara1, chara2 = chara2, chara1
            r, g, b, mask = chara1.split()
            pic.paste(chara1, (0, -40), mask)
            r, g, b, mask = chara2.split()
            pic.paste(chara2, (220, -40), mask)
            maskimg = Image.open('assets/static/pics/mask_degree_main.png')
            r, g, b, mask = maskimg.split()
            pic.putalpha(mask)
            if honorRarity == 'low':
                frame = Image.open('assets/static/pics/frame_degree_m_1.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_m_2.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_m_3.png')
            else:
                frame = Image.open('assets/static/pics/frame_degree_m_4.png')
            r, g, b, mask = frame.split()
            if honorRarity == 'low':
                pic.paste(frame, (8, 0), mask)
            else:
                pic.paste(frame, (0, 0), mask)
            wordbundlename = f"honorname_{str(gameCharacterUnitId1).zfill(2)}" \
                             f"{str(gameCharacterUnitId2).zfill(2)}_{str(honor['bondsHonorWordId'] % 100).zfill(2)}_01"
            word = Image.open('assets/online/startapp'
                              f'/bonds_honor/word/{wordbundlename}.png')
            r, g, b, mask = word.split()
            pic.paste(word, (int(190 - (word.size[0] / 2)), int(40 - (word.size[1] / 2))), mask)
            if honor['honorLevel'] < 5:
                for i in range(0, honor['honorLevel']):
                    lv = Image.open('assets/static/pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
            else:
                for i in range(0, 5):
                    lv = Image.open('assets/static/pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
                for i in range(0, honor['honorLevel'] - 5):
                    lv = Image.open('assets/static/pics/icon_degreeLv6.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
        else:
            # 小图
            if honor['bondsHonorViewType'] == 'reverse':
                pic = bonds_background(gameCharacterUnitId2, gameCharacterUnitId1, False)
            else:
                pic = bonds_background(gameCharacterUnitId1, gameCharacterUnitId2, False)
            chara1 = Image.open(f'assets/static/chara/chr_sd_{str(gameCharacterUnitId1).zfill(2)}_01/chr_sd_'
                                f'{str(gameCharacterUnitId1).zfill(2)}_01.png')
            chara2 = Image.open(f'assets/static/chara/chr_sd_{str(gameCharacterUnitId2).zfill(2)}_01/chr_sd_'
                                f'{str(gameCharacterUnitId2).zfill(2)}_01.png')
            if honor['bondsHonorViewType'] == 'reverse':
                chara1, chara2 = chara2, chara1
            chara1 = chara1.resize((120, 102))
            r, g, b, mask = chara1.split()
            pic.paste(chara1, (-5, -20), mask)
            chara2 = chara2.resize((120, 102))
            r, g, b, mask = chara2.split()
            pic.paste(chara2, (60, -20), mask)
            maskimg = Image.open('assets/static/pics/mask_degree_sub.png')
            r, g, b, mask = maskimg.split()
            pic.putalpha(mask)
            if honorRarity == 'low':
                frame = Image.open('assets/static/pics/frame_degree_s_1.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_s_2.png')
            elif honorRarity == 'middle':
                frame = Image.open('assets/static/pics/frame_degree_s_3.png')
            else:
                frame = Image.open('assets/static/pics/frame_degree_s_4.png')
            r, g, b, mask = frame.split()
            if honorRarity == 'low':
                pic.paste(frame, (8, 0), mask)
            else:
                pic.paste(frame, (0, 0), mask)
            if honor['honorLevel'] < 5:
                for i in range(0, honor['honorLevel']):
                    lv = Image.open('assets/static/pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
            else:
                for i in range(0, 5):
                    lv = Image.open('assets/static/pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
                for i in range(0, honor['honorLevel'] - 5):
                    lv = Image.open('assets/static/pics/icon_degreeLv6.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
    return pic


def get_honor_asset(server, path):
    if server == 'jp':
        return Image.open(path)
    if 'bonds_honor' in path:  # 没解出来 之后再改
        return Image.open(path)
    else:
        path = path.replace('startapp/honor', f'startapp/{server}honor').replace('startapp/honor',
                                                                                 f'startapp/{server}honor')
        if os.path.exists(path):
            return Image.open(path)
        else:
            dirs = os.path.abspath(os.path.join(path, ".."))
            foldername = dirs[dirs.find(f'{server}honor') + len(f'{server}honor') + 1:]
            filename = path[path.find(foldername) + len(foldername) + 1:]
            try:
                if server == 'tw':
                    print(f'download from https://storage.sekai.best/sekai-tc-assets/honor/{foldername}_rip/{filename}')
                    resp = requests.get(f"https://storage.sekai.best/sekai-tc-assets/honor/{foldername}_rip/{filename}",
                                        timeout=3)
                elif server == 'en':
                    print(f'download from https://storage.sekai.best/sekai-en-assets/honor/{foldername}_rip/{filename}')
                    resp = requests.get(f"https://storage.sekai.best/sekai-en-assets/honor/{foldername}_rip/{filename}",
                                        timeout=3)
            except:
                return Image.open(path.replace('{server}honor', 'honor'))
            if resp.status_code == 200:  # 下载到了
                pic = Image.open(io.BytesIO(resp.content))
                if not os.path.exists(dirs):
                    os.makedirs(dirs)
                pic.save(path)
                return pic
            else:
                return Image.open(path)


def bonds_background(chara1, chara2, ismain=True):
    if ismain:
        pic1 = Image.open(f'assets/static/bonds/{str(chara1)}.png')
        pic2 = Image.open(f'assets/static/bonds/{str(chara2)}.png')
        pic2 = pic2.crop((190, 0, 380, 80))
        pic1.paste(pic2, (190, 0))
    else:
        pic1 = Image.open(f'assets/static/bonds/{str(chara1)}_sub.png')
        pic2 = Image.open(f'assets/static/bonds/{str(chara2)}_sub.png')
        pic2 = pic2.crop((90, 0, 380, 80))
        pic1.paste(pic2, (90, 0))
    return pic1
