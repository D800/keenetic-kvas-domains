#!/usr/bin/env python3
"""Merge upstream-only domains into category files."""

import re
from pathlib import Path

# Domains to skip — suspicious, unclear, or low-value
SKIP = {
    "circlecrewpinkcrowd.com",
    "digash.live",
    "atv4.dnskp.cc",
    "delivery.2d.net.co",
    "insearch.site",
    "pvpessence.com",
    "etahub.com",
    "magaz.global",
    "supersliv.biz",
    "ukdevilz.com",
    "slifki.biz",
    "flisland.net",
    "diabrowser.com",
    "miracleptr.wordpress.com",  # random blog
}

# domain -> category mapping
MAPPING = {
    "social": [
        "whatsapp.com", "whatsapp.net", "whatsapp.biz", "wa.me",
        "twin.me", "twinme.com", "twinlife-systems.com",
        "truthsocial.com",
        "patreonusercontent.com",
    ],
    "video": [
        "disneyplus.com", "hbomax.com", "max.com",
        "fxnetworks.com", "le-production.tv",
        "vod-fy.crunchyrollcdn.com",
        "gql.twitch.tv", "usher.ttvnw.net",
        "v.vrv.co",
        "coldfilm.city", "coldfilm.ink",
        "hdrezka.app", "hdrezka.tech", "hdrezka.tv", "hdrzk.org", "hdstudio.org",
        "rezka.cc", "rezka.fi", "rezka.land", "rezka.tv", "rezka-ua.in",
        "filmix.fan",
        "lostfilm.download", "lostfilm.tw", "lostfilm.uno",
        "kinozaltv.life",
        "anilib.me", "anilibria.org", "anilibria.wtf",
        "myanimelist.net",
        "radiojar.com", "sndcdn.com", "soundcloud.cloud",
        "x-minus.pro",
        "thetvdb.com", "tvdevinfo.com",
        "musixmatch.com", "musicbrainz.org",
        "yt.be", "yt3.googleusercontent.com",
    ],
    "ai": [
        "augmentcode.com", "windsurf.com", "trae.ai",
        "data.cline.bot", "genspark.ai",
        "kilo.ai", "kilocode.ai",
        "deepl.com", "langdock.com",
        "hume.ai", "sonara.ai",
        "chub.ai",
        "production-openaicom-storage.azureedge.net",
        "dreamina.capcut.com",
    ],
    "dev": [
        "sentry.dev", "posthog.com",
        "youtrack.cloud", "toolbox.app",
        "git.new", "code.gist.build",
        "connect.ngrok-agent.com",
        "modrinth.com",
        "codelinaro.org",
        "primevue.org", "scrollrevealjs.org",
        "openh264.org",
        "dub.sh", "urlr.me",
        "snapgene.com",
        "devexpress.com",
        "document360.com", "document360.io",
        "editorx.com", "uizard.io",
        "octopus.do",
        "make.com",
        "profitwell.com", "paritydeals.com",
        "paddle.com", "paddlestatus.com",
    ],
    "news": [
        "themoscowtimes.com",
        "espreso.tv", "liga.net", "ukrainer.net", "ukrinform.net",
        "zaxid.net", "novyny.live", "dailylviv.com",
        "glavred.info", "glavred.net", "mezha.net", "rima.media", "dumka.media",
        "iditelesombase.org",
        "usatoday.com", "spiegel.de",
        "sotaproject.com",
        "lu4.org",
    ],
    "torrents": [
        "mega.nz", "cloudtorrents.com", "bt4gprx.com",
        "audiobookbay.lu",
        "lib.rus.ec",
    ],
    "gaming": [
        "gamestop.com", "g2a.com", "eneba.com",
        "wbgames.com",
        "haydaygame.com", "marvelsnap.com", "seconddinnertech.com", "snapgametech.com",
        "deckbrew.xyz",
        "mw2.wiki",
    ],
    "adult": [
        "e-hentai.org", "fansly.com", "manyvids.com", "hitomi.la",
        "nude-moon.org", "nhentai.net",
        "eporner.com", "freeones.com", "theporndude.com",
        "realbooru.com", "yande.re",
        "xhcdn.com", "xnxx-ru.com",
        "rule34.us",
    ],
    "vpn-privacy": [
        "tiptop-vpn.com", "lantern.io", "croxyproxy.com",
        "startmail.com", "riseup.net",
        "nordaccount.com", "nordcdn.com",
        "scryde.io", "scryde.net", "scryde.ru", "scryde.world", "ruscryde.net",
        "scryde1.net", "scryde2.net", "scryde3.net", "scryde4.net", "scryde5.net",
        "scryde6.net", "scryde7.net", "scryde8.net", "scryde9.net",
        "scryde10.net", "scryde11.net", "scryde12.net",
        "sms-activate.io", "grizzlysms.com",
        "mailerlite.com", "mailinator.com",
    ],
    "shopping": [
        "ikea.com", "klarna.com", "wise.com", "transferwise.com",
        "indeed.com", "primark.com", "housebrand.com", "lyst.com",
        "dyson.com", "techbargains.com",
        "penguin.com", "penguinrandomhouse.com",
        "manybooks.net",
        "swapd.co",
    ],
    "crypto": [
        "quicknode.com",
        "exchanger.bits.media",
    ],
    "cloud-infra": [
        "parallels.com", "parallels.net", "parallels.cn", "parallelsaccess.com", "myparallels.com",
        "sophos.com", "cisecurity.org", "hybrid-analysis.com", "tria.ge",
        "support.anydesk.com",
        "siteground.com",
        "hc-ping.com", "hchk.io",
        "spiceworks.com", "semrush.com",
        "speedtest.net", "fast.com",
        "netacad.com", "netapp.com",
        "new.abb.com",
        "lgeapi.com", "lgthinq.com",
        "expandrive.com",
        "myqrcode.com",
        "notion-emojis.s3-us-west-2.amazonaws.com",
    ],
    "linux": [
        "arduino.cc", "bufferbloat.net",
        "xiaomi.eu",
    ],
    "hardware-electronics": [
        "bosch.com", "boschaftermarket.com", "boschautoparts.com",
        "home.by.me",
        "yeggi.com",
    ],
    "tools-services": [
        "apkmirror.com",
        "easydmarc.com",
        "legalshield.com",
        "mintmobile.com",
    ],
    "forums-books": [
        "4pda.ws",
        "pixabay.com", "unsplash.com", "imgur.com", "gifyu.com",
        "lingq.com",
    ],
    "ua-media": [
        "censor.net",
        "jw.org", "jw-russia.org",
    ],
    "media-db": [
        "metopera.org",
    ],
    "misc": [
        "a-vrv.akamaized.net",
        "affinity.studio",
        "aircanada.com", "akc.org", "all3dp.com", "amplitude.com", "andrevi.ch",
        "ansys.com", "any.do", "app.zerossl.com", "arc.net",
        "chesscomfiles.com",
        "clevelandclinic.org",
        "flyertalk.com",
        "monolisa.dev",
        "nippon.com", "kaleido.ai",
        "pronouns.page",
        "qwant.com",
        "restream.io",
        "tiktokv.eu",
        "webmd.com",
    ],
}


def main():
    cats_dir = Path(__file__).parent.parent / "domains" / "categories"

    # Verify all upstream domains are accounted for
    all_mapped = set()
    for domains in MAPPING.values():
        all_mapped.update(domains)
    all_mapped.update(SKIP)

    total_added = 0
    for cat, new_domains in sorted(MAPPING.items()):
        cat_file = cats_dir / f"{cat}.txt"
        existing = set()
        lines = []
        if cat_file.exists():
            lines = cat_file.read_text().splitlines()
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    existing.add(stripped)

        to_add = sorted(set(new_domains) - existing)
        if not to_add:
            continue

        with open(cat_file, "a") as f:
            for d in to_add:
                f.write(f"{d}\n")

        total_added += len(to_add)
        print(f"  {cat}: +{len(to_add)} ({', '.join(to_add[:5])}{'...' if len(to_add) > 5 else ''})")

    print(f"\nTotal added: {total_added}")
    print(f"Skipped (suspicious): {len(SKIP)}")
    print(f"Skipped domains: {', '.join(sorted(SKIP))}")


if __name__ == "__main__":
    main()
