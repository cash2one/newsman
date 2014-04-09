ToDos - High Priority
----------------------
1. 社交(Twitter/WeChat)信息抓取
2. 新闻去重
3. 抓取Instagram/Flickr内容
4. 热点新闻提取
5. 根据热门关键字搜索图片 [link1](http://jackdschultz.com/index.php/2013/09/19/useful-named-entity-recognition/) [link2](https://gist.github.com/shlomibabluki/6333174)
6. 参照谷歌编码风格
    [中文](http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/)
    [EN](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)
    [link](http://azd325.github.io/blog/2013/08/18/python-strip-tags/)
7. 采用nose/coverage进行测试
8. 修改README
9. 过一遍代码的Todo

ToDos - Low Priority
---------------------
1. 图片判断是否是男人
2. 判断图片是否是黄图
3. 类别类似新闻
4. Bugu用户账户代码转移
5. Minerva代码转移
6. Feed管理平台
7. qrconverter类似脚本使用docopt/docopt

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
24. 数据备份和恢复 
25. 测试标题提取使用Lassie(多国语言)
26. 融合[Scrapely](https://github.com/scrapy/scrapely)到转码器中
27. data_processor代码整理、重构
28. 整理转码器图片提取模块 [link](http://jackdschultz.com/index.php/2013/09/13/validating-url-as-an-image-in-python/)
29. URL处理换成gruns/furl
30. 去掉html内容的代码换成那个bs4
31. 新闻摘要
32. 由文字生成图片
33. 详情页增加夜间、字体大小、分享等代码
34. 集成CDN

ToDos - Generated from docs
--------------------------
* `data_processor/baidu_uck.py`
    1. Line 31: _sanitize
        - test the code
        - remove code that sanitize too much

* `data_processor/image_helper.py`
    1. Line 188: scale_image
        - boundary checker

* `data_processor/transcoder.py`
    1. Line 171: _transcode
        - add http string checkers

* `feed_manager/feed.py`
    1. Line 62: add
        - implement _link_cleaner!

* `data_processor/thumbnail.py`
    1. Line 30: is_valid_image
        - this method should be moved to image_helper
    2. Line 69: generate_thumbnail
        - relative path could be a url including its suffix like jpg/png

* `scraper/rss.py`
    1. Line 101: _get_tts
        - replace primitive exception recording with logger
    2. Line 263: update
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
    1. Line 230: parse
        - boundary checkers
        - update parsing info to feed database
    2. Line 41: _read_entry
        - add more boundary checks
        - [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
        - add tags
        - add thumbnail limit(downward)

