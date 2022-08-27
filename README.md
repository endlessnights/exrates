# exrates
Parses https://mironline.ru/support/list/kursy_mir/ and getting Kazakhstan's exchange rate from Russian Ruble to KZT (Tenge) \

Pull Docker image: \
docker pull legeminus/exrates

Run Docker container: \
docker run -it -d -p 8080:5000 legeminus/exrates \
(8080 - out, 5000 - inside, default) \
\
Then create **NGINX configuration** file to proxy 8080 to 80 on domain name: \
nano /etc/nginx/sites-available/exrates-docker \
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass http://127.0.01:8080;
}
}
\
Make symb-link: \
sudo ln -s /etc/nginx/sites-available/exrates-docker /etc/nginx/sites-enabled/ \
Then run **CERTBOT** to get SSL-certificate to your domain name.
