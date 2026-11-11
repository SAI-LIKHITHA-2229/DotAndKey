from flask import g
from werkzeug.middleware.proxy_fix import ProxyFix


def init_security(app):
    # Behind a reverse proxy (nginx, Render, Railway...) every request seems
    # to come from the proxy. TRUST_PROXY=<number of proxies> makes Flask use
    # the real client IP, which rate limiting depends on. Only set it when a
    # proxy really is in front, otherwise clients could fake their IP.
    proxies = app.config["TRUST_PROXY"]
    if proxies:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxies, x_proto=proxies)

    @app.after_request
    def add_security_headers(response):
        # The API only returns JSON, so it never needs to run scripts,
        # load resources or be shown inside a frame.
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if app.config["APP_ENV"] == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Per-user data (carts, addresses, orders) must not be cached.
        if "user_id" in g:
            response.headers["Cache-Control"] = "no-store"
        return response
