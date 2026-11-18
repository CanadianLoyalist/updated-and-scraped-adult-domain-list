#!/usr/bin/env python3
"""
FamilyShield Standalone Linux Client (v2 - With Optional Social Media & Video Blocker)
Repository: https://github.com/CanadianLoyalist/updated-and-scraped-adult-domain-list

Features:
  1. Downloads the latest raw_domains.txt and cleaned_domains.txt from GitHub
     (520,000+ adult websites, mirror domains, and directory aggregators).
  2. Interactive 3-option menu (or CLI flags: --adult-only, --with-social, --remove-social)
     allowing the user to block Adult Content Only, or Adult Content + Social Media & Video Sites.
  3. Includes a built-in fallback of 900+ social media/video hostnames (Meta/FB/IG/Threads/WhatsApp,
     X/Twitter/Nitter, TikTok, YouTube/Invidious/Piped, Reddit, Snapchat, Discord, Twitch, Kick,
     Pinterest, Tumblr, Imgur, Bluesky, Mastodon, Telegram, etc.) AND also fetches the latest
     social_media_domains.txt from GitHub if available.
  4. Enforces Browser DNS-over-HTTPS (DoH) Lockdowns for Firefox, Chrome, Brave, Edge, and Chromium
     so browsers cannot bypass /etc/hosts.
  5. Installs itself to /usr/local/bin/familyshield and configures a weekly root cron job
     that remembers the user's chosen mode (Adult-Only vs. Adult + Social Media).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/CanadianLoyalist/updated-and-scraped-adult-domain-list/main"
RAW_DOMAINS_URL = f"{GITHUB_RAW_BASE}/raw_domains.txt"
CLEANED_DOMAINS_URL = f"{GITHUB_RAW_BASE}/cleaned_domains.txt"
SOCIAL_DOMAINS_URL = f"{GITHUB_RAW_BASE}/social_media_domains.txt"

HOSTS_PATH = "/etc/hosts"
INSTALL_BIN_PATH = "/usr/local/bin/familyshield"
STATE_DIR = "/var/lib/familyshield"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
CRON_FILE = "/etc/cron.d/familyshield-autoupdate"

START_MARKER = "# >>> ADULT BLOCKLIST START >>>"
END_MARKER = "# <<< ADULT BLOCKLIST END <<<"

SOCIAL_START_MARKER = "# >>> SOCIAL MEDIA BLOCKLIST START >>>"
SOCIAL_END_MARKER = "# <<< SOCIAL MEDIA BLOCKLIST END <<<"

DOMAIN_REGEX = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)

# Built-in comprehensive Social Media & Video Platform Ecosystems
# (Used immediately and merged with social_media_domains.txt from GitHub if present)
SOCIAL_MEDIA_ECOSYSTEMS = {
    "Meta (Facebook, Instagram, Threads, Messenger, WhatsApp)": [
        "facebook.com", "m.facebook.com", "web.facebook.com", "touch.facebook.com",
        "mbasic.facebook.com", "upload.facebook.com", "graph.facebook.com",
        "connect.facebook.net", "fb.com", "fb.me", "fb.gg", "fb.watch", "fbcdn.net",
        "fbsbx.com", "fbinfra.net", "fbpigeon.com", "facebook-hardware.com",
        "instagram.com", "i.instagram.com", "graph.instagram.com", "cdninstagram.com",
        "ig.me", "instagr.am", "igsonar.com",
        "threads.net", "threads.com",
        "messenger.com", "m.me", "nbabot.net",
        "whatsapp.com", "web.whatsapp.com", "api.whatsapp.com", "chat.whatsapp.com",
        "wa.me", "whatsapp.net",
        "meta.com", "oculus.com", "workplace.com"
    ],
    "X / Twitter (including CDNs, shortlinks & Nitter mirrors)": [
        "x.com", "api.x.com", "mobile.x.com", "pro.x.com",
        "twitter.com", "mobile.twitter.com", "api.twitter.com", "upload.twitter.com",
        "tweetdeck.twitter.com", "ads.twitter.com", "analytics.twitter.com",
        "t.co", "x.co", "twimg.com", "pbs.twimg.com", "video.twimg.com", "abs.twimg.com",
        "twttr.com", "twttr.net", "tweetdeck.com", "periscope.tv", "pscp.tv", "vine.co",
        "nitter.net", "nitter.poast.org", "nitter.privacydev.net", "nitter.cz",
        "nitter.unixfox.eu", "nitter.1d4.us", "nitter.kavin.rocks", "xcancel.com"
    ],
    "TikTok / ByteDance (including CapCut, Lemon8 & regional CDNs)": [
        "tiktok.com", "m.tiktok.com", "vt.tiktok.com", "vm.tiktok.com",
        "ads.tiktok.com", "analytics.tiktok.com", "live.tiktok.com",
        "tiktokv.com", "tiktokcdn.com", "tiktokcdn-us.com", "tiktokcdn-eu.com",
        "tiktokw.us", "ttwstatic.com", "musical.ly", "muscdn.com", "musemuse.cn",
        "byteoversea.com", "ibytedtos.com", "ibyteimg.com", "ipstatp.com",
        "sgsnssdk.com", "snssdk.com", "amemv.com", "toutiao.com", "douyin.com",
        "iesdouyin.com", "lemon8-app.com", "capcut.com"
    ],
    "YouTube & Alternative Frontends (Invidious / Piped)": [
        "youtube.com", "m.youtube.com", "music.youtube.com", "gaming.youtube.com",
        "tv.youtube.com", "kids.youtube.com", "studio.youtube.com", "accounts.youtube.com",
        "youtu.be", "yt.be", "ytimg.com", "i.ytimg.com", "s.ytimg.com",
        "googlevideo.com", "youtube-nocookie.com", "youtubei.googleapis.com",
        "youtubekids.com", "youtubeeducation.com", "withyoutube.com",
        "invidious.io", "yewtu.be", "inv.nadeko.net", "invidious.nerdvpn.de",
        "invidious.flokinet.to", "invidious.privacyredirect.com",
        "piped.video", "pipedapi.kavin.rocks", "piped.kavin.rocks"
    ],
    "Reddit (including old/new subdomains, shortlinks & Redlib/Teddit mirrors)": [
        "reddit.com", "old.reddit.com", "new.reddit.com", "np.reddit.com",
        "sh.reddit.com", "i.reddit.com", "m.reddit.com", "gateway.reddit.com",
        "oauth.reddit.com", "gql.reddit.com",
        "redd.it", "i.redd.it", "v.redd.it", "preview.redd.it", "external-preview.redd.it",
        "redditmedia.com", "redditstatic.com", "redditinc.com", "redditblog.com",
        "teddit.net", "libreddit.it", "redlib.catsarch.com", "redlib.perennialte.ch"
    ],
    "Snapchat": [
        "snapchat.com", "web.snapchat.com", "accounts.snapchat.com", "map.snapchat.com",
        "story.snapchat.com", "spotlight.snapchat.com", "forbusiness.snapchat.com",
        "snap.com", "sc-cdn.net", "sc-gw.com", "sc-jpl.com", "sc-prod.net",
        "sc-static.net", "snap-dev.net", "snapkit.com", "bitmoji.com", "addlive.io"
    ],
    "Discord": [
        "discord.com", "ptb.discord.com", "canary.discord.com", "status.discord.com",
        "support.discord.com", "blog.discord.com",
        "discordapp.com", "cdn.discordapp.com", "media.discordapp.net",
        "images-ext-1.discordapp.net", "images-ext-2.discordapp.net",
        "discordapp.net", "discord.gg", "discord.new", "discord.gift", "discord.gifts",
        "discord.media", "discord.co", "discordcdn.com", "discordstatus.com",
        "hammerandchisel.ssl.fastly.net"
    ],
    "Twitch, Kick & Live Streaming Platforms": [
        "twitch.tv", "m.twitch.tv", "clips.twitch.tv", "player.twitch.tv",
        "dashboard.twitch.tv", "gql.twitch.tv", "passport.twitch.tv",
        "ttvnw.net", "static-cdn.jtvnw.net", "jtvnw.net", "twitchcdn.net",
        "twitchsvc.net", "justin.tv", "ext-twitch.tv",
        "kick.com", "streamlabs.com", "streamelements.com",
        "trovo.live", "dlive.tv", "bigo.tv", "bigolive.tv", "likee.video",
        "younow.com", "afreecatv.com", "sooplive.co.kr", "chzzk.naver.com",
        "nimo.tv", "huya.com", "douyu.com", "twitcasting.tv", "picarto.tv"
    ],
    "Video Hosting & Streaming Sites (Dailymotion, Vimeo, Rumble, Odysee, Bitchute)": [
        "vimeo.com", "player.vimeo.com", "vimeocdn.com", "f.vimeocdn.com", "i.vimeocdn.com",
        "dailymotion.com", "dai.ly", "dmcdn.net", "dmxleo.com",
        "rumble.com", "rmbl.ws", "1a-1791.com",
        "bitchute.com", "old.bitchute.com",
        "odysee.com", "lbry.tv", "librarian.lbry.tv",
        "peertube.tv", "joinpeertube.org", "metacafe.com", "veoh.com",
        "brighteon.com", "banned.video", "rokfin.com", "nebula.tv", "curiositystream.com",
        "floatplane.com", "bilibili.com", "bilibili.tv", "b23.tv", "hdslb.com",
        "nicovideo.jp", "nico.ms", "nimg.jp", "iqiyi.com", "iq.com", "youku.com",
        "tudou.com", "v.qq.com", "wetv.vip", "rutube.ru", "coub.com", "streamable.com",
        "veed.io", "wistia.com", "wistia.net", "jwplayer.com", "jwpcdn.com"
    ],
    "Pinterest, Tumblr, Imgur & Visual Discovery": [
        "pinterest.com", "pin.it", "pinimg.com", "i.pinimg.com", "s.pinimg.com",
        "pinterest.ca", "pinterest.co.uk", "pinterest.de", "pinterest.fr",
        "pinterest.es", "pinterest.it", "pinterest.jp", "pinterest.com.au",
        "pinterest.com.mx", "pinterest.br", "pinterest.ru",
        "tumblr.com", "api.tumblr.com", "assets.tumblr.com", "64.media.tumblr.com",
        "media.tumblr.com", "tmblr.co", "tumblr.co",
        "imgur.com", "i.imgur.com", "m.imgur.com", "s.imgur.com", "imgurinc.com",
        "giphy.com", "media.giphy.com", "i.giphy.com", "gph.is",
        "tenor.com", "media.tenor.com", "c.tenor.com",
        "9gag.com", "img-9gag-fun.9cache.com", "9cache.com",
        "ifunny.co", "imgflip.com", "knowyourmeme.com", "boredpanda.com",
        "flickr.com", "flic.kr", "staticflickr.com", "500px.com", "unsplash.com",
        "deviantart.com", "wixmp.com", "sta.sh", "artstation.com", "behance.net",
        "dribbble.com", "weheartit.com", "vsco.co"
    ],
    "Bluesky, Mastodon, Truth Social, Parler, Gab & Decentralized Social": [
        "bsky.app", "bsky.social", "bsky.network", "plc.directory",
        "mastodon.social", "mastodon.online", "mastodon.world", "mstdn.social",
        "mstdn.jp", "fosstodon.org", "infosec.exchange", "hachyderm.io",
        "joinmastodon.org", "pawoo.net", "baraag.net", "misskey.io",
        "lemmy.world", "lemmy.ml", "beehaw.org", "kbin.social", "pixelfed.social",
        "truthsocial.com", "truthsocial.tv", "tmtgcorp.com",
        "gab.com", "gab.ai", "dissenter.com",
        "gettr.com", "parler.com", "minds.com", "mewe.com", "clouthub.com",
        "poast.org", "nostr.com", "primal.net", "damus.io", "snort.social",
        "iris.to", "farcaster.xyz", "warpcast.com"
    ],
    "LinkedIn, Quora, Medium, Substack & Blogging Platforms": [
        "linkedin.com", "lnkd.in", "licdn.com", "media.licdn.com", "static.licdn.com",
        "slideshare.net",
        "quora.com", "qsf.fs.quoracdn.net", "quoracdn.net", "qr.ae",
        "medium.com", "miro.medium.com", "link.medium.com",
        "substack.com", "substackcdn.com",
        "patreon.com", "patreonusercontent.com",
        "ko-fi.com", "buymeacoffee.com", "gumroad.com",
        "livejournal.com", "wattpad.com", "wattpad.co",
        "archiveofourown.org", "ao3.org", "fanfiction.net",
        "goodreads.com", "letterboxd.com", "rateyourmusic.com", "last.fm"
    ],
    "Telegram, Signal, Line, WeChat, Kakao & Social Messengers": [
        "telegram.org", "web.telegram.org", "core.telegram.org", "desktop.telegram.org",
        "t.me", "telegram.me", "telegram.dog", "telegra.ph", "telesco.pe", "cdn-telegram.org",
        "signal.org", "signal.art", "signal.group", "signal.link", "signal.me",
        "wechat.com", "weixin.qq.com", "web.wechat.com",
        "line.me", "line-apps.com", "line-scdn.net",
        "kakaocorp.com", "kakao.com", "daum.net",
        "viber.com", "kik.com", "skype.com", "join.skype.com", "web.skype.com",
        "guilded.gg", "matrix.org", "element.io", "revolt.chat", "zulip.com",
        "groupme.com", "band.us", "zalo.me", "chat.zalo.me"
    ],
    "Regional & International Social Networks (VK, OK, Weibo, Xiaohongshu, BeReal, Nextdoor)": [
        "vk.com", "m.vk.com", "vk.ru", "vkontakte.ru", "vkuseraudio.net",
        "vkuservideo.net", "vk-cdn.net", "userapi.com",
        "ok.ru", "odnoklassniki.ru", "mycdn.me",
        "weibo.com", "m.weibo.cn", "weibo.cn", "sinaimg.cn", "t.cn",
        "xiaohongshu.com", "xhscdn.com", "xhslink.com",
        "kuaishou.com", "kwai.com",
        "zhihu.com", "zhimg.com",
        "douban.com", "tieba.baidu.com", "qzone.qq.com",
        "bereal.com", "bere.al",
        "clubhouse.com", "joinclubhouse.com",
        "nextdoor.com", "nextdoor.co.uk", "nextdoor.ca",
        "meetup.com", "yikyak.com", "whisper.sh", "ask.fm", "curiouscat.live",
        "tellonym.me", "ngl.link", "sendit.lol", "aminoapps.com",
        "tagged.com", "hi5.com", "myspace.com", "xing.com", "plurk.com",
        "mixi.jp", "ameblo.jp", "hatena.ne.jp", "pixiv.net", "pximg.net",
        "booth.pm", "fanbox.cc", "skeb.jp",
        "4chan.org", "4channel.org", "4cdn.org", "8kun.top"
    ],
    "Dating & Social Meet Apps (Non-Explicit Mainstream)": [
        "tinder.com", "gotinder.com", "tindersparks.com",
        "bumble.com", "badoo.com", "hinge.co", "match.com", "okcupid.com",
        "pof.com", "eharmony.com", "zoosk.com", "coffee-meets-bagel.com",
        "grindr.com", "her.app", "feeld.co", "raya.app", "tantanapp.com"
    ]
}

def clean_domain(domain_str: str) -> str | None:
    domain = domain_str.strip().lower()
    if not domain or domain.startswith("#"):
        return None
    for prefix in ("http://", "https://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.lstrip("/ \t")
    domain = domain.split("/")[0].split("?")[0].split("#")[0].split(":")[0]
    domain = domain.rstrip("!. ,;:")
    if domain.startswith("www."):
        domain = domain[4:]
    if DOMAIN_REGEX.match(domain):
        return domain
    return None

def fetch_url_text(url: str, optional: bool = False) -> str | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "FamilyShield-Linux-Client/2.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        if not optional:
            print(f"[-] Could not fetch {url}: {e}")
    return None

def build_social_hostnames() -> set[str]:
    base_social = set()
    for _, dom_list in SOCIAL_MEDIA_ECOSYSTEMS.items():
        for d in dom_list:
            c = d.strip().lower()
            if c:
                base_social.add(c)

    # Also check if social_media_domains.txt is available on GitHub for dynamic additions
    remote_social = fetch_url_text(SOCIAL_DOMAINS_URL, optional=True)
    if remote_social:
        for line in remote_social.splitlines():
            c = clean_domain(line)
            if c:
                base_social.add(c)

    expanded = set()
    for d in base_social:
        expanded.add(d)
        if not d.startswith("www."):
            expanded.add(f"www.{d}")
        if d.count(".") == 1 and not d.startswith(("m.", "api.", "cdn.", "i.", "v.")):
            expanded.add(f"m.{d}")
    return expanded

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state_data: dict):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)
    except Exception:
        pass

def enforce_browser_doh_lockdown():
    """Locks down DNS-over-HTTPS (DoH) on Firefox, Chrome, Chromium, Brave, and Edge."""
    print("[*] Locking down browser DNS-over-HTTPS (DoH) bypasses...")

    # 1. Firefox policies.json
    ff_dirs = [
        "/etc/firefox/policies",
        "/usr/lib/firefox/distribution",
        "/usr/lib/firefox-esr/distribution",
    ]
    ff_policy = {
        "policies": {
            "DNSOverHTTPS": {
                "Enabled": False,
                "Locked": True
            }
        }
    }
    for d in ff_dirs:
        try:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "policies.json"), "w", encoding="utf-8") as f:
                json.dump(ff_policy, f, indent=2)
        except Exception:
            pass

    # 2. Chromium / Chrome / Brave / Edge managed policies
    chromium_dirs = [
        "/etc/opt/chrome/policies/managed",
        "/etc/chromium/policies/managed",
        "/etc/chromium-browser/policies/managed",
        "/etc/brave/policies/managed",
        "/etc/opt/edge/policies/managed",
    ]
    chromium_policy = {
        "DnsOverHttpsMode": "off",
        "BuiltInDnsClientEnabled": False
    }
    for d in chromium_dirs:
        try:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "familyshield_doh.json"), "w", encoding="utf-8") as f:
                json.dump(chromium_policy, f, indent=2)
        except Exception:
            pass

def replace_or_remove_block(hosts_text: str, start_marker: str, end_marker: str, new_block_lines: list[str] | None) -> str:
    if start_marker in hosts_text and end_marker in hosts_text:
        before = hosts_text.split(start_marker)[0].rstrip()
        after = hosts_text.split(end_marker)[1].lstrip("\r\n")
        if new_block_lines:
            return before + "\n\n" + "".join(new_block_lines) + ("\n" + after if after else "")
        else:
            return before + ("\n" + after if after else "\n")
    else:
        if new_block_lines:
            return hosts_text.rstrip() + "\n\n" + "".join(new_block_lines)
        return hosts_text

def prompt_blocking_mode(cli_args, social_currently_active: bool) -> int:
    """
    Returns:
      1 = Block Adult Content ONLY
      2 = Block Adult Content + Social Media & Video Platforms
      3 = Remove Social Media Block (Keep Adult Content Blocked)
    """
    if cli_args.with_social or cli_args.mode == 2:
        return 2
    if cli_args.remove_social or cli_args.mode == 3:
        return 3
    if cli_args.adult_only or cli_args.mode == 1:
        return 1

    # Non-interactive runs (e.g., weekly background cron update) preserve current setting
    if not sys.stdin.isatty():
        return 2 if social_currently_active else 1

    status_str = "ACTIVE (Social Media is currently BLOCKED)" if social_currently_active else "INACTIVE (Adult-Only mode)"
    print("\n" + "=" * 68)
    print("  FamilyShield Blocklist Configuration Menu")
    print(f"  Current Social Media Block Status: {status_str}")
    print("=" * 68)
    print("  [1] Block Adult Content ONLY (520,000+ adult & mirror domains)")
    print("  [2] Block Adult Content + Social Media & Video Sites")
    print("      (Meta/FB/IG/Threads/WhatsApp, X/Twitter, TikTok, YouTube,")
    print("       Reddit, Snapchat, Discord, Twitch, Kick, Pinterest, etc.)")
    print("  [3] Remove Social Media Block (Keep Adult Content Blocked)")
    print("=" * 68)
    try:
        choice = input("Select an option [1-3] (Press Enter to keep current setting): ").strip()
    except EOFError:
        choice = ""

    if choice == "1":
        return 1
    elif choice == "2":
        return 2
    elif choice == "3":
        return 3
    return 2 if social_currently_active else 1

def install_auto_update(selected_mode: int):
    """Copies executable to /usr/local/bin/familyshield and writes weekly cron job."""
    current_exe = os.path.realpath(sys.executable if getattr(sys, "frozen", False) else __file__)
    try:
        if current_exe != os.path.realpath(INSTALL_BIN_PATH):
            shutil.copy2(current_exe, INSTALL_BIN_PATH)
            os.chmod(INSTALL_BIN_PATH, 0o755)
            print(f"[+] Installed standalone app to {INSTALL_BIN_PATH}")
    except Exception as e:
        print(f"[!] Note: Could not copy binary to {INSTALL_BIN_PATH}: {e}")

    mode_flag = "--with-social" if selected_mode == 2 else "--adult-only"
    cron_content = (
        "# FamilyShield Weekly Auto-Updater (Runs every Sunday at 03:00 AM and on reboot)\n"
        "SHELL=/bin/bash\n"
        "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n"
        f"0 3 * * 0 root {INSTALL_BIN_PATH} {mode_flag} >> /var/log/familyshield.log 2>&1\n"
        f"@reboot root sleep 45 && {INSTALL_BIN_PATH} {mode_flag} >> /var/log/familyshield.log 2>&1\n"
    )
    try:
        with open(CRON_FILE, "w", encoding="utf-8") as f:
            f.write(cron_content)
        os.chmod(CRON_FILE, 0o644)
        print(f"[+] Automatic weekly updates configured in {CRON_FILE} (Mode: {mode_flag})")
    except Exception as e:
        print(f"[-] Failed to write cron file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="FamilyShield Linux Client - Blocks 520,000+ Adult Domains + Optional Social Media & Video Platforms."
    )
    parser.add_argument(
        "--install-auto-update",
        action="store_true",
        help="Install FamilyShield to /usr/local/bin/familyshield and enable weekly automatic GitHub updates."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild /etc/hosts even if GitHub blocklists have not changed."
    )
    parser.add_argument(
        "--mode",
        type=int,
        choices=[1, 2, 3],
        help="1 = Adult Content Only, 2 = Adult + Social Media & Video Sites, 3 = Remove Social Media Block"
    )
    parser.add_argument(
        "--adult-only",
        action="store_true",
        help="Block Adult Content Only (Mode 1)."
    )
    parser.add_argument(
        "--with-social",
        action="store_true",
        help="Block Adult Content + Social Media & Video Sites (Mode 2)."
    )
    parser.add_argument(
        "--remove-social",
        action="store_true",
        help="Instantly remove Social Media Block while keeping Adult Content blocked (Mode 3)."
    )
    args = parser.parse_args()

    if os.geteuid() != 0:
        print("[-] Error: FamilyShield must be run with sudo privileges.")
        print(f"    Run: sudo {sys.argv[0]} --install-auto-update")
        sys.exit(1)

    with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
        hosts_content = f.read()

    social_currently_active = (SOCIAL_START_MARKER in hosts_content and SOCIAL_END_MARKER in hosts_content)
    adult_currently_active = (START_MARKER in hosts_content and END_MARKER in hosts_content)

    mode = prompt_blocking_mode(args, social_currently_active)

    # Fast path: Instantly remove Social Media block if Adult block is already active
    if mode == 3 and adult_currently_active and not args.force:
        print("[*] Removing Social Media & Video blocklist from /etc/hosts...")
        new_hosts = replace_or_remove_block(hosts_content, SOCIAL_START_MARKER, SOCIAL_END_MARKER, None)
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new_hosts)
        state = load_state()
        state["social_mode"] = False
        save_state(state)
        if args.install_auto_update or os.path.exists(CRON_FILE):
            install_auto_update(1)
        subprocess.run(["resolvectl", "flush-caches"], check=False, stderr=subprocess.DEVNULL)
        print("[+] Social Media block removed! Adult Content (520,000+ domains) remains blocked.")
        return

    print("[*] Downloading latest adult domain lists from GitHub...")
    raw_text = fetch_url_text(RAW_DOMAINS_URL)
    cleaned_text = fetch_url_text(CLEANED_DOMAINS_URL)

    if not raw_text and not cleaned_text:
        print("[-] Could not reach GitHub to download domain lists. Please check your internet connection.")
        sys.exit(1)

    social_hostnames = build_social_hostnames() if mode == 2 else set()

    # Compute content hash so background cron updates skip rewriting disk if nothing changed
    combined_hash = hashlib.sha256(
        ((raw_text or "") + (cleaned_text or "") + f"|social={mode == 2}|{len(social_hostnames)}").encode("utf-8")
    ).hexdigest()

    state = load_state()
    desired_social_bool = (mode == 2)
    if (
        not args.force
        and adult_currently_active
        and (social_currently_active == desired_social_bool)
        and state.get("sha256") == combined_hash
    ):
        print("[+] FamilyShield is already up to date with GitHub!")
        if args.install_auto_update:
            install_auto_update(mode)
        return

    # Parse and deduplicate adult domains
    base_domains = set()
    for content in (raw_text, cleaned_text):
        if content:
            for line in content.splitlines():
                d = clean_domain(line)
                if d:
                    base_domains.add(d)

    unique_hostnames = set()
    for d in base_domains:
        unique_hostnames.add(d)
        unique_hostnames.add(f"www.{d}")

    print(f"[*] Loaded {len(base_domains):,} base domains ({len(unique_hostnames):,} total adult hostnames with www).")

    chunk_size = 9
    sorted_adult = sorted(unique_hostnames)
    adult_block_lines = [f"{START_MARKER}\n"]
    for i in range(0, len(sorted_adult), chunk_size):
        chunk = " ".join(sorted_adult[i:i + chunk_size])
        adult_block_lines.append(f"0.0.0.0\t{chunk}\n")
    adult_block_lines.append(f"{END_MARKER}\n")

    new_hosts_content = replace_or_remove_block(hosts_content, START_MARKER, END_MARKER, adult_block_lines)

    if mode == 2:
        print(f"[*] Applying Social Media & Video blocklist ({len(social_hostnames):,} hostnames)...")
        sorted_social = sorted(social_hostnames)
        social_block_lines = [f"{SOCIAL_START_MARKER}\n"]
        for i in range(0, len(sorted_social), chunk_size):
            chunk = " ".join(sorted_social[i:i + chunk_size])
            social_block_lines.append(f"0.0.0.0\t{chunk}\n")
        social_block_lines.append(f"{SOCIAL_END_MARKER}\n")
        new_hosts_content = replace_or_remove_block(new_hosts_content, SOCIAL_START_MARKER, SOCIAL_END_MARKER, social_block_lines)
    else:
        if social_currently_active:
            print("[*] Removing Social Media blocklist (Adult-Only mode selected)...")
        new_hosts_content = replace_or_remove_block(new_hosts_content, SOCIAL_START_MARKER, SOCIAL_END_MARKER, None)

    print(f"[*] Writing blocklist to {HOSTS_PATH}...")
    with open(HOSTS_PATH, "w", encoding="utf-8") as f:
        f.write(new_hosts_content)

    enforce_browser_doh_lockdown()

    if args.install_auto_update or os.path.exists(CRON_FILE):
        install_auto_update(2 if mode == 2 else 1)

    save_state({"sha256": combined_hash, "social_mode": (mode == 2)})
    subprocess.run(["resolvectl", "flush-caches"], check=False, stderr=subprocess.DEVNULL)

    if mode == 2:
        print("[+] FamilyShield Complete! Both ADULT CONTENT (520,000+ sites) and SOCIAL MEDIA / VIDEO sites are now blocked.")
    else:
        print("[+] FamilyShield Complete! ADULT CONTENT (520,000+ sites) is now blocked (Social Media is unblocked).")

if __name__ == "__main__":
    main()
