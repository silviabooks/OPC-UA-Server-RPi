openssl req -x509 -newkey rsa:2048 -keyout myPrivateKey.pem -out myCertificate.pem -days 355 -nodes
openssl x509 -outform der -in myCertificate.pem -out myCertificate.der
