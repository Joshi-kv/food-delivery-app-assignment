# GitHub Actions CI/CD Setup for AWS EC2

## Required GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

### 1. Docker Hub Credentials
- **DOCKER_USERNAME**: Your Docker Hub username
- **DOCKER_PASSWORD**: Your Docker Hub password or access token

### 2. AWS EC2 Credentials
- **EC2_HOST**: Your EC2 instance public IP address (e.g., `54.123.45.67`)
- **EC2_PEM_KEY**: Your EC2 private key (.pem file content)

**Note:** Username defaults to `ubuntu` and port defaults to `22`

## How to Get AWS EC2 SSH Key

### Method 1: Use Existing Key Pair
If you already have the .pem file from EC2 instance creation:

```bash
# Display the private key content
cat your-key.pem

# Copy the entire output including:
# -----BEGIN RSA PRIVATE KEY-----
# ... key content ...
# -----END RSA PRIVATE KEY-----
```

Paste this entire content into the **AWS_EC2_SSH_KEY** secret.

### Method 2: Generate New Key on EC2
If you need to create a new key for GitHub Actions:

1. **SSH into your EC2 instance:**
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

2. **Generate a new SSH key pair:**
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions_key -N ""
```

3. **Add public key to authorized_keys:**
```bash
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

4. **Display private key (copy this for GitHub secret):**
```bash
cat ~/.ssh/github_actions_key
```

5. **Test the key:**
```bash
# From your local machine
ssh -i github_actions_key ubuntu@YOUR_EC2_IP
```

## Pipeline Workflow

### Trigger Events
- **Push to main branch**: Runs full pipeline (test → build → deploy)
- **Pull request to main**: Runs tests only

### Pipeline Stages

#### 1. Test Stage
- Sets up Python 3.11 and Redis
- Installs dependencies
- Runs database migrations
- Executes Django tests
- Checks code style with flake8

#### 2. Build Stage
- Builds Docker image
- Pushes to Docker Hub with tags:
  - `latest` - Always points to the latest build
  - `<commit-sha>` - Specific version tag

#### 3. Deploy Stage (AWS EC2)
- SSH into EC2 instance
- Pull latest code from GitHub
- Pull latest Docker image
- Stop existing containers
- Start new containers
- Run database migrations
- Collect static files
- Clean up old Docker images

## Setup Instructions

### Step 1: Prepare EC2 Instance

Ensure your EC2 instance has:
- Docker installed
- Docker Compose installed
- Application directory at `/app/food-delivery-app`
- Git repository cloned

### Step 2: Configure GitHub Secrets

Add all required secrets as listed above.

### Step 3: Test Deployment

1. Make a small change to your code
2. Commit and push to main branch:
```bash
git add .
git commit -m "Test CI/CD deployment"
git push origin main
```

3. Monitor the pipeline:
   - Go to your GitHub repository
   - Click on **Actions** tab
   - Watch the workflow progress

### Step 4: Verify Deployment

After successful deployment:
```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f web

# Access application
curl http://localhost
```

## Troubleshooting

### Pipeline Fails at Deploy Stage

**Error: Permission denied (publickey)**
- Verify EC2_PEM_KEY is correct (entire .pem file content)
- Ensure EC2 instance is using the correct key pair
- Check EC2 instance is Ubuntu (username: ubuntu)

**Error: Connection timeout**
- Verify EC2_HOST is correct public IP
- Check EC2 security group allows SSH (port 22) from anywhere (0.0.0.0/0)
- Ensure EC2 instance is running

### Docker Pull Fails

**Error: Authentication required**
- Verify DOCKER_USERNAME and DOCKER_PASSWORD are correct
- Check Docker Hub credentials

### Migration Fails

**Error: Database is locked**
- Stop containers: `docker-compose down`
- Start again: `docker-compose up -d`
- Retry deployment

### Application Not Accessible

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs web

# Restart containers
docker-compose restart
```

## Manual Deployment

If you need to deploy manually without CI/CD:

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Navigate to app directory
cd /app/food-delivery-app

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Security Best Practices

1. **Never commit secrets to repository**
   - Use GitHub Secrets for all sensitive data
   - Add `.env` to `.gitignore`

2. **Rotate SSH keys regularly**
   - Generate new keys every 90 days
   - Update GitHub secrets

3. **Limit SSH access**
   - Configure EC2 security group to allow SSH only from necessary IPs
   - Consider using GitHub Actions IP ranges

4. **Monitor deployments**
   - Check GitHub Actions logs regularly
   - Set up notifications for failed deployments

## Notifications (Optional)

Add Slack/Email notifications for deployment status:

```yaml
- name: Notify deployment status
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Rollback

If deployment fails, rollback to previous version:

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Navigate to app directory
cd /app/food-delivery-app

# Checkout previous commit
git log --oneline  # Find previous commit hash
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

For more information, see the main [DEPLOYMENT.md](../../DEPLOYMENT.md) guide.
