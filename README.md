# FamilyShield Adult Domain Blocker

**Linux Mint / Ubuntu / Debian (1-Command Install)** — Copy and paste into your terminal:
```bash
curl -sL "[https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz](https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz)" | tar -xz && sudo ./familyshield --install-auto-update
```

**Windows 10 / 11 (1-Command Install)** — Open **PowerShell** and copy/paste:
```powershell
irm "[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/familyshield.ps1](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/familyshield.ps1)" | iex
```

**Manual Update Command** (optional, after installing):
* **Linux:**
```bash
sudo familyshield --force
```
* **Windows (PowerShell):**
```powershell
& "$env:ProgramData\FamilyShield\familyshield.ps1" -Force
```

**Switch Blocking Modes (Adult-Only vs. Adult + Social Media & Video Sites):**
* **Linux:**
```bash
sudo familyshield --with-social
sudo familyshield --remove-social
```
* **Windows (PowerShell):**
```powershell
& "$env:ProgramData\FamilyShield\familyshield.ps1" -WithSocial
& "$env:ProgramData\FamilyShield\familyshield.ps1" -RemoveSocial
```

**Android Blocklist URLs** (for RethinkDNS, Blokada, AdAway):
* **Adult Content Blocklist:**
```text
[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt)
```
* **Social Media & Video Blocklist (Optional):**
```text
[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/social_host_names.txt](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/social_host_names.txt)
```

Blocks 520,000+ adult websites, mirror domains, and directory aggregators in `/etc/hosts` (Linux) and `C:\Windows\System32\drivers\etc\hosts` (Windows), locks down browser DNS-over-HTTPS (DoH) bypasses via system policies and the Windows Registry, and checks this repository weekly for updates.

### Love the Lord your God with all your heart, mind and soul. Let's go and sin no more.
