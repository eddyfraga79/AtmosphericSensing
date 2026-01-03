# Create a systemd service file

* Create a new file called, for example, my_project.service:
```
sudo nano /etc/systemd/system/my_project.service
```
* Paste the following in the my_project.service

```
[Unit]
Description=My Python Project
After=network.target

[Service]
Type=simple
WorkingDirectory=/dir/to/my_project
ExecStart=/dir/to/my_project/start.sh
Restart=always
User=pi
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
# Enable the service

* Tell systemd to start your service at boot:
```
sudo systemctl daemon-reload
sudo systemctl enable my_project.service
```

# Check for errors after boot

* After reboot, check the service status:
```
sudo systemctl status my_project.service
```
or
```
journalctl -u my_project.service -b -f
```

# Make sure systemd can execute the script

* Your start.sh must be executable:
```
chmod +x /home/pi/my_project/start.sh
```

# Disable auto-start at boot

* If you want to prevent it from starting automatically on future reboots, run:
```
sudo systemctl disable my_project.service
sudo systemctl stop my_project.service
```
* If you change your mind and want it to auto-start again:
```
sudo systemctl enable my_project.service
```