# FamilyShield - Adult & Social Media Blocker
Blocks **520,000+ adult websites, mirror domains, and directory aggregators** (plus an optional **900+ domain Social Media & Video Blocker**) at the OS level in `/etc/hosts`[cite: 10], locks down browser DNS-over-HTTPS (DoH) bypasses[cite: 10], and automatically checks this repository weekly for updates[cite: 10].

### Linux Mint / Ubuntu / Debian (1-Command Install)
**Option 1: Block Adult Content ONLY (520,000+ adult & mirror domains)** — Copy and paste into your terminal:
```bash
curl -sL "[https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz](https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz)" | tar -xz && sudo ./familyshield --adult-only --install-auto-update
```
**Option 2: Block Adult Content + Social Media & Video Sites** (Meta/Facebook/Instagram/Threads/WhatsApp, X/Twitter, TikTok, YouTube, Reddit, Snapchat, Discord, Twitch, Kick, Pinterest, Tumblr, Telegram, etc.)[cite: 10]:
```bash
curl -sL "[https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz](https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz)" | tar -xz && sudo ./familyshield --with-social --install-auto-update
```
**Switch Modes or Force an Update Anytime After Installing:**
```bash
# Open the interactive [1 / 2 / 3] configuration menu:
sudo familyshield

# Enable Social Media & Video blocking alongside Adult blocking:
sudo familyshield --with-social

# Instantly remove Social Media blocking (keep Adult content blocked):
sudo familyshield --remove-social

# Manually force an update check from GitHub:
sudo familyshield --force
```

### Android Setup (RethinkDNS / Blokada / AdAway)
Paste either (or both) of these raw blocklist URLs into your Android DNS/VPN blocker's custom hosts list:
* **Adult Content Blocklist (Required):**
```text
[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt)
```
* **Social Media & Video Blocklist (Optional):**
```text
[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/social_host_names.txt](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/social_host_names.txt)
```
