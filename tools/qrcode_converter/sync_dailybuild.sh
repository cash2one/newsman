#!/bin/sh

# sync_dailybuild.sh
# Replicate file trees to server using rsync
# or call from cron (make sure ssh key is loaded beforehand)

cd /home
rsync -e ssh -av --delete work/web/doremi.baidu.com/hao123gm/globalnews_dailybuild/ work@hk01-gmobile-web00.vm:/home/work/web/doremi.baidu.com/hao123gm/globalnews_dailybuild
