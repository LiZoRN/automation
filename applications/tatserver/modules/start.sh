#!/bin/bash

cd /data/web2/
nohup python web2py.py -a '123456' -c server.crt -k server.key -i 172.16.11.195 -p 8000

