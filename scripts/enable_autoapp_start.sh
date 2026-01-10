#!/bin/bash
# enable_autoapp_start.sh — Enable your app from starting at bootup
# my_project.service must first be placed in folder /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable my_project.service
