#!/bin/bash


# Set timezone non-interactively to avoid tzdata prompt
export DEBIAN_FRONTEND=noninteractive
sudo ln -fs /usr/share/zoneinfo/Africa/Accra /etc/localtime
sudo apt-get install -y tzdata
sudo dpkg-reconfigure -f noninteractive tzdata

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io

sudo apt-get install -y git

#build docker image
docker build -t episcope:latest .

#create systemd service
sudo tee /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon for Django app
After=network.target

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm --name episcope-app -p 8000:8000 episcope:latest
ExecStop=/usr/bin/docker stop episcope-app

[Install]
WantedBy=multi-user.target
EOF

#enable and start service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable gunicorn.service
sudo systemctl restart gunicorn.service

#configure nginx
sudo tee /etc/nginx/sites-available/episcope << EOF
server {
    listen 80;
    server_name api-episcope.grandkojo.my;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /app/episcope;
    }

    location / {
        include proxy_params;
        proxy_pass http://localhost:8000;
    }
}
EOF

#enable nginx site
sudo ln -s /etc/nginx/sites-available/episcope /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo "🔒 Installing HTTPS certificates..."
sudo apt install -y certbot python3-certbot-nginx

sleep 5

sudo certbot --nginx \
  --non-interactive \
  --agree-tos \
  --redirect \
  --no-eff-email \
  --email essienernest.kojoowu@gmail.com \
  -d api-episcope.grandkojo.my
