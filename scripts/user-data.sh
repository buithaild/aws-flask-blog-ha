
#!/bin/bash
set -euo pipefail

exec > >(tee -a /var/log/blog-bootstrap.log) 2>&1

echo "=== Starting Flask Blog bootstrap ==="

# 1. Install packages
dnf install -y python3 python3-pip git awscli-2

# 2. Create application user
id blogapp &>/dev/null || \
  useradd --system --create-home blogapp

# 3. Clone GitHub repository
mkdir -p /opt/blog
chown blogapp:blogapp /opt/blog

sudo -u blogapp git clone \
  https://github.com/buithaild/aws-flask-blog-ha.git \
  /opt/blog/app

cd /opt/blog/app

# 4. Install Python dependencies
sudo -u blogapp python3 -m venv .venv
sudo -u blogapp .venv/bin/python -m pip install \
  -r requirements.txt

# 5. Create application launcher
cat > /opt/blog/start.py <<'PYTHON'
import json
import os
import subprocess

result = subprocess.run(
    [
        "/usr/bin/aws",
        "ssm",
        "get-parameter",
        "--name", "/blog-ha/database-url",
        "--with-decryption",
        "--region", "ap-southeast-1",
        "--output", "json",
    ],
    check=True,
    capture_output=True,
    text=True,
)

database_url = json.loads(
    result.stdout
)["Parameter"]["Value"]

env = os.environ.copy()
env["DATABASE_URL"] = database_url
env["RUNNING_ON_EC2"] = "true"

os.chdir("/opt/blog/app")

os.execve(
    "/opt/blog/app/.venv/bin/gunicorn",
    [
        "gunicorn",
        "--workers", "2",
        "--bind", "0.0.0.0:8000",
        "--timeout", "60",
        "run:app",
    ],
    env,
)
PYTHON

chown root:root /opt/blog/start.py
chmod 755 /opt/blog/start.py

# 6. Create systemd service
cat > /etc/systemd/system/blog.service <<'SERVICE'
[Unit]
Description=Flask Blog Application
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=blogapp
Group=blogapp
WorkingDirectory=/opt/blog/app
ExecStart=/usr/bin/python3 /opt/blog/start.py
Restart=always
RestartSec=10
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
SERVICE

# 7. Start application
systemctl daemon-reload
systemctl enable --now blog

echo "=== Flask Blog bootstrap completed ==="
