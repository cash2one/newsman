Newsman
========

This project provides backend support for news service

Newsman is licensed under GNU Affero GPL v3

What a README.md usually contains
---------------------------------
- A description of your project
- Links to the project's ReadTheDocs page
- A TravisCI button showing the state of the build
- "Quickstart" documentation (how to quickly install and use your project)
- A list of non-Python dependencies (if any) and how to install them

License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

(see [LICENSE](https://github.com/chengdujin/newsman/blob/master/LICENSE)
for full AGPL licence)

**(For those who don't get the legal lingo: Basically what we're saying is
feel free to copy our code, but please share back any changes or improvements
that you make, in the spirit of free software)**

Walkthrough
-------------------------

This project is outlined with the following modules:

* `data_processor`: transcoding webpages, news summarization, TTS-generation, Searchet-based features, and mines hot and related news from server logs and stored user information; it also provides code to dedup news. it contains code that handles scaling images, making thumbnails; checking if the image is content-sensitive; checking if the content of the image matches its description, etc.

* `feed_manager`: RSS-adding page, manual hot news push news page and strategy modification page 

* `publisher`: news reading, image reading and etc.

* `scraper`: scrapes RSS resources for news, blogs and images; APIs of SNS, APIs of SNS-based images, and streams.

* `templates`: HTML, CSS and Javascript code necessary for news-page and integrated information page (Searchet-based features)

* `tools`: a collection of auxilary tools, including todo-collector, feed2db,
  transcoder_web_presentor, feed_preview, qrcode_converter and etc. 

* `watchdog`: provides code to watch over the running databases and the like; clean and restore obsolete data.
