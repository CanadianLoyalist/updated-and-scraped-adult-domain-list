# FamilyShield Adult Domain Blocker
**Linux Mint / Ubuntu / Debian (1-Command Install)** — Copy and paste into your terminal:
```bash
curl -sL [https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz](https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz) | tar -xz && sudo ./familyshield --install-auto-update
```
**Manual Update Command** (optional, after installing):
```bash
sudo familyshield --force
```
**Android Blocklist URL** (for RethinkDNS, Blokada, AdAway):
```text
[https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt](https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt)
```
Blocks 520,000+ adult websites, mirror domains, and directory aggregators in `/etc/hosts`[cite: 5, 7], disables browser DNS-over-HTTPS (DoH) bypasses[cite: 5, 7], and checks this repository weekly for updates[cite: 7].
