FamilyShield Adult & Social Media Domain Blocker

Blocks 520,000+ adult websites, mirror domains, and directory aggregators (plus an optional Social Media & Video Platform Blocker) at the OS level via /etc/hosts (Linux) and C:\Windows\System32\drivers\etc\hosts (Windows). Automatically locks down browser DNS-over-HTTPS (DoH) bypasses via system policies/Windows Registry and checks this repository weekly for updates.

🐧 Linux Mint / Ubuntu / Debian (1-Command Install)

Copy and paste into your terminal:

curl -sL "https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/releases/download/AdultBlocker/familyshield-linux-x64.tar.gz" | tar -xz && sudo ./familyshield --install-auto-update


🪟 Windows 10 / 11 (1-Command Install)

Open PowerShell and copy/paste (automatically requests Administrator privileges):

irm "https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/familyshield.ps1" | iex


🔄 Manual Update & Mode Switching Commands (Optional)

During installation on Linux or Windows, an interactive menu lets you choose between Adult Content Only or Adult Content + Social Media & Video Sites (Meta/Facebook/Instagram/WhatsApp, X/Twitter, TikTok, YouTube, Reddit, Snapchat, Discord, Twitch, Kick, Pinterest, etc.).

You can manually force an update or switch modes at any time:

Linux:

# Interactive Menu / Force Update
sudo familyshield --force

# Direct CLI Mode Switching
sudo familyshield --adult-only
sudo familyshield --with-social
sudo familyshield --remove-social


Windows (PowerShell):

# Interactive Menu / Force Update
& "$env:ProgramData\FamilyShield\familyshield.ps1" -Force

# Direct CLI Mode Switching
& "$env:ProgramData\FamilyShield\familyshield.ps1" -AdultOnly
& "$env:ProgramData\FamilyShield\familyshield.ps1" -WithSocial
& "$env:ProgramData\FamilyShield\familyshield.ps1" -RemoveSocial


📱 Android Blocklist URLs (for RethinkDNS, Blokada, AdAway)

Adult Content Blocklist (520,000+ domains):

https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/host_names.txt


Social Media & Video Platforms Blocklist (Optional add-on):

https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main/social_host_names.txt
