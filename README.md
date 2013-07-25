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
2. [DONE]图片类的代码放在image_processor中
3. 图片抓取代码加入
4. task.py内容分解到各相应文件夹
5. Feed取消文档，改为数据库
6. Readability（decruft）代码整理出来
7. [DONE]文件名生成方式修改 --> 语言-分类-源（objectId）-时间-随机码
8. image/big_image等修改
9. [DONE]加入朗读抓取代码
10. [Done]根据RSS提供者的元数据区分更新时间
11. 加入摘要代码
12. 添加自定义Exception类
13. 返回类型理清（raise Exception/return None）

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
13. 根据Todos标签自动生成Markdown文档
14. 增加在线生成临时图片和MP3的接口

ToDos - Generated from docs
--------------------------
* `scraper/database.py`
    1. Line 38: update
        - break update_database into several shorter mthods
    2. Line 56: update_feed
        - write docs

* `data_processor/transcoder.py`
    1. Line 161: transcode
        - should separate big_images from transcoding
        - return an exception when fucked up

* `image_processor/thumbnail.py`
    1. Line 19: is_thumbnail
        - boundary checker should not return None, instead probably an Exception
    2. Line 31: generate_thumbnail
        - boundary checkers
        - relative path could be a url including its suffix like jpg/png

* `scraper/rss.py`
    1. Line 107: update
        - code to remove added items if things suck at database/memory

* `scraper/memory.py`
    1. Line 15: update
        - add more comments
        - be precautious with possible redis adding failure

* `data_processor/tts_provider.py`
    1. Line 76: _query_segment
        - write some boundary checkers
        - determine how do these languages separate words
    2. Line 137: _download
        - Test! Test! Test!
        - boundary checkers
        - write docs!
    3. Line 53: google
        - write docs
        - rename the file and variables
        - remove accepting command line calls

* `scraper/rss_parser.py`
    1. Line 238: parse
        - boundary checkers
        - update parsing info to feed database
    2. Line 36: _read_entry
        - add more boundary checks
        - [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
        - add tags
        - add thumbnail limit(downward)

