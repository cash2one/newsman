Tasks of a watch dog
--------------------

* `scrape`: hourly, spider rss sources and web services for latest information

* `clean memory`: daily, clean expired items and its place in queues in the memory

* `clean database`: daily, clean expired items in database

* `clean saved expired files`: daily, clean expired files saved on the disk

* `clean temporary files`: daily, clean temporary files created by accident

* `clean unrecorded files`: daily, remove files on the disk not recorded in database

* `clean zombies`: daily, clean zombie items in memory and database

* `remove zombie processes`: semi-daily, kill zombie processes

* `monitor memory`: monitor memory usage, alarm on risks, restart memory
  service, restore data

* `monitor database`: monitor database usage, alarm on risks, restart database
  service, restore data if backups are available 

* `monitor web server`: monitor web server usage, alarm on risks, restart web
  server

* `monitor scraping`: monitor rss/web service scraping, alarm on errors or
  blockage
