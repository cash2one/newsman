Definition
-----------
this module contains four kinds of files:
* crawler: it scrapes RSS/ATOM alike published content; legal web pages like
  WAP pages; APIs. Data are not differentiated as RSS, web pages or pictures,
videos and etc.

* database handler: mostly deals with permanently storing scraped data on to
  one or two dedicated database server.

* memory handler: data in memory could be provided by crawlers or automatically
  generated from database.

* feature interface: provides callers so that server routine program could
  regularly asked it to scrape data.

ToDos
------
1. (done) extract image-processing methods
2. (done) break down database storing method
3. integrate api scraping
4. extract alert-maintenance-related code from task
5. (done) add newsbeuter-like mechanism to mitigate pressure on rss servers
6. add feed table/database statistics collector (ctlr to rss.py update method
   to database.py)
7. put some basic maintenance code in database and memory
