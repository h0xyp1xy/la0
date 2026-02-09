# Gunicorn config for la0 Django app (run behind nginx as la0app)
# Copy to project: cp ... deploy/gunicorn.conf.py (or run with -c from project root)
import os

bind = "unix:/run/la0/gunicorn.sock"
workers = 2
threads = 2
worker_class = "sync"
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# So nginx (www-data) can connect to the socket
umask = 0o007

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Run from backend dir
chdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
wsgi_app = "config.wsgi:application"
