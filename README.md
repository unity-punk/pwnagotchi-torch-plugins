# pwnagotchi-torch-plugins

FULL DISCLOSURE I DO NOT HAVE A CLUE WHAT IM DOING.

a place for my dumb plugins

# Add my repo
Custom plugin repository

Edit your `/etc/pwnagotchi/config.toml` to look like this

```TOML
main.custom_plugin_repos = [
    "https://github.com/unity-punk/pwnagotchi-torch-plugins/archive/master.zip",
    ]
```
Then run this command: `sudo pwnagotchi plugins update`


# wpa_sec_manager.py
Cleans and creates a searchable web ui page from wpa-sec.cracked.potfile
generates local QR codes in webui

Web UI access at http://pwnagotchi.local:8080/plugins/wpa_sec_manager
  
  REQUIREMENTS:  
  
[Pwnagotchi torch v2.9.5.8](https://github.com/jayofelony/pwnagotchi/releases/tag/v2.9.5.8)  
wpa-sec Plugin installed and working
qrencode must be installed and working
  ``` sudo apt install qrencode ```

INSTALL:
install qrencode
```
sudo apt update
sudo apt install qrencode
```

change to custom plugin directory
``` 
cd /etc/pwnagotchi/custom-plugins
```
download to current working directory:
```
wget https://github.com/unity-punk/pwnagotchi-torch-plugins/raw/refs/heads/main/wpa_sec_manager.py
```


CONFIGURE:

add to config.toml:
```
[main.plugins.wpa_sec_manager]
main.plugins.wpa_sec_manager.enabled = true
# Optional: change path if your potfile is stored elsewhere
main.plugins.wpa_sec_manager.potfile_path = "/etc/pwnagotchi/handshakes/wpa-sec.cracked.potfile"
main.plugins.wpa_sec_manager.qr_dir = "/etc/pwnagotchi/handshakes/qrcodes"
```

finally restart pwnagotchi service
```
pwnkill
```
