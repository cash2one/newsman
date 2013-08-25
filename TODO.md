ToDos - High Priority
----------------------
1. 预警代码整理、重构
2. Feed管理平台
3. 自定义Exception类，并替换相应代码
4. 理清每个函数的返回类型（raise Exception or None?）
5. 服务器质量监控
6. 数据整理代码整理、重构
7. URL处理换成gruns/furl
8. 测试标题提取使用Lassie(多国语言)
9. qrconverter类似脚本使用docopt/docopt
10. 为每个文件增加开源声明
11. thumbnail/image_helper重新构造
12. 修改本文档
13. Redis expire可能会失效，访问时增加检查和清理
14. 去掉html内容的代码换成那个bs4
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
11. 为PM提供RSS管理的Web界面
12. 增加在线生成临时图片和MP3的接口
13. 参照谷歌编码风格
    [中文](http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/)
    [EN](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)

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


ToDos - Generated from docs
--------------------------
* `data_processor/transcoder.py`
    1. Line 140: _transcode
        - add http string checkers

* `scraper/rss.py`
    1. Line 104: _get_tts
        - replace primitive exception recording with logging
    2. Line 222: update
        - code to remove added items if things suck at database/memory

* `data_processor/tts_provider.py`
    1. Line 103: _query_segment
        - write some boundary checkers
        - determine how do these languages separate words
        - get encoding of a feed. use that if indicated, else 'utf-8'
    2. Line 203: _download
        - Test! Test! Test!
        - boundary checkers
        - write docs!
    3. Line 71: google
        - write docs
        - rename the file and variables
        - remove accepting command line calls

* `scraper/rss_parser.py`
    1. Line 218: parse
        - boundary checkers
        - update parsing info to feed database
    2. Line 38: _read_entry
        - add more boundary checks
        - [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
        - add tags
        - add thumbnail limit(downward)

* `data_processor/baidu_uck.py`
    1. Line 32: _sanitize
        - test the code
        - remove code that sanitize too much

* `publisher/inquirer.py`
    1. Line 41: get_categories_by_language
        - need to refactor this method after sorting out feed.py
        - added database inquire if language cannot be found in memory

* `data_processor/image_helper.py`
    1. Line 147: scale_image
        - boundary checker

* `data_processor/thumbnail.py`
    1. Line 30: is_valid_image
        - boundary checker should not return None, instead probably an Exception
        - this method should be moved to image_helper
    2. Line 51: generate_thumbnail
        - boundary checkers
        - relative path could be a url including its suffix like jpg/png

* `scraper/memory.py`
    1. Line 24: update
        - be precautious with possible redis adding failure

* `feed_manager/feed.py`
    1. Line 49: add
        - implement _link_cleaner!

