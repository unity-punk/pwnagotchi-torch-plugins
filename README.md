# pwnagotchi-torch-plugins

FULL DISCLOSURE I DO NOT HAVE A CLUE WHAT IM DOING.

a place for my dumb plugins

# wpa_sec_manager.py
Cleans and creates a searchable web ui page from wpa-sec.cracked.potfile
generates local QR codes in webui

Web UI access at http://pwnagotchi.local:8080/plugins/wpa_sec_manager
  
  REQUIREMENTS:  
  
[Pwnagotchi torch v2.9.5.8](https://github.com/jayofelony/pwnagotchi/releases/tag/v2.9.5.8)  
wpa-sec Plugin installed and working
qrencode must be installed and working
  ``` sudo apt install qrencode ```


CONFIG:

add to config.toml:
```
[main.plugins.wpa_sec_manager]
main.plugins.wpa_sec_manager.enabled = true
# Optional: change path if your potfile is stored elsewhere
main.plugins.wpa_sec_manager.potfile_path = "/etc/pwnagotchi/handshakes/wpa-sec.cracked.potfile"
main.plugins.wpa_sec_manager.qr_dir = "/etc/pwnagotchi/handshakes/qrcodes"
```


