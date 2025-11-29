from time import perf_counter as time

import pdoc
import pdoc.web

FAVICON = "https://raw.githubusercontent.com/pyxora/pyxora-docs/refs/heads/main/images/favicon.png"

def local(*args, **kwargs):
    """
    Run a web server to preview documentation for all modules except excluded ones.
    """
    x1 = time()
    ip = "localhost"
    port = 8080
    pdoc.render.configure(favicon=FAVICON, docformat="google")
    httpd = pdoc.web.DocServer(
        (ip, port),
        [
            "pyxora",
            "!pyxora.docs",
            "!pyxora.examples",
            "!pyxora.project",
            "!pyxora.templates",
            "!pyxora.editor",
        ],
    )
    x2 = time()
    url = f"http://{ip}:{httpd.server_port}"
    print(f"server ready: {url}")
    print(f"render time: {(x2 - x1) * 1000:.2f} ms")
    print("\nPress Ctrl+C to stop")
    pdoc.web.open_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
