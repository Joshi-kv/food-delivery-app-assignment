# AWS EC2 Deployment Guide - Food Delivery App

Complete guide for deploying the Food Delivery App on AWS EC2 with Docker, using SQLite database.

---

## Table of Contents
1. [AWS EC2 Setup](#aws-ec2-setup)
2. [Server Configuration](#server-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Domain & SSL Setup](#domain--ssl-setup)
5. [CI/CD with GitHub Actions](#cicd-with-github-actions)
6. [Maintenance & Monitoring](#maintenance--monitoring)

---

## AWS EC2 Setup

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**
   - Go to https://console.aws.amazon.com
   - Navigate to EC2 Dashboard

2. **Launch Instance**
   - Click "Launch Instance"
   - **Name**: food-delivery-app-server
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: t2.medium (recommended) or t2.small (minimum)
   - **Key Pair**: Create new or select existing SSH key pair (download .pem file)

3. **Configure Storage**
   - Root volume: 20 GB gp3 (minimum)
   - This will store application, Docker images, and SQLite database

4. **Network Settings**
   - Create new security group or use existing
   - **Security Group Rules**:
     - SSH (22) - Your IP only
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
     - Custom TCP (8000) - 0.0.0.0/0 (for testing, remove in production)

5. **Launch Instance**
   - Review and click "Launch Instance"
   - Wait for instance to be in "Running" state
   - Note down the Public IP address

### Step 2: Connect to EC2 Instance

**From Linux/Mac:**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**From Windows (using PuTTY):**
- Convert .pem to .ppk using PuTTYgen
- Use PuTTY to connect with the .ppk key

---

## Server Configuration

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Logout and login again for group changes
exit
# SSH back in
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Verify Docker installation
docker --version
```

### Step 3: Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 4: Install Git

```bash
sudo apt install git -y
git --version
```

### Step 5: Configure Firewall (UFW)

```bash
# Enable UFW
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check status
sudo ufw status
```

---

## Docker Deployment

### Step 1: Clone Repository

```bash
# Create application directory
sudo mkdir -p /app/food-delivery-app
sudo chown ubuntu:ubuntu /app/food-delivery-app
cd /app/food-delivery-app

# Clone your repository
git clone https://github.com/YOUR_USERNAME/food-delivery-app-assignment.git .
```

### Step 2: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit environment file
nano .env
```

**Production .env configuration:**
```env
# Django Settings
SECRET_KEY=your-very-secure-random-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=YOUR_EC2_PUBLIC_IP,yourdomain.com,www.yourdomain.com

# Database Configuration (SQLite)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
```

**Generate SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Create Docker Volumes Directory

```bash
# Create directories for persistent data
mkdir -p /app/food-delivery-app/data
mkdir -p /app/food-delivery-app/staticfiles
mkdir -p /app/food-delivery-app/media

# Set permissions
chmod -R 755 /app/food-delivery-app/data
```

### Step 4: Update docker-compose.yml for SQLite

Create/update `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 food_delivery_app.asgi:application
    restart: always
    volumes:
      - ./data:/app/data
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./db.sqlite3:/app/db.sqlite3
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis_data:
```

### Step 5: Build and Start Application

```bash
# Build Docker images
docker-compose build

# Start containers
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### Step 6: Initialize Application

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Setup RBAC
docker-compose exec web python manage.py setup_rbac
```

### Step 7: Test Application

```bash
# Check logs
docker-compose logs -f web

# Test application
curl http://localhost:8000
```

Access from browser: `http://YOUR_EC2_PUBLIC_IP:8000`

---

## Deployment Options

### Option A: Without Domain (Direct Access via IP)

If you don't have a domain, you can run the application directly on port 80:

**Update docker-compose.yml to use port 80:**
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: daphne -b 0.0.0.0 -p 80 food_delivery_app.asgi:application
    restart: always
    volumes:
      - ./data:/app/data
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./db.sqlite3:/app/db.sqlite3
    ports:
      - "80:80"
    env_file:
      - .env
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis_data:
```

**Restart application:**
```bash
docker-compose down
docker-compose up -d --build
```

**Access application:** `http://YOUR_EC2_PUBLIC_IP`

**Pros:**
- Simple setup
- No additional software needed
- Direct access via IP

**Cons:**
- No SSL/HTTPS (not secure for production)
- No caching or optimization
- Port 80 requires sudo or Docker

---

### Option B: With Domain & Nginx (Recommended for Production)

### Step 1: Configure Domain

1. **Purchase domain** from provider (GoDaddy, Namecheap, Route53, etc.)

2. **Add DNS A Record**:
   - Type: A
   - Name: @ (or subdomain)
   - Value: YOUR_EC2_PUBLIC_IP
   - TTL: 300

3. **Wait for DNS propagation** (5-30 minutes)

### Step 2: Install Nginx

```bash
sudo apt update
sudo apt install nginx -y

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 3: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/food-delivery-app
```

**Nginx configuration:**
```nginx
upstream django_app {
    server localhost:8000;
}

server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    # WebSocket support
    location /ws/ {
        proxy_pass http://django_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Application
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /app/food-delivery-app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/food-delivery-app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

**Enable site:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/food-delivery-app /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 4: Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect HTTP to HTTPS (option 2)

# Test auto-renewal
sudo certbot renew --dry-run
```

**Access application:** `https://yourdomain.com`

**Note:** If you don't have a domain, skip this entire section and use Option A above.

---

## CI/CD with GitHub Actions

### Step 1: Generate SSH Key on EC2

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions_key -N ""

# Add public key to authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# Display private key (copy this for GitHub secrets)
cat ~/.ssh/github_actions_key
```

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

1. **DOCKER_USERNAME**: Your Docker Hub username
2. **DOCKER_PASSWORD**: Your Docker Hub password/token
3. **SERVER_HOST**: Your EC2 Public IP
4. **SERVER_USERNAME**: `ubuntu`
5. **SERVER_SSH_KEY**: Private key from previous step
6. **SERVER_PORT**: `22`

### Step 3: Update GitHub Actions Workflow

The workflow file `.github/workflows/ci-cd.yml` is already configured. Update the deploy script:

```yaml
deploy:
  name: Deploy to AWS EC2
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  
  steps:
  - name: Deploy to EC2
    uses: appleboy/ssh-action@v1.0.0
    with:
      host: ${{ secrets.SERVER_HOST }}
      username: ${{ secrets.SERVER_USERNAME }}
      key: ${{ secrets.SERVER_SSH_KEY }}
      port: ${{ secrets.SERVER_PORT }}
      script: |
        cd /app/food-delivery-app
        git pull origin main
        docker-compose pull
        docker-compose up -d --build
        docker-compose exec -T web python manage.py migrate
        docker-compose exec -T web python manage.py collectstatic --noinput
        docker system prune -f
```

### Step 4: Test CI/CD Pipeline

```bash
# Make a change and push to main branch
git add .
git commit -m "Test CI/CD deployment"
git push origin main

# Check GitHub Actions tab for pipeline status
```

---

## Maintenance & Monitoring

### Backup SQLite Database

**Manual backup:**
```bash
# Backup database
docker-compose exec web python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Copy database file
cp /app/food-delivery-app/db.sqlite3 /app/food-delivery-app/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3
```

**Automated backup script:**
```bash
# Create backup script
nano /app/food-delivery-app/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/app/food-delivery-app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /app/food-delivery-app/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /app/food-delivery-app/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /app/food-delivery-app/backup.sh >> /app/food-delivery-app/backup.log 2>&1
```

### View Logs

```bash
# Application logs
docker-compose logs -f web

# Redis logs
docker-compose logs -f redis

# Nginx logs (if using Nginx)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u docker -f
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check Docker stats
docker stats

# Check running containers
docker-compose ps
```

### Update Application

```bash
cd /app/food-delivery-app

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Clean up old images
docker system prune -f
```

### Restart Services

```bash
# Restart application
docker-compose restart web

# Restart all containers
docker-compose restart

# Restart Nginx (if using Nginx)
sudo systemctl restart nginx

# Restart entire stack
docker-compose down && docker-compose up -d
```

---

## Troubleshooting

### Application Not Accessible

**Check containers:**
```bash
docker-compose ps
docker-compose logs web
```

**Check Nginx (if using Nginx):**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Check firewall:**
```bash
sudo ufw status
```

### Database Issues

**Check database file:**
```bash
ls -lh /app/food-delivery-app/db.sqlite3
```

**Reset database (WARNING: deletes all data):**
```bash
docker-compose down
rm /app/food-delivery-app/db.sqlite3
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py setup_rbac
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a -f
docker volume prune -f

# Clean old logs
sudo journalctl --vacuum-time=7d
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## Security Best Practices

### 1. Secure SSH Access
```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

### 2. Configure Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Updates
```bash
# Update system weekly
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 4. Monitor Logs
```bash
# Check for suspicious activity
sudo tail -100 /var/log/auth.log
```

### 5. Backup Regularly
- Enable automated backups (see backup section)
- Store backups in S3 or external storage
- Test restore procedures

---

## Cost Optimization

### EC2 Instance Sizing
- **t2.micro** (1GB RAM): Testing only
- **t2.small** (2GB RAM): Light production (< 100 users)
- **t2.medium** (4GB RAM): Recommended for production

### Storage
- Use gp3 volumes (cheaper than gp2)
- Clean up old Docker images regularly
- Compress old backups

### Data Transfer
- Use CloudFront CDN for static files
- Enable gzip compression in Nginx

---

## Quick Reference Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f web

# Restart application
docker-compose restart web

# Update application
cd /app/food-delivery-app && git pull && docker-compose up -d --build

# Backup database
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# Check status
docker-compose ps

# Check Nginx status (if using Nginx)
sudo systemctl status nginx
```

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f web`
- Review GitHub Actions: Repository → Actions tab
- AWS Support: https://console.aws.amazon.com/support/

---

**Deployment Complete!** Your Food Delivery App is now running on AWS EC2 with Docker.
