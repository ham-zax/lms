# Hosting the FMGE mock

Everything a new session needs to operate, update or debug the published FMGE mock.

| What | URL |
| --- | --- |
| Mock (share this) | https://fmge.hamza.my.id/lms/fmge/mock |
| Frappe desk | https://fmge.hamza.my.id/app |
| LMS home | https://fmge.hamza.my.id/lms |

The live site runs **only** on an Oracle Cloud VM. The WSL bench on the dev PC is for development and is not published.

## At a glance

| Item | Value |
| --- | --- |
| VM | Oracle free tier (E2.1.Micro): 2 small vCPU, ~950 MB RAM, 4 GB swap, 48 GB disk, Ubuntu 26.04 x86_64 |
| SSH | `ssh -i ~/.ssh/id_relay ubuntu@140.238.225.111` (key on the dev PC) |
| Bench | `/home/ubuntu/frappe-bench` (apps `frappe`, `payments`, `lms`) |
| Site | `fmge.localhost` (name kept from the dev bench; `host_name` = `https://fmge.hamza.my.id`) |
| Tunnel | `fmge-oci`, id `473e7a3e-1afe-4518-9672-5f088e210987`, config `/etc/cloudflared/config.yml` on the VM |
| DNS | `fmge.hamza.my.id`: proxied CNAME to the `fmge-oci` tunnel |
| Admin password | `~/.config/fmge-admin-password.txt` on the dev PC (mode 600). The file is one labelled line; the password is the text after `: ` |
| Code | `lms` = https://github.com/ham-zax/lms (branch `main`), `frappe` and `payments` = upstream `develop` |

The VM used to run the SuperLive token relay (`~/repo/sl-relay`). The relay was removed on 2026-09-28; a full backup of its files and systemd units is in `~/repo/sl-relay/server-backup-2026-09-28/` on the dev PC. `sl-relay/deploy.sh` still points at this VM, so **don't run it**: it would reinstall the relay next to Frappe on a 1 GB machine.

## How a request reaches the mock

```
browser ── https://fmge.hamza.my.id ──> Cloudflare edge
        ── tunnel fmge-oci (outbound from the VM; no inbound ports) ──> cloudflared
        ── http://127.0.0.1:8080 ──> nginx      /assets → sites/assets, /files → site public files
        ── http://127.0.0.1:8000 ──> gunicorn   X-Frappe-Site-Name: fmge.localhost
```

## What runs on the VM

All are systemd units, enabled at boot. A reboot was tested on 2026-09-28: the site came back without manual steps, about 20 s after SSH returned.

| Unit | Details |
| --- | --- |
| `fmge-web` | gunicorn, 2 workers × 4 threads (gthread), `--preload frappe.app:application`, cwd `~/frappe-bench/sites` |
| `nginx` | `/etc/nginx/sites-available/fmge`, listens on `127.0.0.1:8080` only, 1 worker process |
| `mariadb` | port 3306, localhost only; low-memory tuning in `/etc/mysql/mariadb.conf.d/99-frappe.cnf` (96 MB buffer pool, utf8mb4) |
| `fmge-redis-cache` | port 13000, `~/frappe-bench/config/redis_cache.conf` (48 MB LRU, no persistence) |
| `fmge-redis-queue` | port 11000, `~/frappe-bench/config/redis_queue.conf` |
| `cloudflared` | installed with `cloudflared service install`, credentials in `/etc/cloudflared/<tunnel-id>.json` |

These do not run on the VM: the stock `redis-server` (disabled), the Frappe background worker, the scheduler, socketio and the file watcher. The mock doesn't need them, and RAM is tight. Idle memory is about 600 MB used plus about 150 MB of swap.

Typical latency through Cloudflare: 0.2–0.4 s for a page and about 0.6–1 s for the quiz API. The first request after a restart takes about 3 s.

## Common commands (on the VM)

```sh
ssh -i ~/.ssh/id_relay ubuntu@140.238.225.111

systemctl status fmge-web nginx mariadb fmge-redis-cache fmge-redis-queue cloudflared
journalctl -u fmge-web -f            # app log
sudo tail -f /var/log/nginx/error.log
free -h                              # watch RAM/swap

# bench commands (the bench CLI is not installed; this is what `bench` runs)
cd ~/frappe-bench/sites
F="$HOME/frappe-bench/env/bin/python -m frappe.utils.bench_helper frappe --site fmge.localhost"
$F migrate
$F clear-cache
$F execute lms.fmge.importer.install_psm_block_1
$F backup --with-files               # -> sites/fmge.localhost/private/backups/
sudo systemctl restart fmge-web      # after any Python change
```

Use an absolute path to `env/bin/python`. A relative `../env` works but prints `sys.prefix` warnings.

## Updating the published mock

The VM is too small to build the frontend, and packages must not be re-resolved there (see the gotchas below). The workflow is: change and build on the dev PC, push, then pull or copy onto the VM.

- **Python / backend changes**: commit and push to `ham-zax/lms` from `~/repo/AVO/exam-question-preparation`. Then on the VM:
  ```sh
  git -C ~/frappe-bench/apps/lms pull origin main
  sudo systemctl restart fmge-web
  ```
  Run `$F migrate` too if doctypes or patches changed.
- **Question bank changes**: edit the Markdown source, run `scripts/fmge/build_question_bank.py`, and commit and push the output. Pull on the VM as above, then `$F execute lms.fmge.importer.install_psm_block_1`.
- **Frontend changes**: build on the dev PC (see "Frontend build gotcha"). The build output is git-ignored, so copy it up:
  ```sh
  cd ~/repo/AVO/exam-question-preparation
  tar czf /tmp/lmsbuild.tgz lms/public/frontend lms/www/_lms.html
  scp -i ~/.ssh/id_relay /tmp/lmsbuild.tgz ubuntu@140.238.225.111:/tmp/
  ssh -i ~/.ssh/id_relay ubuntu@140.238.225.111 \
    'rm -rf ~/frappe-bench/apps/lms/lms/public/frontend && tar xzf /tmp/lmsbuild.tgz -C ~/frappe-bench/apps/lms && sudo systemctl restart fmge-web'
  ```
- **Upgrading frappe / payments**: do it on the dev bench first. Then `pip freeze` the dev env (excluding editable installs) into `~/frappe-bench/requirements.lock` on the VM, run `uv pip install -r requirements.lock` into `~/frappe-bench/env`, check out the same commits on the VM, copy `apps/frappe/frappe/public/dist` (built assets, git-ignored) and `sites/assets/{css,js,locale,assets.json,assets-rtl.json}`, run `$F migrate`, and restart `fmge-web`.

Data (questions, users) lives only in the VM database. The dev bench database is a snapshot from 2026-09-28 and is not synced either way.

## Gotchas

- **Never run the LMS test suite against a real site**, locally or on the VM. The upstream `lms/lms/doctype/lms_quiz/test_lms_quiz.py` tearDown deletes every `LMS Question`. `allow_tests` is false on the VM site. If questions vanish, re-run the importer.
- **Dependency conflict**: frappe `develop` pins `beautifulsoup4>=4.15,<4.16`, while lms pins `>=4.12,<4.14`. A fresh `pip/uv install -e` of all three apps fails to resolve. The VM env was built from the dev env's `pip freeze` (`~/frappe-bench/requirements.lock`, bs4 4.13.5) plus `uv pip install --no-deps -e apps/*`. `uv` is at `~/.local/bin/uv` on the VM.
- **Frontend build gotcha (dev PC)**: `apps/lms` on the dev bench is a symlink to `~/repo/AVO/exam-question-preparation`, so `yarn build` / `bench build` fail to resolve `../../../../sites/common_site_config.json`, and the default Node heap runs out because frappe-ui enables sourcemaps. What worked: a temporary wrapper vite config that aliases that import and sets `build.sourcemap=false`, with `NODE_OPTIONS=--max-old-space-size=4096`, then copying `lms/public/frontend/index.html` to `lms/www/_lms.html`. A failed build empties `lms/public/frontend`, so don't copy it to the VM until the build has succeeded.
- **Error pages**: Cloudflare **530** means the tunnel is down (VM off, or `cloudflared` stopped). **502** means nginx is up but gunicorn isn't: it's still starting (about 20 s after boot) or crashed (`journalctl -u fmge-web`).
- **Memory**: if the site gets sluggish, check `free -h`. Swap use is expected; sustained heavy swapping means too many workers or a runaway job. Don't add a worker, scheduler or socketio without checking RAM first.

## Security notes

- The whole site is reachable, including `/login` and the Frappe desk. The Administrator password is not the default (see above).
- The mock needs no account. Its endpoints (`lms.fmge.public_quiz`) are rate limited and never create users or submissions.
- The notes PDF is public at `/assets/lms/fmge/day2-psm-notes.pdf`, because practice feedback links to pages in it.
- The VM firewall (iptables) only allows SSH inbound. The old relay port 5000 rules were removed; Frappe, nginx, MariaDB and Redis all bind to 127.0.0.1.

## The dev PC (WSL) bench

Location: `~/repo/AVO/frappe-bench`. `apps/lms` is a symlink to `~/repo/AVO/exam-question-preparation`. Site `fmge.localhost`, bench-private MariaDB on port 3307 (datadir `frappe-bench/local-mariadb/data`), Redis on 13000/11000 (`frappe-bench/config/redis_*.conf`).

Nothing starts automatically. It was stopped on 2026-09-28, with no systemd units, cron or shell-rc hooks. To use it for development, start the pieces by hand (for example in `tmux -L wsl-agent` sessions):

```sh
cd ~/repo/AVO/frappe-bench
mariadbd --no-defaults --datadir=$PWD/local-mariadb/data --socket=$PWD/local-mariadb/run/mariadb.sock \
  --pid-file=$PWD/local-mariadb/run/mariadb.pid --port=3307 --bind-address=127.0.0.1 \
  --skip-networking=0 --log-error=$PWD/local-mariadb/log/mariadb.log
redis-server config/redis_cache.conf
redis-server config/redis_queue.conf
./serve-fmge.sh        # frappe serve on 127.0.0.1:8000 in a restart loop
```

To stop MariaDB cleanly: `mariadb-admin --socket=~/repo/AVO/frappe-bench/local-mariadb/run/mariadb.sock -u root shutdown`. When killing the dev web server, match `^../env/bin/python -m frappe.utils.bench_helper`. Never `pkill -f` a pattern that also appears in your own shell command.

The system `mariadb` and `redis-server` packages (ports 3306/6379) were installed on the dev PC during the Frappe setup, but the bench doesn't use them.

## History

- Until 2026-09-28 the site ran on the WSL dev bench and was published through the `satori-mcp` tunnel (`~/.cloudflared/config.yml` on the dev PC). That tunnel also serves `mcp.hamza.my.id`, which is important and must stay up. The fmge rule was removed from that config; backups are `config.yml.bak-2026-09-28` and `config.yml.bak-2026-09-28-pre-oci`. If you ever touch that tunnel: `cloudflared tunnel ingress validate`, then kill only the `cloudflared tunnel run` process (the webharness watchdog restarts it within about 20 s), then check `~/repo/webharness/bin/status` for `public health: ok` and `issues: 0`. Don't restart the `mcp-dev-bridge` service.
- 2026-09-28: moved to the Oracle VM. The database was restored from a dev-bench backup (50 LMS Questions verified on both), and apps were checked out at the dev commits (frappe `864bd0c`, payments `86fefa9`, lms `637d9f2`).
