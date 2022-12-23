# CustomTokens

Run:
```
uvicorn app:app --reload --port=5858
```

Sync service:

```
sudo nano /etc/systemd/system/sync-tokens.service
sudo systemctl enable sync-tokens.service
sudo systemctl start sync-tokens.service
```

Nginx:
```
sudo nano /etc/nginx/sites-available/tokens.mbc.wiki.conf
sudo ln -s /etc/nginx/sites-available/tokens.mbc.wiki.conf /etc/nginx/sites-enabled
sudo systemctl restart nginx
```