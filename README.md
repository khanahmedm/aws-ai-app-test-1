# Flask Bedrock app

# Flask + Gunicorn + Nginx on EC2 (with Bedrock Integration)

This guide documents all the steps taken to set up a Flask web application on an EC2 instance using Gunicorn and Nginx, with integration to Amazon Bedrock. It also includes all the troubleshooting and fixes required to resolve common issues.

---

## 1. Install Dependencies on EC2

```bash
sudo yum update -y
sudo yum install python3-pip python3-devel nginx git -y
```

---

## 2. Set Up the Flask App

```bash
# Create directory structure
mkdir -p ~/flask-bedrock/aws-ai-app-test-1
cd ~/flask-bedrock/aws-ai-app-test-1

# Set up virtual environment
python3 -m venv ../venv
source ../venv/bin/activate

# Install Flask and Gunicorn
pip install flask gunicorn boto3
```

Create `app.py` inside `aws-ai-app-test-1` with your Flask app using Bedrock.

---

## 3. Run Gunicorn Manually (for testing)

```bash
cd ~/flask-bedrock/aws-ai-app-test-1
source ../venv/bin/activate
gunicorn --workers 3 --bind unix:flask-bedrock.sock --umask 007 app:app
```

Check that the socket was created:
```bash
ls -l flask-bedrock.sock
```

Test locally:
```bash
curl -I --unix-socket flask-bedrock.sock http://localhost/
```

---

## 4. Configure Nginx

```bash
sudo nano /etc/nginx/conf.d/flask-bedrock.conf
```

Content:
```nginx
server {
    listen 80 default_server;
    server_name localhost;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ec2-user/flask-bedrock/aws-ai-app-test-1/flask-bedrock.sock;
    }
}
```

Test and restart:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. Configure Systemd to Run Gunicorn as a Service

```bash
sudo nano /etc/systemd/system/flask-bedrock.service
```

Content:
```ini
[Unit]
Description=Gunicorn instance to serve flask-bedrock
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/flask-bedrock/aws-ai-app-test-1
Environment="PATH=/home/ec2-user/flask-bedrock/venv/bin"
ExecStart=/home/ec2-user/flask-bedrock/venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/home/ec2-user/flask-bedrock/aws-ai-app-test-1/flask-bedrock.sock \
  --umask 007 \
  app:app

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-bedrock
sudo systemctl start flask-bedrock
```

---

## 6. Directory Permission Fixes

```bash
sudo chmod o+x /home/ec2-user
sudo chmod o+x /home/ec2-user/flask-bedrock
sudo chmod o+x /home/ec2-user/flask-bedrock/aws-ai-app-test-1
```

---

## 7. Troubleshooting Summary

### Problem: `502 Bad Gateway` from Nginx

**Cause:** Nginx could not access the socket file due to permissions or ownership

**Fix:**
- Ensure Gunicorn creates the socket with `--umask 007`
- Add `nginx` user to `ec2-user` group: `sudo usermod -aG ec2-user nginx`
- Set directory permissions: `chmod o+x` or `chmod 711` on each directory in the path

### Problem: `Permission denied` to socket in logs

**Fix:**
- `ls -l` should show: `srwxrwx--- ec2-user ec2-user`
- Ensure Nginx is restarted after permission changes

### Problem: `curl` works locally but not in browser

**Fix:**
- EC2 instance directory was not accessible to `nginx`
- Solution: `chmod 711 /home/ec2-user`

### Problem: SELinux

**Checked:** `getenforce` returned `Permissive`, so not an issue in this case

---

## 8. Confirm Everything is Working

Test from EC2:
```bash
curl -I http://localhost
```

Test from browser:
```
http://<your-ec2-public-ip>
```

---

You now have a production-ready Flask app running behind Gunicorn and Nginx, with socket-based communication and correct permissions to support Amazon Bedrock integration! 🚀

