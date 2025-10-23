# Quick Deployment Guide - AWS EC2

Your EC2 IP: **3.27.71.144**

## Step-by-Step Deployment

### Step 1: Connect to EC2

```bash
chmod 400 food_delivery_app_key.pem
ssh -i food_delivery_app_key.pem ubuntu@3.27.71.144
```

### Step 2: Update System & Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y

# Logout and login again
exit
```

### Step 3: Reconnect and Setup Application

```bash
# Reconnect to EC2
ssh -i food_delivery_app_key.pem ubuntu@3.27.71.144

# Verify Docker
docker --version
docker-compose --version

# Create app directory
sudo mkdir -p /app/food-delivery-app
sudo chown ubuntu:ubuntu /app/food-delivery-app
cd /app/food-delivery-app

# Clone your repository (replace with your GitHub repo URL)
git clone https://github.com/YOUR_USERNAME/food-delivery-app-assignment.git .
```

### Step 4: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Generate SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env file
nano .env
```

**Update .env with these values:**
```env
SECRET_KEY=<paste-generated-secret-key-here>
DEBUG=False
ALLOWED_HOSTS=3.27.71.144

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

REDIS_HOST=redis
REDIS_PORT=6379
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 5: Deploy Application

```bash
# Build and start containers
docker-compose up -d --build

# Wait for containers to start (30 seconds)
sleep 30

# Check if containers are running
docker-compose ps

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser (follow prompts)
docker-compose exec web python manage.py createsuperuser

# Setup RBAC
docker-compose exec web python manage.py setup_rbac
```

### Step 6: Access Your Application

Open browser and go to: **http://3.27.71.144**

- **Customer Signup**: http://3.27.71.144/signup/
- **Delivery Partner Signup**: http://3.27.71.144/delivery-signup/
- **Admin Login**: http://3.27.71.144/admin-login/

---

## GitHub Actions CI/CD Setup

### Step 1: Get PEM Key Content

On your local machine:
```bash
cat food_delivery_app_key.pem
```

Copy the entire output (including BEGIN and END lines).

### Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these 4 secrets:

| Secret Name | Value |
|------------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password |
| `EC2_HOST` | `3.27.71.144` |
| `EC2_PEM_KEY` | Paste entire .pem file content |

### Step 3: Test CI/CD

```bash
# Make a change and push
git add .
git commit -m "Test deployment"
git push origin main

# Check GitHub Actions tab to see deployment progress
```

---

## Useful Commands

### View Logs
```bash
# Application logs
docker-compose logs -f web

# Redis logs
docker-compose logs -f redis

# All logs
docker-compose logs -f
```

### Restart Application
```bash
docker-compose restart web
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose up -d
```

### Update Application
```bash
cd /app/food-delivery-app
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup Database
```bash
# Create backup directory
mkdir -p /app/food-delivery-app/backups

# Backup database
cp /app/food-delivery-app/db.sqlite3 /app/food-delivery-app/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3
```

### Check Container Status
```bash
docker-compose ps
docker stats
```

---

## Troubleshooting

### Application not accessible
```bash
# Check if containers are running
docker-compose ps

# Check logs for errors
docker-compose logs web

# Restart containers
docker-compose restart
```

### Port 80 already in use
```bash
# Check what's using port 80
sudo lsof -i :80

# If it's Apache or Nginx, stop it
sudo systemctl stop apache2
sudo systemctl stop nginx
```

### Database locked error
```bash
docker-compose down
docker-compose up -d
```

### Out of disk space
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a -f
docker volume prune -f
```

---

## Security Checklist

- [ ] Changed SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Updated ALLOWED_HOSTS with your IP
- [ ] Created strong superuser password
- [ ] EC2 Security Group allows only necessary ports
- [ ] SSH key has proper permissions (chmod 400)

---

## Next Steps

1. **Test the application** - Create test bookings
2. **Setup automated backups** - Schedule daily database backups
3. **Monitor logs** - Check for errors regularly
4. **Get a domain** (optional) - For SSL/HTTPS support
5. **Setup monitoring** - Use CloudWatch or similar

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f web`
2. Verify containers: `docker-compose ps`
3. Check EC2 security group allows port 80
4. Ensure .env file is configured correctly

Your app should now be live at: **http://3.27.71.144** 🚀
