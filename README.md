News Backend
============

This project is outlined with the following modules:

* `image-processor`: handles scaling images, making thumbnails; checking if the
image is content-sensitive; checking if the content of the image matches its
description, etc.

* `alert-maitenance`: provides code to watch over the running databases and the like; clean and restore obsolete data.

* `scraper`: scrapes RSS resources for news, blogs and images; APIs of SNS,
APIs of SNS-based images, and streams.

* `data-miner`: mines hot and related news from server logs and stored user information; it also provides code to dedup news 

* `user-account`: provides code to do user register/login/logoff, API-based login/logoff; code to comment on news/images; code to favorate news/images; code to do personalization (subscription, collect, comment, change themes and colors)

* `data-processor`: transcoding webpages, news summarization, TTS-generation,
Searchet-based features 

* `template`: HTML, CSS and Javascript code necessary for news-page and
integrated information page (Searchet-based features)

* `adminstration`: RSS-adding page, manual hot news push news page and strategy
modification page 

* `interface`: news reading, image reading and etc.
