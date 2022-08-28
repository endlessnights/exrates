# exrates
Parses https://mironline.ru/support/list/kursy_mir/ and getting Kazakhstan's exchange rate from Russian Ruble to KZT (Tenge). 

Pull Docker image: \
docker pull legeminus/exrates

Run Docker container: \
docker run -it -d -p 8080:5000 legeminus/exrates \
(8080 - out, 5000 - inside, default) \
\
Then create **NGINX configuration** file to proxy 8080 to 80 on domain name: \
nano /etc/nginx/sites-available/exrates-docker \
server { \
    listen 80; \
    server_name example.com; \
    location / { \
        proxy_pass http://127.0.01:8080; \
} \
}
\
Make symb-link: \
sudo ln -s /etc/nginx/sites-available/exrates-docker /etc/nginx/sites-enabled/ \
Then run **CERTBOT** to get SSL-certificate to your domain name.

We need to restart Docker container every 2 hours, then create CRON task: \
sudo crontab -e  \
*/120 * * * * docker restart <docker-container-ID>


Or pull this repo and: \
docker build -t k8s-exrates . \
docker run -p 5000:5000 k8s-exrates \
Man: https://vas3k.club/post/1631419/
