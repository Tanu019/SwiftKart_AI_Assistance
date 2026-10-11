"""
redirect_server.py
------------------
Lightweight redirect server on port 3000 that captures Supabase OAuth / email links
and forwards them seamlessly to the Streamlit app on port 8501 with auth_token.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

HTML_REDIRECT = """<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to SwiftKart AI...</title>
    <script>
        (function() {
            let hash = window.location.hash;
            let search = window.location.search;
            let target = "http://localhost:8501/";

            if (hash && hash.length > 1) {
                let params = new URLSearchParams(hash.substring(1));
                let token = params.get("access_token");
                if (token) {
                    target = "http://localhost:8501/?auth_token=" + encodeURIComponent(token);
                } else {
                    target = "http://localhost:8501/" + search;
                }
            } else if (search && search.length > 1) {
                target = "http://localhost:8501/" + search;
            }
            window.location.replace(target);
        })();
    </script>
</head>
<body style="background:#090F15; color:#FFFFFF; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0;">
    <div style="text-align:center;">
        <h2>Connecting to SwiftKart AI...</h2>
        <p style="color:#94A3B8;">Redirecting to your dashboard at port 8501...</p>
    </div>
</body>
</html>
"""

class RedirectHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_REDIRECT.encode("utf-8"))

    def log_message(self, format, *args):
        # Silent logging
        pass

if __name__ == "__main__":
    port = 3000
    server = HTTPServer(("0.0.0.0", port), RedirectHandler)
    print(f"Redirect server running on http://localhost:{port} -> http://localhost:8501")
    server.serve_forever()
