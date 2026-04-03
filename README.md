# keenetic-kvas-domains

Domain lists for [KVAS](https://github.com/qzeleza/kvas) — selective domain routing on Keenetic routers.

## How it works

```
domains/categories/*.txt  ──(GitHub Actions)──>  domains/kvas-aggregated.txt
                                                        │
                                          raw.githubusercontent.com/...
                                                        │
                                               Keenetic cron job
                                                        │
                                                   kvas import
```

1. Domains are organized by category in `domains/categories/`
2. On push, GitHub Actions aggregates all categories into `domains/kvas-aggregated.txt`
3. Keenetic router pulls the aggregated file and imports it via `kvas import`

## Domain categories

| File | Domains | Description |
|------|---------|-------------|
| `social.txt` | Telegram, Discord, Facebook, Twitter/X, Instagram, LinkedIn, messengers |
| `video.txt` | YouTube, Netflix, TikTok, anime, streaming, cinema |
| `ai.txt` | OpenAI, Anthropic, Groq, ElevenLabs, etc. |
| `dev.txt` | JetBrains, GitLab, Grafana, HashiCorp, databases, CI/CD |
| `news.txt` | Independent media, journalism, human rights |
| `torrents.txt` | Torrent trackers, libraries, sci-hub |
| `gaming.txt` | Steam, game platforms, esports |
| `adult.txt` | NSFW |
| `vpn-privacy.txt` | VPN, privacy tools, encrypted email |
| `shopping.txt` | E-commerce, marketplaces |
| `crypto.txt` | Crypto exchanges, DeFi |
| `cloud-infra.txt` | Cloud providers, enterprise IT, SaaS |
| `linux.txt` | Linux distros, package repos |
| `forums-books.txt` | Forums, books, wikis, education |
| `ua-media.txt` | Ukrainian media, regional news |
| `hardware-electronics.txt` | Hardware vendors, electronics |
| `tools-services.txt` | Online tools, SIM services, file hosting |
| `media-db.txt` | TMDB, media databases |
| `misc.txt` | Everything else |

## Adding domains

Add one domain per line to the appropriate category file. Lines starting with `#` are comments.

```bash
echo "example.com" >> domains/categories/social.txt
git commit -am "add example.com to social"
git push  # GitHub Actions builds kvas-aggregated.txt
```

## Router setup

### Auto-update (recommended)

Copy `scripts/kvas-pull-update.sh` to Keenetic and set up cron:

```bash
# On Keenetic via SSH:
scp scripts/kvas-pull-update.sh root@<ROUTER_IP>:/opt/etc/cron.daily/kvas-pull-update.sh
ssh root@<ROUTER_IP> "chmod +x /opt/etc/cron.daily/kvas-pull-update.sh"
```

Or manual crontab for custom schedule:

```bash
# Edit crontab on Keenetic:
crontab -e
# Add (every Sunday at 4:00):
0 4 * * 0 /opt/etc/cron.daily/kvas-pull-update.sh
```

**Important:** Edit `REPO` variable in the script to match your GitHub username/repo.

### Manual import

```bash
curl -sL https://raw.githubusercontent.com/YOUR_USER/keenetic-kvas-domains/main/domains/kvas-aggregated.txt -o /tmp/kvas.txt
kvas import /tmp/kvas.txt
```

## Upstream tracking

The workflow `.github/workflows/upstream-sync.yml` checks [itdoginfo/allow-domains](https://github.com/itdoginfo/allow-domains) weekly for changes. When new domains appear:

1. A GitHub issue is created with the diff
2. New domains **not** in our list are highlighted
3. You decide what to add — nothing is auto-imported

The file `domains/inside-kvas.lst` is a snapshot of the upstream list for diffing.

## KVAS commands reference

```bash
kvas show                   # Current domain list
kvas add example.com        # Add domain
kvas del example.com        # Remove domain
kvas import ./list.txt      # Import from file
kvas export ./backup.txt    # Export to file
kvas test                   # Test all services
kvas update                 # Apply changes
```

## Files

```
domains/
├── categories/            # Thematic domain lists (source of truth)
│   ├── social.txt
│   ├── video.txt
│   ├── ai.txt
│   └── ...
├── kvas-aggregated.txt    # Auto-built by GitHub Actions
├── inside-kvas.lst        # Upstream snapshot (itdoginfo/allow-domains)
└── kvas_list_03_04_26.txt # Original export from KVAS (reference)
scripts/
├── kvas-pull-update.sh    # Cron script for Keenetic routers
├── deploy.sh              # Manual deploy via SSH
└── categorize.py          # One-time categorization helper
```
