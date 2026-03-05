# Personal Dev Config Package

**Version:** 1.0.0  
**For:** Freelancers, Indie Developers, Personal Projects, Small Teams  
**Supports:** GitHub • GitLab • Bitbucket • Gitea • Multi-platform  

---

## 🎯 What Is This?

A **lightweight, no-corporate-BS** development environment config for indie developers!

**Perfect for:**
- 👤 Freelancers building client projects
- 🚀 Indie developers shipping side projects
- 📚 Students learning to code
- 🌟 Open source contributors
- 👥 Small teams (2-5 people)
- 🏠 Remote developers

**NOT for:**
- ❌ Corporate environments (use walmart-config or acme-corp-config instead)
- ❌ Teams requiring VPN/proxy
- ❌ Enterprise compliance

---

## ✨ Features

### ✅ No Corporate Hassles
- **No VPN required**
- **No proxy configuration**
- **No enterprise approvals**
- **No mandatory tools**
- **YOUR code, YOUR rules!**

### 🐙 Multi-Platform Support

Pre-configured profiles for:

| Platform | Best For | Free Tier |
|----------|----------|----------|
| **GitHub** | Portfolio, OSS, job hunting | Unlimited repos, 2000 Actions min/mo |
| **GitLab** | Better CI/CD, self-hosting | Unlimited repos, 400 CI min/mo |
| **Bitbucket** | Atlassian ecosystem | Unlimited repos, 50 Pipeline min/mo |
| **Gitea** | Privacy, self-hosting, learning | Free (self-host) |
| **Multi-platform** | Using multiple platforms | Mix & match! |

### 💸 Free Tier Friendly

**All recommended tools have free options:**
- ✅ Deployment: Vercel, Netlify, Render, Railway, Fly.io
- ✅ Backend: Supabase, Firebase, PlanetScale
- ✅ Learning: freeCodeCamp, The Odin Project, MDN
- ✅ Tools: VS Code, Postman, DBeaver (all free!)

---

## 🚀 Quick Start

### 1. Install Package

```bash
cd prism
python3 scripts/package_manager.py install personal-dev-config
```

### 2. Choose Your Platform Profile

**Option A: GitHub (most popular)**
```bash
cp config/profiles/github.yaml config/user-profile.yaml
```

**Option B: GitLab (better CI/CD)**
```bash
cp config/profiles/gitlab.yaml config/user-profile.yaml
```

**Option C: Bitbucket**
```bash
cp config/profiles/bitbucket.yaml config/user-profile.yaml
```

**Option D: Gitea (self-hosted)**
```bash
cp config/profiles/gitea.yaml config/user-profile.yaml
```

**Option E: Multi-platform (using multiple)**
```bash
cp config/profiles/multi-platform.yaml config/user-profile.yaml
```

### 3. Edit Your Profile

```bash
# Update with YOUR info:
code config/user-profile.yaml

# Update:
# - name: "Your Name"
# - email: "your-email@example.com"
# - username: "your-username"
```

### 4. Run Installer

```bash
python3 install-ui.py
```

**Or CLI:**
```bash
python3 install.py
```

### 5. Set Up SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy to clipboard
pbcopy < ~/.ssh/id_ed25519.pub  # macOS
# or
cat ~/.ssh/id_ed25519.pub       # Linux/Windows

# Add to your platform:
# GitHub:    https://github.com/settings/keys
# GitLab:    https://gitlab.com/-/profile/keys
# Bitbucket: https://bitbucket.org/account/settings/ssh-keys/
# Gitea:     https://your-gitea.com/user/settings/keys
```

### 6. Start Coding! 🎉

```bash
# Clone your repos
gh repo clone your-username/your-repo  # GitHub
glab repo clone your-username/your-repo  # GitLab
git clone git@bitbucket.org:your-username/your-repo.git  # Bitbucket

# Start building!
code your-repo/
```

---

## 📚 What's Included

### Base Configuration

**File:** `base/personal-dev.yaml`

- ✅ Git configuration (no corporate settings!)
- ✅ Minimal tool requirements
- ✅ Optional tools (install what YOU need)
- ✅ Free cloud platform suggestions
- ✅ Project organization structure
- ✅ Learning resources

### Platform Profiles

**Directory:** `profiles/`

| Profile | File | What's Configured |
|---------|------|------------------|
| GitHub | `github.yaml` | GitHub CLI, Actions, SSH, repos |
| GitLab | `gitlab.yaml` | GitLab CLI, CI/CD, registry, SSH |
| Bitbucket | `bitbucket.yaml` | Pipelines, SSH, Atlassian tools |
| Gitea | `gitea.yaml` | Gitea CLI, self-hosted config, SSH |
| Multi-platform | `multi-platform.yaml` | Multiple SSH keys, conditional git config |

### Welcome Page

**File:** `welcome.yaml`

- ✅ Indie developer welcome message
- ✅ Platform selection guidance
- ✅ Free tier tips
- ✅ Community links
- ✅ Troubleshooting

### Resources

**File:** `resources.yaml`

**60+ free resources:**
- 🐙 Git platforms (GitHub, GitLab, Bitbucket, Gitea)
- 🚀 Deployment (Vercel, Netlify, Render, Railway, Fly.io)
- 🔥 Backend services (Supabase, Firebase, PlanetScale)
- 🎓 Learning (freeCodeCamp, Odin Project, MDN)
- 🛠️ Developer tools (VS Code, Postman, DBeaver)
- 🎨 Design assets (Figma, Unsplash, Heroicons)
- 💼 Freelance platforms (Upwork, Toptal, Fiverr)

---

## 🤔 Which Platform Should I Choose?

### 🐙 GitHub

**Use if:**
- ✅ Building your portfolio
- ✅ Looking for jobs (recruiters use GitHub!)
- ✅ Contributing to open source
- ✅ Want the largest developer community

**Pros:**
- Biggest community
- Best for portfolio visibility
- GitHub Actions (CI/CD)
- Free private repos
- GitHub Pages (free hosting)

**Cons:**
- Limited CI/CD minutes (2000/month)
- Corporate owned (Microsoft)

**Free Tier:** Unlimited repos, 2000 Actions minutes/month

---

### 🦊 GitLab

**Use if:**
- ✅ Want better CI/CD for free
- ✅ Considering self-hosting
- ✅ Building complex pipelines
- ✅ Need container registry

**Pros:**
- Better free CI/CD (400 min/month + more features)
- Built-in container registry
- Can self-host (full control!)
- GitLab Pages
- Issue tracking & boards

**Cons:**
- Smaller community than GitHub
- Less portfolio visibility

**Free Tier:** Unlimited repos, 400 CI/CD minutes/month, 5 GB storage

---

### 🚣 Bitbucket

**Use if:**
- ✅ Using Jira or Confluence
- ✅ Small team (up to 5 users)
- ✅ Atlassian ecosystem user

**Pros:**
- Good Jira integration
- Bitbucket Pipelines
- Free for small teams

**Cons:**
- Smallest community
- Limited free CI/CD (50 min/month)
- Less portfolio visibility

**Free Tier:** Unlimited repos, 50 Pipeline minutes/month

---

### ☕ Gitea (Self-hosted)

**Use if:**
- ✅ Want full control & privacy
- ✅ Learning DevOps
- ✅ Have a server or VPS
- ✅ Don't trust big tech

**Pros:**
- **Full control** over your code
- **Privacy** (your server, your data)
- **Free** (just server costs)
- Lightweight & fast
- GitHub Actions compatible
- No vendor lock-in

**Cons:**
- You maintain the server
- No built-in community
- Requires some DevOps knowledge

**Cost:** Free software + ~$5-20/month VPS (DigitalOcean, Linode, Hetzner)

---

### 🌐 Multi-platform

**Use if:**
- ✅ GitHub for OSS + portfolio
- ✅ GitLab for personal projects
- ✅ Work uses something else
- ✅ Want flexibility

**Setup:**
- Separate SSH keys per platform
- Git conditional includes (auto-switch email)
- Organized project directories

---

## 💸 Free Tier Recommendations

### Deployment

| Service | Best For | Free Tier |
|---------|----------|----------|
| **Vercel** | React, Next.js, frontend | Unlimited (Hobby plan) |
| **Netlify** | Static sites, Jamstack | 100 GB bandwidth/month |
| **Render** | Full-stack, backend | Free (750 hours/month) |
| **Railway** | Quick deploys, databases | $5 credit/month |
| **Fly.io** | Global apps, Docker | 3 VMs free |

### Backend/Database

| Service | What You Get | Free Tier |
|---------|--------------|----------|
| **Supabase** | PostgreSQL + Auth + Storage | 500 MB DB, 1 GB storage |
| **Firebase** | Firestore + Auth + Hosting | Spark plan |
| **PlanetScale** | MySQL with branches | 5 GB storage |
| **Neon** | Serverless PostgreSQL | 3 GB storage |

### Learning (All FREE!)

- **freeCodeCamp** - Complete web dev curriculum
- **The Odin Project** - Full-stack path
- **MDN Web Docs** - Web technology reference
- **roadmap.sh** - Developer roadmaps
- **Exercism** - Coding practice

---

## 👥 For Students

### GitHub Education Pack

**Get FREE access to:**
- GitHub Pro (normally $4/month)
- Copilot (normally $10/month)
- DigitalOcean credits ($200)
- Heroku credits
- Name.com domain
- And 80+ other tools!

**Sign up:** https://education.github.com

---

## 🔧 Multi-Platform SSH Setup

If using multiple platforms:

```bash
# Generate separate keys
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "you@github"
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_gitlab -C "you@gitlab"

# Configure SSH (~/.ssh/config)
cat >> ~/.ssh/config << EOF
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github

Host gitlab.com
  HostName gitlab.com
  User git
  IdentityFile ~/.ssh/id_ed25519_gitlab
EOF

# Add keys to platforms
pbcopy < ~/.ssh/id_ed25519_github.pub  # Add to GitHub
pbcopy < ~/.ssh/id_ed25519_gitlab.pub  # Add to GitLab
```

---

## 📋 Project Structure Suggestion

```bash
~/Projects/
├── personal/          # Personal side projects
│   ├── blog/
│   ├── portfolio/
│   └── cool-app/
│
├── freelance/         # Client work
│   ├── client-a/
│   └── client-b/
│
├── open-source/       # OSS contributions
│   ├── react/
│   ├── fastapi/
│   └── my-oss-project/
│
├── learning/          # Tutorials, courses
│   ├── fcc-projects/
│   ├── odin-project/
│   └── udemy-course/
│
└── experiments/       # POCs, spikes
    ├── new-tech-test/
    └── random-idea/
```

---

## 🚀 Next Steps After Install

### 1. Build Your Portfolio

**On GitHub:**
- Create awesome README for profile
- Pin your best projects
- Contribute to open source
- Use GitHub Pages for portfolio site

### 2. Set Up CI/CD

**GitHub Actions:**
```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm run build
      - run: npm run deploy
```

**GitLab CI:**
```yaml
# .gitlab-ci.yml
deploy:
  script:
    - npm run build
    - npm run deploy
```

### 3. Join Communities

- 📝 **Dev.to** - Write & share
- 🔴 **Reddit** - r/webdev, r/learnprogramming
- 💬 **Discord** - The Odin Project, freeCodeCamp
- 🐦 **Twitter** - Follow #100DaysOfCode, #BuildInPublic

### 4. Start Building!

**Project Ideas:**
- 📝 Personal blog (Next.js + MDX)
- 💼 Portfolio site (React + Tailwind)
- ⚖️ Todo app (learning CRUD)
- 📊 Analytics dashboard (practice data viz)
- 🤖 Discord bot (learn APIs)
- 🏪 E-commerce site (full-stack practice)

---

## ❓ FAQ

### Q: I'm a complete beginner. Where do I start?

**A:** 
1. Choose **GitHub** (best for beginners)
2. Complete **freeCodeCamp** Responsive Web Design
3. Follow **The Odin Project** Foundations
4. Build small projects & push to GitHub
5. Join **Dev.to** and share your journey!

### Q: Should I use GitHub or GitLab?

**A:** 
- **GitHub** if: Building portfolio, job hunting, OSS
- **GitLab** if: Want better CI/CD, considering self-hosting
- **Both** if: Use GitHub for portfolio + GitLab for personal projects

### Q: How much does this cost?

**A:** **$0/month** using free tiers!

**Optional costs:**
- Domain: ~$12/year (Namecheap)
- VPS for Gitea: ~$5-20/month (optional)
- Paid courses: Your choice (but tons of free options!)

### Q: What about corporate work?

**A:** This package is for **personal projects only**.

For work:
- Use company's config package
- Or use walmart-config/acme-corp-config as templates

### Q: Can I contribute to this package?

**A:** Yes! It's maintained by the community.

---

## 🆘 Support

**Communities:**
- 📝 Dev.to - https://dev.to
- 🔴 r/learnprogramming - https://reddit.com/r/learnprogramming
- 💬 The Odin Project Discord - https://discord.gg/fbFCkYabZB
- ❓ Stack Overflow - https://stackoverflow.com

**Package Issues:**
- GitHub: https://github.com/prism/personal-config/issues

---

## 🐶 Contributing

Want to improve this package? PRs welcome!

**Ideas:**
- Add more platform profiles (Codeberg, SourceHut)
- More free tier resources
- Better beginner guidance
- Localization (non-English)

---

**Built by indie developers, for indie developers ❤️**

**Start building your dreams - no corporate approval needed! 🚀**
