#!/bin/bash
/home/davsean/.cache/pypoetry/virtualenvs/uccc-foundation-app-qFY2nxrc-py3.9/bin/python /home/davsean/foundation-app/scripts/fmi_report_data.py

# write_protect
chmod 0444 /mnt/00_results/*xml
chmod 0444 /mnt/00_results/*pdf

cp -r 20* /mnt/00_results/
latest=`ls -d 20* | tail -1`
echo $latest
cp -rv 20* /mnt/00_results/
rm -rf /mnt/00_results/00_latest
mv $latest /mnt/00_results/00_latest
echo syncing
echo '  latest'
/usr/bin/rclone --config /home/davsean/.config/rclone/rclone.conf --log-file /tmp/rclone.log sync /mnt/00_results/00_latest fmi_onedrive:FMI_REPORTS
echo '  all'
/usr/bin/rclone --config /home/davsean/.config/rclone/rclone.conf --log-file /tmp/rclone.log sync /mnt/00_results/ fmi_onedrive:FMI_REPORTS/full/
