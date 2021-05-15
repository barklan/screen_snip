#!/bin/bash

export TESSDATA_PREFIX=/home/barklan/sys/tessdata_best/

cd /home/barklan/sys/screen_snip

source env/bin/activate
python textshot.py eng+rus
deactivate