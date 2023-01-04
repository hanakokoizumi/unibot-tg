# unibot-tg

将 [Unibot](https://github.com/watagashi-uni/Unibot) 的部分功能移植到 Telegram 上。

已移植功能：
- 查询 Profile
- 查询 Expert/Master 完成情况
- 模拟抽卡
- 查询群友信息

支持缺少资源文件时自动下载。

使用了 [Nightcord API](https://docs.api.nightcord.de)。

## 部署
1. `pip install -r requirements.txt`
2. 将 `config.example.yml` 重命名为 `config.json`，并填写其中的内容。
3. 之后运行 `download.py` 下载资源。
4. 最后运行 `main.py` 即可。

注：如果遇到文件夹缺失，直接创建这个空文件夹即可。

## 建议的 Commands List
```
start - Get URL of nightcord.de
bind - Bind a JP player ID
unbind - Unbind a JP player ID
gacha - Execute an emulation of current gacha on JP server
profile - Get profile of JP player
experts - Get player process on expert diff of a JP player
masters - Get player process on master diff of a JP player
```

## Credits
- [Unibot](https://github.com/watagashi-uni/Unibot) by [watagashi-uni](https://github.com/watagashi-uni)
- [Nightcord API](https://docs.api.nightcord.de) by Hanako
