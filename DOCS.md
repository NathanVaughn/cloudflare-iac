# Docs

This goes over my Cloudflare account configuration.

## lksg.me

Old Linkspring domain name. This repo redirects all traffic to <https://links.nathanv.me>
and blocks any emails being sent. The following subdomains used to be used:

- `lksg.me`
- `www.lksg.me`
- `cdn.lksg.me`
- `status.lksg.me`
- `dev.lksg.me`
- `dev-cdn.lksg.me`

## nathanv.app

My domain name used for self-hosted services in my homelab. DNS is largely managed
automatically by <https://github.com/NathanVaughn/homelab-k8s>.

This repo blocks any emails being sent and redirects HTTP requests for
<https://nathanv.app> to <https://nathanv.me>.

## nathanv.me

My main domain name. This repo blocks any emails being sent.

### Main website

Repository: <https://github.com/NathanVaughn/nathanv.me>

- `nathanv.me`
- `www.nathanv.me`

That repository also contains the following redirects:

- `https://nathanv.me/links/*` -> `https://links.nathanv.me/*`
- `https://nathanv.me/link/*` -> `https://links.nathanv.me/*`
- `https://nathanv.me/blog/*` -> `https://blog.nathanv.me/*`
- `https://nathanv.me/pay/*` -> `https://pay.nathanv.me/*`
- `https://nathanv.me/links` -> `https://links.nathanv.me`
- `https://nathanv.me/blog` -> `https://blog.nathanv.me`
- `https://nathanv.me/pay` -> `https://pay.nathanv.me`

### Blog

Repository: <https://github.com/NathanVaughn/blog.nathanv.me>

- `blog.nathanv.me`
- `www.blog.nathanv.me`

### Links

Repository: <https://github.com/NathanVaughn/links.nathanv.me>

- `links.nathanv.me`
- `www.links.nathanv.me`

### Payments

Repository: <https://github.com/NathanVaughn/pay.nathanv.me>

- `pay.nathanv.me`
- `www.pay.nathanv.me`

### Files

CNAME for `nathanv-public` R2 bucket.

- `files.nathanv.me`

### URL Shortener

CNAME to <https://dub.co>.

- `go.nathanv.me`

### Git Redirect

Redirects `https://git.nathanv.me/*` to `https://github.com/NathanVaughn/*`.

- `git.nathanv.me`

### Kubernetes DNS

Redirects to the git repo <https://github.com/NathanVaughn/k8s-dns>

- `dnsconfigs.nathanv.me`

### Teapot

Fun Cloudflare Worker: <https://github.com/NathanVaughn/nathanv.me-teapot>

- `nathanv.me/teapot`

## nvaughn.email

My domain name used for sending and receiving emails. Allows
for `nath@nvaughn.email` vanity address.

This repo allows emails to be sent with SendGrid, redirects inbound emails to my
GMail address, and redirects HTTP requests for
<https://nvaughn.email> to <https://nathanv.me>.
Also configures MTA-STS from this guide:
<https://developers.cloudflare.com/email-routing/setup/mta-sts/>
