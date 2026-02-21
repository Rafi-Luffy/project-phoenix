# GitHub Configuration Directory

**Purpose**: GitHub-specific configuration, workflows, and documentation  
**Last Updated**: December 28, 2025  

---

## 📁 Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflows
│   ├── build-docker.yml       # Build & push Docker image
│   ├── deploy-staging.yml     # Deploy to staging
│   ├── deploy-production.yml  # Deploy to production
│   ├── test-integration.yml   # Run integration tests
│   ├── code-quality.yml       # Code quality checks
│   └── release.yml            # Create releases
├── WORKFLOWS_SETUP.md       # Setup and configuration guide
├── QUICK_REFERENCE.md       # Quick reference card
└── README.md               # This file
```

---

## 🚀 Getting Started

### 1. Initial Setup (First Time)

Follow [WORKFLOWS_SETUP.md](WORKFLOWS_SETUP.md) for:
- AWS IAM role creation
- OIDC provider setup
- GitHub secrets configuration
- GitHub branch protection

**Time**: ~30 minutes

### 2. First Deployment

```bash
# 1. Push code to develop
git push origin develop
# Automatically triggers build-docker and deploy-staging

# 2. Monitor workflow
gh run list --workflow=build-docker.yml

# 3. Check staging deployment
kubectl get deployment -n phoenix

# 4. Create release
git tag v1.0.0
git push origin v1.0.0
# Manually approve production deployment

# 5. Deploy to production
# Approval required in GitHub
```

### 3. Daily Development

```bash
# Feature development
git checkout -b feature/your-feature
git commit -m "feat: description"
git push origin feature/your-feature
# Create PR, status checks run automatically

# Merge when ready
git merge develop
git push origin develop
# Auto-deploys to staging
```

---

## 📋 Workflow Overview

### 1. build-docker.yml
**Triggers**: Push, PR, tags  
**Duration**: 5-10 minutes  
**Purpose**: Build Docker image and push to ECR

```yaml
Stages:
  1. Build Docker image with Buildx
  2. Run tests (unit, integration)
  3. Security scanning (Trivy, Bandit, Semgrep)
  4. Push to ECR
  5. Archive results
```

### 2. deploy-staging.yml
**Triggers**: develop push, build completion  
**Duration**: 5-15 minutes  
**Purpose**: Deploy to staging EKS cluster

```yaml
Stages:
  1. Configure AWS credentials
  2. Validate Helm chart
  3. Deploy with Helm
  4. Health checks (30 attempts)
  5. Smoke tests
  6. Slack notification
```

### 3. deploy-production.yml
**Triggers**: main push (approval), tags, manual  
**Duration**: 10-20 minutes  
**Purpose**: Deploy to production with safeguards

```yaml
Stages:
  1. Approval gate
  2. Image verification
  3. Backup current release
  4. Deploy with Helm (atomic)
  5. Health checks (60 attempts)
  6. Pod stability monitoring
  7. Smoke tests
  8. Automatic rollback (if failed)
```

### 4. test-integration.yml
**Triggers**: Push, PR, scheduled daily  
**Duration**: 10-20 minutes  
**Purpose**: Comprehensive testing

```yaml
Services:
  - PostgreSQL 15
  - Redis 7

Tests:
  - Integration tests
  - API endpoint tests
  - Performance tests
  - E2E tests (Docker Compose)
```

### 5. code-quality.yml
**Triggers**: Push, PR, scheduled weekly  
**Duration**: 10-15 minutes  
**Purpose**: Code quality and security

```yaml
Jobs:
  - Linting (flake8, black, isort, pylint)
  - Type checking (mypy)
  - Dependency scanning (safety, pip-audit)
  - SAST (Semgrep)
  - Code coverage (80% minimum)
```

### 6. release.yml
**Triggers**: Tags, manual dispatch  
**Duration**: 5-10 minutes  
**Purpose**: Create releases and tag images

```yaml
Jobs:
  - Generate changelog
  - Create GitHub release
  - Build and push Docker image
  - Security scan release image
```

---

## 🔐 Configuration Checklist

### GitHub Secrets (Required)

Set in: Settings → Secrets and variables → Actions

```bash
# AWS credentials (OIDC)
AWS_ACCOUNT_ID              = 123456789012
AWS_ROLE_TO_ASSUME          = arn:aws:iam::123456789012:role/...
AWS_REGION                  = us-east-1

# Slack notifications (optional)
SLACK_WEBHOOK_URL           = https://hooks.slack.com/...
```

### Branch Protection Rules (Recommended)

Set in: Settings → Branches → main

```yaml
Require status checks before merging:
  - build (build-docker.yml)
  - test (test-integration.yml)
  - code-quality (code-quality.yml)

Require code reviews: 1 approval

Dismiss stale reviews: true

Require branches to be up to date: true
```

### Deployment Environments (For Production)

Set in: Settings → Environments → production

```yaml
Environment protection rules:
  - Required reviewers: Team lead, DevOps lead
  
Secrets:
  - DATABASE_PASSWORD (if needed)
  - PRODUCTION_SLACK_URL (if different)
```

---

## 📚 Documentation Files

### WORKFLOWS_SETUP.md (1,400+ lines)
Complete setup guide including:
- AWS IAM role creation
- OIDC provider configuration
- GitHub secrets setup
- Workflow-specific configuration
- Troubleshooting procedures
- Security best practices

**When to use**: First-time setup, troubleshooting, permission issues

### QUICK_REFERENCE.md (280+ lines)
Quick reference for common tasks:
- Push and deploy commands
- Status checking
- Troubleshooting quick fixes
- Critical endpoints
- Security reminders

**When to use**: During development, quick lookup

### CI_CD_PIPELINE_GUIDE.md (in root)
Comprehensive pipeline documentation:
- Workflow details
- Configuration options
- Deployment procedures
- Health check specifications
- Best practices

**When to use**: Understanding the system, team training

### TASK_8_COMPLETION_REPORT.md (in root)
Technical task documentation:
- Design decisions
- Architecture details
- Performance metrics
- Integration points

**When to use**: Reference, knowledge transfer

---

## 🎯 Common Tasks

### Deploy Code to Staging

```bash
# Option 1: Automatic (on develop push)
git commit -m "feat: new feature"
git push origin develop
# Automatically builds and deploys

# Option 2: Manual (specific image)
gh workflow run deploy-staging.yml \
  --ref develop \
  -f image-tag=v1.0.0-rc1

# Check progress
gh run list --workflow=deploy-staging.yml
gh run view <run-id> --log
```

### Deploy to Production

```bash
# Option 1: Tag-based (automatic with approval)
git tag v1.0.0
git push origin v1.0.0
# Requires approval in GitHub

# Option 2: Manual (specific image)
gh workflow run deploy-production.yml \
  --ref main \
  -f image-tag=v1.0.0

# Check status
gh run view <run-id> --log
```

### Rollback Production

```bash
# Using Helm (fastest)
helm rollback phoenix-api -n phoenix

# Or deploy previous version
git tag v0.9.9
git push origin v0.9.9
# Approve deployment
```

### Check Workflow Logs

```bash
# List recent runs
gh run list --workflow=deploy-production.yml --limit=5

# View specific run
gh run view <run-id>

# View full logs
gh run view <run-id> --log

# View specific job logs
gh run view <run-id> --job=<job-id> --log

# Download artifacts
gh run download <run-id>
```

---

## 🔍 Status Checks

### See All Workflow Status

```bash
# View in GitHub
https://github.com/owner/repo/actions

# View in terminal
gh run list --workflow=all --limit=10
gh workflow list
```

### Monitor Deployment

```bash
# Staging
gh run list --workflow=deploy-staging.yml
kubectl get deployment -n phoenix phoenix-api

# Production
gh run list --workflow=deploy-production.yml
kubectl get deployment -n phoenix phoenix-api -w
```

### Check Test Results

```bash
# Latest test run
gh run list --workflow=test-integration.yml --limit=1
gh run view <run-id> --log

# Download test report
gh run download <run-id> -n test-report
open test-report.html
```

---

## 🐛 Troubleshooting

### Workflow Won't Start

**Problem**: Workflow not triggering on push

**Solution**:
1. Check syntax: `gh workflow view build-docker.yml`
2. Check triggers: Look for `on:` section
3. Check if file is in `.github/workflows/`
4. File must end with `.yml` or `.yaml`

### Build Fails

**Problem**: `docker build` or `push` fails

**Solution**:
```bash
# Check logs
gh run view <run-id> --job=build --log

# Test locally
docker build -f Dockerfile.backend .

# Check AWS credentials
aws sts get-caller-identity

# Check ECR access
aws ecr describe-repositories --region us-east-1
```

### Deployment Fails

**Problem**: Helm deployment or health checks fail

**Solution**:
```bash
# Check pod status
kubectl get pods -n phoenix

# View pod logs
kubectl logs -n phoenix -l app=phoenix-api --tail=50

# Describe pod for events
kubectl describe pod -n phoenix <pod-name>

# Check events
kubectl get events -n phoenix

# Rollback if needed
helm rollback phoenix-api -n phoenix
```

### Health Check Timeout

**Problem**: Deployment hangs at health check

**Solution**:
```bash
# Test endpoint manually
kubectl port-forward -n phoenix svc/phoenix-api 8000:80
curl localhost:8000/health

# Check pod readiness
kubectl get pods -n phoenix -o wide

# Check if pod is running
kubectl get pod -n phoenix <pod-name> -o jsonpath='{.status.phase}'

# Increase timeout (if needed)
helm upgrade phoenix-api ./helm/phoenix-api \
  --set readinessProbe.timeoutSeconds=10
```

---

## 🔒 Security Notes

### Secrets Management

✅ **DO**:
- Use GitHub secrets for sensitive data
- Rotate secrets periodically
- Use OIDC for AWS access (no long-lived keys)
- Review secret usage in workflows

❌ **DON'T**:
- Commit secrets to repository
- Use AWS access keys in workflows
- Log secret values
- Share secrets in chat/email

### Workflow Security

✅ **DO**:
- Require approvals for production
- Enable branch protection rules
- Run security scanning
- Use minimal IAM permissions

❌ **DON'T**:
- Allow direct pushes to main
- Skip status checks
- Run workflows on untrusted PRs
- Grant excessive IAM permissions

---

## 📈 Monitoring and Alerts

### Setup Slack Notifications

1. Get webhook: https://api.slack.com/messaging/webhooks
2. Set secret: `gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/..."`
3. Test: Create a tag and deploy
4. Messages sent to Slack on: build success/fail, deployment complete, release created

### Email Notifications

GitHub Actions sends emails by default for:
- Workflow failures
- Approval required
- Release created

Configure in: Settings → Notifications

### GitHub Status Checks

All workflows appear as status checks on:
- Pull requests (blocking merge)
- Commit status
- Branch protection rules

---

## 📞 Support and Help

### Quick Links

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Troubleshooting**: See WORKFLOWS_SETUP.md

### Common Issues

1. **Secrets not working**: Check syntax in workflow (use `${{ secrets.SECRET_NAME }}`)
2. **Workflow not running**: Check file location (`.github/workflows/`) and syntax
3. **Deployment fails**: Check pod logs and health check endpoint
4. **Images not building**: Test locally: `docker build -f Dockerfile.backend .`

### Team Questions

- Workflow syntax: See documentation in this directory
- Deployment issues: Check `.github/QUICK_REFERENCE.md`
- Setup issues: Follow `.github/WORKFLOWS_SETUP.md`
- Technical details: Read root `CI_CD_PIPELINE_GUIDE.md`

---

## 🎓 Learning Resources

### Recommended Reading Order

1. **Quick Reference** (5 minutes): `.github/QUICK_REFERENCE.md`
2. **Setup Guide** (30 minutes): `.github/WORKFLOWS_SETUP.md`
3. **Pipeline Guide** (1 hour): Root `CI_CD_PIPELINE_GUIDE.md`
4. **Task Report** (30 minutes): Root `TASK_8_COMPLETION_REPORT.md`

### Practice Exercises

1. **Push to develop**: `git push origin develop` and watch workflows
2. **Manual deployment**: `gh workflow run deploy-staging.yml`
3. **Check logs**: `gh run list` and `gh run view <run-id> --log`
4. **Create release**: `git tag v1.0.0 && git push origin v1.0.0`

---

## 📅 Maintenance Schedule

### Daily
- Monitor workflow runs
- Check Slack notifications
- Review failed deployments

### Weekly
- Review workflow logs
- Update documentation if needed
- Check security scanning results

### Monthly
- Rotate secrets (optional)
- Review IAM permissions
- Update workflow dependencies

### Quarterly
- Update GitHub Actions versions
- Review security posture
- Plan workflow improvements

---

## ✅ Verification Checklist

Before going live:

- [ ] AWS IAM role created
- [ ] OIDC provider configured
- [ ] GitHub secrets set (AWS_ACCOUNT_ID, AWS_ROLE_TO_ASSUME, etc.)
- [ ] Workflows visible in GitHub Actions tab
- [ ] Test build workflow with first push
- [ ] Staging deployment successful
- [ ] Production approval configured
- [ ] Slack notifications working (optional)
- [ ] Team trained on QUICK_REFERENCE.md
- [ ] Documentation shared with team

---

## 🚀 Next Steps

1. **Setup** (30 min): Follow WORKFLOWS_SETUP.md
2. **Test** (15 min): Push to develop and verify build
3. **Deploy** (10 min): Deploy to staging manually
4. **Production** (5 min): Approve production deployment
5. **Monitor** (ongoing): Watch metrics and logs

---

**Version**: 1.0  
**Last Updated**: December 28, 2025  
**Status**: ✅ Ready to Use

