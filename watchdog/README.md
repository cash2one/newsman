Tasks of a watch dog
--------------------

* `scrape`: **HOURLY**. spider rss sources and web services for latest information

* `clean memory`: **DAILY**. clean expired items and its place in queues in the memory

* `clean database`: **DAILY**. clean expired items in database

* `clean saved expired files`: **DAILY**. clean expired files saved on the disk

* `clean temporary files`: **DAILY**. clean temporary files created by accident

* `clean unrecorded files`: **DAILY**. remove files on the disk not recorded in database

* `clean zombies`: **DAILY**. clean zombie items in memory and database

* `remove zombie processes`: **Semi-DAILY**. kill zombie processes

* `monitor memory`: **REAL-TIME**. monitor memory usage, alarm on risks, restart memory
  service, restore data

* `monitor database`: **REAL-TIME**. monitor database usage, alarm on risks, restart database
  service, restore data if backups are available 

* `monitor web server`: **REAL-TIME**. monitor web server usage, alarm on risks, restart web
  server

* `monitor scraping`: **DAILY**. monitor rss/web service scraping, alarm on errors or
  blockage
