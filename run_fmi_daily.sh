#!/bin/bash
#/home/davsean/.cache/pypoetry/virtualenvs/uccc-foundation-app-qFY2nxrc-py3.9/bin/python /home/davsean/foundation-app/scripts/fmi_report_data.py
cp -r 20* /mnt/00_results/
latest=`ls -d 20* | head -1`
echo $latest
cp -r 20* /mnt/00_results/
rm -rf /mnt/00_results/00_latest
mv $latest /mnt/00_results/00_latest

