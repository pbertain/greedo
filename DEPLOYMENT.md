# Gree.do Deployment Guide

This document describes the deployment setup using GitHub Actions and Ansible for both development and production environments.

## 🚀 Deployment Infrastructure

### Environments

- **Development**: `host78.nird.club:17000` (auto-deploys from `dev` branch)
- **Production**: `host74.nird.club:17000` (manual deployment with confirmation)

### Prerequisites

1. **GitHub Secrets Configuration**
   - `SSH_KEY`: Private SSH key for accessing both servers

2. **Server Requirements**
   - Ubuntu 20.04+ or Debian 11+
   - Python 3.11+
   - Ansible user with sudo privileges
   - SSH access on port 22

## 🔧 Setup Instructions

### 1. Server Preparation

Both servers should have the `ansible` user configured:

```bash
# On each server
sudo useradd -m -s /bin/bash ansible
sudo usermod -aG sudo ansible
sudo mkdir -p /home/ansible/.ssh
sudo cp /root/.ssh/authorized_keys /home/ansible/.ssh/
sudo chown -R ansible:ansible /home/ansible/.ssh
sudo chmod 700 /home/ansible/.ssh
sudo chmod 600 /home/ansible/.ssh/authorized_keys

# Enable passwordless sudo for ansible user
echo "ansible ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible
```

### 2. GitHub Secrets

Add the following secret to your GitHub repository:

```
SSH_KEY: Your private SSH key content
```

## 🔄 Deployment Process

### Development Deployment

**Automatic**: Pushes to the `dev` branch trigger automatic deployment to dev environment.

```bash
git checkout -b dev
git push origin dev
```

**Manual**: You can also trigger the dev deployment manually through GitHub Actions.

### Production Deployment

**Manual Only**: Production deployments require manual trigger with confirmation.

1. Go to GitHub Actions
2. Select "Deploy to Production"
3. Click "Run workflow"
4. Enter `DEPLOY-TO-PROD` in the confirmation field
5. Click "Run workflow"

## 📋 Deployment Components

### Ansible Playbook Features

- **System Updates**: Updates packages and installs dependencies
- **User Management**: Creates dedicated application user
- **Python Environment**: Sets up virtual environment with dependencies
- **Systemd Service**: Configures application as a system service
- **Environment-Specific Nginx**: Deploys nginx configs from `conf/{env}/nginx/` directories
- **Custom Nginx Testing**: Uses `/usr/local/nginx/sbin/nginx -t` for configuration validation
- **Health Checks**: Verifies deployment success
- **Security**: Restrictive permissions and security headers

### Application Structure

```
/opt/{env}/gree-do/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
├── static/              # Static assets (CSS, JS, images)
├── holonet-stamp/       # Core Star Wars time library
├── venv/               # Python virtual environment
└── .env                # Environment configuration

conf/
├── dev/nginx/           # Dev nginx configurations
│   ├── sites-available/ # Available nginx sites
│   └── sites-enabled/   # Enabled nginx sites
└── prod/nginx/          # Production nginx configurations
    ├── sites-available/ # Available nginx sites
    └── sites-enabled/   # Enabled nginx sites
```

### System Services

- **Application**: `systemd` service running Flask app
- **Custom Nginx**: Reverse proxy with custom installation at `/usr/local/nginx/sbin/nginx`
- **Configuration Testing**: Validates nginx config before restart
- **Logs**: Available via `journalctl -u gree-do -f`

## 🔍 Monitoring and Troubleshooting

### Health Checks

Both environments expose health check endpoints:

```bash
# Development
curl http://host78.nird.club:17000/api/health

# Production  
curl http://host74.nird.club:17000/api/health
```

### Service Management

```bash
# Check application status
sudo systemctl status gree-do

# View logs
sudo journalctl -u gree-do -f

# Restart application
sudo systemctl restart gree-do

# Check nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/gree-do_access.log
```

### Manual Deployment

If needed, you can deploy manually using Ansible:

```bash
# For development
cd ansible
ansible-playbook -i inventory/dev.yml deploy.yml

# For production  
cd ansible
ansible-playbook -i inventory/prod.yml deploy.yml
```

## 🔒 Security Features

- **SSH Key Authentication**: No password authentication
- **Dedicated User**: Application runs as `gree-do` user
- **Security Headers**: Nginx adds security headers
- **File Permissions**: Restrictive file and directory permissions
- **Systemd Security**: NoNewPrivileges and filesystem restrictions
- **Nginx Security**: Blocks access to sensitive files

## 🎯 Environment Differences

| Feature | Development | Production |
|---------|-------------|------------|
| Debug Mode | Enabled | Disabled |
| Log Level | DEBUG | INFO |
| Auto-deployment | Yes (on push) | No (manual only) |
| HTTPS | Optional | Recommended |
| Error Details | Verbose | Minimal |

## 📝 Deployment Checklist

### Pre-deployment

- [ ] Code tested locally
- [ ] Tests passing
- [ ] SSH access to target servers confirmed
- [ ] GitHub secrets configured

### Post-deployment

- [ ] Health check endpoint responding
- [ ] All pages loading correctly
- [ ] API endpoints functional
- [ ] Static assets serving properly
- [ ] Logs show no errors

## 🆘 Rollback Procedure

If a deployment fails:

1. **Check logs**: `sudo journalctl -u gree-do -f`
2. **Restart service**: `sudo systemctl restart gree-do`
3. **Revert code**: Deploy previous working version
4. **Manual intervention**: SSH to server if needed

## 📞 Support

For deployment issues:

1. Check GitHub Actions logs
2. Review server logs via SSH
3. Verify service status
4. Check network connectivity

Remember: **Han shot first!** 🚀