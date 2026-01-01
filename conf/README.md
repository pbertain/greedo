# Environment-Specific Nginx Configurations

This directory contains nginx configuration files for different deployment environments.

## Structure

```
conf/
├── dev/nginx/           # Development environment
│   ├── sites-available/ # Available nginx sites
│   └── sites-enabled/   # Enabled nginx sites
└── prod/nginx/          # Production environment
    ├── sites-available/ # Available nginx sites
    └── sites-enabled/   # Enabled nginx sites
```

## Deployment

The Ansible playbook (`ansible/deploy.yml`) automatically:

1. Copies the appropriate environment configurations to `/etc/nginx/`
2. Tests the nginx configuration using `/usr/local/nginx/sbin/nginx -t`
3. Restarts nginx using `systemctl restart nginx` only if tests pass

## Custom Nginx Installation

This setup is designed to work with a custom nginx installation where:
- Nginx binary is located at: `/usr/local/nginx/sbin/nginx`
- Configuration testing uses the custom binary path
- Service management still uses systemctl for the nginx service

## Configuration Files

Each environment should have its nginx configuration files pre-configured with:
- Appropriate server settings
- Proxy configurations pointing to the Flask application
- Security headers and SSL settings (if applicable)
- Static file serving optimizations

The configuration files are deployed as-is, so ensure they are properly configured for each environment before deployment.