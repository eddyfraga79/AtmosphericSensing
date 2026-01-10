#!/bin/bash
# disable_autoapp_start.sh — Disables your app from starting at bootup
# my_project.service must first be placed in folder /etc/systemd/system/

sudo systemctl disable my_project.service
sudo systemctl stop my_project.service
