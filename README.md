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
1. Feed相关代码重构
2. Task相关代码分解、重构
3. 转码代码清理、重构
4. 对外接口重构
5. Feed管理平台
6. 摘要/首段抓取代码编写
7. 自定义Exception类，并替换相应代码
8. 预警代码整理、重构
9. 数据整理代码整理、重构
10. Readability代码整合、测试
11. 减少参数调用（尽量从数据库中获取）

ToDos - Low Priority
---------------------
1. 图片判断是否是男人
2. 判断图片是否是黄图
3. 抓取Instagram/Flickr内容
4. 社交账户好友信息抓取
5. 热点新闻提取
6. 新闻去重
7. 类别类似新闻
8. Bugu用户账户代码转移
9. Minerva代码转移
10. 详情页增加夜间、字体大小、分享等代码
11. 为PM提供RSS管理的Web界面
12. 增加在线生成临时图片和MP3的接口

Dones
------
1. 图片类的代码放在image_processor中
2. 加入朗读抓取代码
3. 文件名生成方式修改 --> 语言-分类-源（objectId）-时间-随机码
4. 根据RSS提供者的元数据区分更新时间
5. 根据TODO标签自动生成Markdown文档


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

