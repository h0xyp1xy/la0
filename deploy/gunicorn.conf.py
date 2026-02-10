# Gunicorn config for la0 Django app (run behind nginx as la0app)
# Copy to project: cp ... deploy/gunicorn.conf.py (or run with -c from project root)
# IMPORTANT: Run via systemd as User=la0app (not root). Bind to unix socket only.
import os

bind = "unix:/run/la0/gunicorn.sock"
workers = 2
threads = 2
worker_class = "sync"
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# DoS mitigation: limit request time so stuck requests don't exhaust workers
timeout = 30
graceful_timeout = 30
keepalive = 2

# Do NOT use proxy_protocol unless you have a trusted upstream (nginx) that sends it
# Do NOT bind to 0.0.0.0:port on a public interface — use nginx as reverse proxy
forwarded_allow_ips = "127.0.0.1"  # Restrict X-Forwarded-* to localhost/nginx only

# So nginx (www-data) can connect to the socket
umask = 0o007

# Logging (no debug stack traces in production)
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = False

# Run from backend dir
chdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
wsgi_app = "config.wsgi:application"
