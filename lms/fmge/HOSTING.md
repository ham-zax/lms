# Hosting the FMGE mock with Cloudflare Tunnel

The mock runs on a local Frappe bench and is published through an existing Cloudflare Tunnel. No port is opened on the router and no server is rented: `cloudflared` keeps an outbound connection to Cloudflare, and Cloudflare forwards requests for the public hostname down that connection.

| What | URL |
| --- | --- |
| Mock (share this) | https://fmge.hamza.my.id/lms/fmge/mock |
| Frappe desk | https://fmge.hamza.my.id/app |
| LMS home | https://fmge.hamza.my.id/lms |

## How a request reaches the mock

```
browser ── https://fmge.hamza.my.id ──> Cloudflare edge
        ── tunnel (outbound from this PC) ──> cloudflared
        ── http://127.0.0.1:8000, Host: fmge.localhost ──> Frappe (bench serve)
```

Frappe is multi-site and picks the site from the `Host` header. The site on this bench is `fmge.localhost`, so the tunnel rewrites the header instead of the site being renamed or given a second domain.

## Tunnel configuration

The tunnel is a named, locally managed tunnel. Its config is `~/.cloudflared/config.yml`; the credentials file next to it is secret and is not in this repository.

The rule for the mock sits above the catch-all 404 rule:

```yaml
ingress:
  # ...existing rules for other hostnames...
  - hostname: fmge.hamza.my.id
    service: http://127.0.0.1:8000
    originRequest:
      httpHostHeader: fmge.localhost
  - service: http_status:404
```

The DNS record is a proxied CNAME to the tunnel, created once with:

```sh
cloudflared tunnel route dns <tunnel-id> fmge.hamza.my.id
```

## The tunnel is shared with the MCP bridge

The same `cloudflared` process also serves `mcp.hamza.my.id`. It is started by the `mcp-dev-bridge` systemd user service (webharness), whose watchdog restarts `cloudflared` within about 20 seconds if it stops.

To apply a config change without disturbing the rest of that service:

```sh
cloudflared tunnel ingress validate                   # never restart on an invalid config
cloudflared tunnel ingress rule https://fmge.hamza.my.id/
pkill -f '^cloudflared tunnel run'                    # the watchdog starts it again
```

Do not restart `mcp-dev-bridge` itself for a tunnel change: that restarts every MCP provider it runs. After any tunnel change, check the MCP side:

```sh
~/repo/webharness/bin/status   # expect "public health: ok" and "issues: 0"
```

## What must be running

The link only works while this PC is on and all of these are up:

1. the Frappe web server: `bench serve --port 8000` from `frappe-bench` (or `bench start`);
2. MariaDB for the bench;
3. Redis (cache and queue) for the bench;
4. `cloudflared`, via `mcp-dev-bridge`.

`cloudflared` returns a 502 page when the tunnel is up but Frappe is not.

## Security notes

- Publishing the site makes all of it reachable, including `/login` and the Frappe desk. The Administrator password is not the bench default; it is kept outside the repository in `~/.config/fmge-admin-password.txt` (mode 600).
- The mock itself needs no account. Its endpoints (`lms.fmge.public_quiz`) are rate limited and never create users or submissions.
- The notes PDF is public at `/assets/lms/fmge/day2-psm-notes.pdf`, because practice feedback links to pages in it.

## Updating the published mock

- Question bank changes: edit the Markdown source, run `scripts/fmge/build_question_bank.py`, then `bench --site fmge.localhost execute lms.fmge.importer.install_psm_block_1`.
- Python changes: restart the Frappe web server (`bench serve` runs with `--noreload`).
- Frontend changes: rebuild the frontend and copy `lms/public/frontend/index.html` to `lms/www/_lms.html`. Nothing needs to change on the Cloudflare side.

Do not run the LMS test suite against `fmge.localhost`: an upstream quiz test deletes every `LMS Question` on the site it runs on. If questions disappear, re-run the importer above.
