#------------line_notify.py------------
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import requests


url = 'https://notify-api.line.me/api/notify'
token = 'B54c5474b368b5eba88bc9559c083ada2'
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

msg = 'ส่งข้อความ LINE Notify'
r = requests.post(url, headers=headers, data = {'message':msg})

# print(r)
print(r.text)

if "status" in r.text:
    print("i see ")