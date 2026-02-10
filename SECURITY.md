# Security Checklist

Mitigations for common vulnerabilities in the Nginx / Gunicorn / Django stack.

## Django Application Layer

| Vulnerability | Mitigation |
|--------------|------------|
| **SQL Injection** | Django ORM only; no raw queries. Model constraints enforce types. |
| **XSS** | Django auto-escapes templates. No `mark_safe` or unsafe user output. |
| **CSRF** | `CsrfViewMiddleware` enabled. `CSRF_TRUSTED_ORIGINS` for prod. Token in forms and AJAX. |
| **IDOR** | No object references exposed to unauthenticated users. Admin requires auth. |
| **Security Misconfiguration** | `DEBUG=0` default; `SECRET_KEY` required when not DEBUG. `check --deploy` before release. |
| **Broken Authentication** | Strong password validators (min 12 chars). HttpOnly, Secure, SameSite cookies. Session not in URL. |
| **Insecure File Uploads** | No file upload in this app. |
| **Dependency Vulnerabilities** | Run `safety check`. Keep Django and deps updated. |

## Gunicorn

| Vulnerability | Mitigation |
|--------------|------------|
| **Worker Exhaustion & DoS** | `timeout=30`, `graceful_timeout=30`, `max_requests=1000` with jitter. |
| **Information Leakage** | No `proxy_protocol`; `forwarded_allow_ips="127.0.0.1"` to restrict X-Forwarded-* spoofing. |
| **Debug Info** | `loglevel=info`; no debug handlers. |
| **Privilege Escalation** | Run as `User=la0app` in systemd, never root. |
| **Insecure Binding** | Bind to `unix:/run/la0/gunicorn.sock` only. Nginx is the public-facing proxy. |

## Nginx

| Vulnerability | Mitigation |
|--------------|------------|
| **Missing Security Headers** | X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy. HSTS when HTTPS. |
| **Misconfigured SSL/TLS** | Use certbot. Recommended: TLSv1.2/1.3 only; strong ciphers (see la0-nginx.conf comments). |
| **Path Traversal** | Fixed `alias` paths; `autoindex off` for static. No user-controlled paths. Unknown paths return 404. |
| **HTTP DoS** | `client_max_body_size 4M`, `client_body_buffer_size 16k`. Optional: `limit_req_zone` + `limit_req` (see deploy/). |
| **Billion Laughs** | Body size limits. No XML processing in app. |
| **Information Leak** | Add `server_tokens off;` in http block. |

## General

| Vulnerability | Mitigation |
|--------------|------------|
| **Incorrect Permissions** | Code: 644 files, 755 dirs. DB/logs: 640 or 600. Run app as dedicated user. |
| **Exposed Admin** | Admin at `/admin/` requires Django auth. Consider IP allowlist in Nginx for extra hardening. |
| **Insecure Communication** | HTTPS only in prod. `DJANGO_USE_HTTPS=1` enables HSTS and secure cookies. |
| **Logging** | `django.security`, `django.request` loggers. Admin rate-limit events logged. |

## Rate Limiting

- **API** `/api/order/`: 5 requests/minute per IP (django-ratelimit).
- **Admin login** `/admin/login/`: 10 attempts per 15 minutes per IP (middleware).
- **Nginx** (optional): 10 req/s per IP with burst 20 when zone included.
