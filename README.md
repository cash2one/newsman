News Backend
============

This project is outlined with the following modules:

* `image_processor`: handles scaling images, making thumbnails; checking if the
image is content-sensitive; checking if the content of the image matches its
description, etc.

* `alert_maintenance`: provides code to watch over the running databases and the like; clean and restore obsolete data.

* `scraper`: scrapes RSS resources for news, blogs and images; APIs of SNS,
APIs of SNS-based images, and streams.

* `data_miner`: mines hot and related news from server logs and stored user information; it also provides code to dedup news 

* `user_account`: provides code to do user register/login/logoff, API-based login/logoff; code to comment on news/images; code to favorate news/images; code to do personalization (subscription, collect, comment, change themes and colors)

* `data_processor`: transcoding webpages, news summarization, TTS-generation,
Searchet-based features 

* `template`: HTML, CSS and Javascript code necessary for news-page and
integrated information page (Searchet-based features)

* `adminstration`: RSS-adding page, manual hot news push news page and strategy
modification page 

* `interface`: news reading, image reading and etc.

ToDos - High Priority
----------------------
1. 去掉没用的代码
2. 图片类的代码放在image_processor中
3. 图片抓取代码加入
4. task.py内容分解到各相应文件夹
5. 转码测试readability（decruft）
6. 文件名生成方式修改 --> 语言-分类-源（objectId）-时间-随机码
7. image/big_image等修改
8. 加入朗读抓取代码
9. 加入摘要代码

ToDos - Low Priority
---------------------
1. 图片判断是否是男人
2. 判断图片是否是黄图
3. 预警代码整理和修改
4. 抓取Instagram/Flickr内容
5. 社交账户好友信息抓取
6. 热点新闻提取
7. 新闻去重
8. 类别类似新闻
9. Bugu用户账户代码转移
10. Minerva代码转移
11. 详情页增加夜间、字体大小、分享等代码
12. 为PM提供RSS管理的Web界面
