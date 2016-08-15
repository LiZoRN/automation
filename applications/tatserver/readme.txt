# openssl genrsa -out server.key 2048
# openssl req -new -key server.key -out server.csr
# openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
 
# python web2py.py -a '123456' -c server.crt -k server.key -i 172.16.11.195 -p 8000