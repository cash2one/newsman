ToDos - High Priority
----------------------
1. data_processor代码整理、重构
2. 整理转码器图片提取模块
3. 采用nose/coverage进行测试
4. URL处理换成gruns/furl
5. 测试标题提取使用Lassie(多国语言)
6. 融合[Scrapely](https://github.com/scrapy/scrapely)到转码器中
7. 根据热门关键字搜索图片
8. 新闻摘要
9. 修改README
10. 参照谷歌编码风格
    [中文](http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/)
    [EN](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)
11. 去掉html内容的代码换成那个bs4
    [link](http://azd325.github.io/blog/2013/08/18/python-strip-tags/)

ToDos - Low Priority
---------------------
1. 抓取Instagram/Flickr内容
2. 图片判断是否是男人
3. 判断图片是否是黄图
4. 社交账户好友信息抓取
5. 热点新闻提取
6. 新闻去重
7. 类别类似新闻
8. Bugu用户账户代码转移
9. Minerva代码转移
10. 详情页增加夜间、字体大小、分享等代码
11. Feed管理平台
12. qrconverter类似脚本使用docopt/docopt

Dones
------
1. 图片类的代码放在image_processor中
2. 加入朗读抓取代码
3. 文件名生成方式修改 --> 语言-分类-源（objectId）-时间-随机码
4. 根据RSS提供者的元数据区分更新时间
5. 根据TODO标签自动生成Markdown文档
6. 对外接口重构
7. Feed相关代码重构
8. 减少参数调用（尽量从数据库中获取）
9. Readability代码整合、测试
10. 转码代码清理、重构
11. 摘要/首段抓取代码编写
12. 为PM提供一个Simplr, Readability, UCK比较的页面
13. 包结构合理化
14. 抓取改为每处理完一个存储数据库和内存
15. Task相关代码分解、重构
16. 为项目增加开源声明
17. Redis expire可能会失效，访问时增加检查和清理
18. 理清每个函数的返回类型（raise Exception or None?）
19. 输出改为logging
20. 服务器质量监控
21. WAP页支持
22. 预警代码整理、重构
23. 使用Fabric进行发布

ToDos - Generated from docs
--------------------------
* `data_processor/baidu_uck.py`
    1. Line 31: _sanitize
        - test the code
        - remove code that sanitize too much

* `publisher/inquirer.py`
    1. Line 40: get_categories_by_language
        - need to refactor this method after sorting out feed.py

* `data_processor/image_helper.py`
    1. Line 188: scale_image
        - boundary checker

* `data_processor/transcoder.py`
    1. Line 167: _transcode
        - add http string checkers

* `feed_manager/feed.py`
    1. Line 62: add
        - implement _link_cleaner!

* `data_processor/thumbnail.py`
    1. Line 30: is_valid_image
        - this method should be moved to image_helper
    2. Line 54: generate_thumbnail
        - relative path could be a url including its suffix like jpg/png

* `scraper/rss.py`
    1. Line 109: _get_tts
        - replace primitive exception recording with logger
    2. Line 266: update
        - code to remove added items if things suck at database/memory

* `data_processor/tts_provider.py`
    1. Line 120: _query_segment
        - write some boundary checkers
        - determine how do these languages separate words
        - get encoding of a feed. use that if indicated, else 'utf-8'
    2. Line 224: _download
        - Test! Test! Test!
        - boundary checkers
        - write docs!
    3. Line 78: google
        - write docs
        - rename the file and variables
        - remove accepting command line calls

* `scraper/rss_parser.py`
    1. Line 227: parse
        - boundary checkers
        - update parsing info to feed database
    2. Line 41: _read_entry
        - add more boundary checks
        - [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
        - add tags
        - add thumbnail limit(downward)

