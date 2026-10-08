"""
PWA Helper Module for Marathi Quiz Application
Handles Progressive Web App (PWA) manifest serving, MIME type normalization,
service worker registration with Service-Worker-Allowed header,
and DOM metadata injection for mobile browser installability (Add to Home Screen / Install App).
"""

import os
import gc
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# --- 1. Patch Streamlit AppStaticFileHandler to support .json, .js, .webmanifest with correct MIME types ---
try:
    import streamlit.web.server.app_static_file_handler as _ash

    _EXTENSIONS_LIST = list(_ash.SAFE_APP_STATIC_FILE_EXTENSIONS)
    for ext in ['.json', '.webmanifest', '.js', '.css', '.svg', '.ico', '.woff', '.woff2', '.ttf']:
        if ext not in _EXTENSIONS_LIST:
            _EXTENSIONS_LIST.append(ext)
    _ash.SAFE_APP_STATIC_FILE_EXTENSIONS = tuple(_EXTENSIONS_LIST)

    def _pwa_set_extra_headers(self, path: str) -> None:
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix in ['.json', '.webmanifest']:
            self.set_header("Content-Type", "application/manifest+json; charset=utf-8")
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Cache-Control", "no-cache")
        elif suffix == '.js':
            self.set_header("Content-Type", "application/javascript; charset=utf-8")
            self.set_header("Service-Worker-Allowed", "/")
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Cache-Control", "no-cache")
        elif suffix not in _ash.SAFE_APP_STATIC_FILE_EXTENSIONS:
            self.set_header("Content-Type", "text/plain")
        self.set_header("X-Content-Type-Options", "nosniff")

    _ash.AppStaticFileHandler.set_extra_headers = _pwa_set_extra_headers
except Exception as _e:
    pass


# --- 2. Dynamic Tornado Route Injector (for root /manifest.json and /sw.js) ---
_TORNADO_ROUTES_INITIALIZED = False


def _setup_tornado_routes():
    """Dynamically attaches /manifest.json and /sw.js to Streamlit's running Tornado application."""
    global _TORNADO_ROUTES_INITIALIZED
    if _TORNADO_ROUTES_INITIALIZED:
        return

    try:
        import tornado.web
        import tornado.routing

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(base_dir, "static")
        manifest_file = os.path.join(static_dir, "manifest.json")
        sw_file = os.path.join(static_dir, "sw.js")

        class ManifestRequestHandler(tornado.web.RequestHandler):
            def get(self):
                self.set_header("Content-Type", "application/manifest+json; charset=utf-8")
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Cache-Control", "no-cache")
                if os.path.exists(manifest_file):
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        self.write(f.read())
                else:
                    self.set_status(404)
                    self.write({"error": "manifest.json not found"})

        class ServiceWorkerRequestHandler(tornado.web.RequestHandler):
            def get(self):
                self.set_header("Content-Type", "application/javascript; charset=utf-8")
                self.set_header("Service-Worker-Allowed", "/")
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Cache-Control", "no-cache")
                if os.path.exists(sw_file):
                    with open(sw_file, "r", encoding="utf-8") as f:
                        self.write(f.read())
                else:
                    self.set_status(404)
                    self.write("// sw.js not found")

        # Scan active gc objects for Tornado Application instance
        for obj in gc.get_objects():
            if isinstance(obj, tornado.web.Application):
                if hasattr(obj, "default_router") and hasattr(obj.default_router, "rules"):
                    for rule in obj.default_router.rules:
                        if hasattr(rule.target, "rules"):
                            # Prepend handlers so they match before the default static handler
                            rule.target.rules.insert(
                                0,
                                tornado.routing.Rule(
                                    tornado.routing.PathMatches(r"/manifest\.json"),
                                    ManifestRequestHandler
                                )
                            )
                            rule.target.rules.insert(
                                0,
                                tornado.routing.Rule(
                                    tornado.routing.PathMatches(r"/sw\.js"),
                                    ServiceWorkerRequestHandler
                                )
                            )
                            rule.target.rules.insert(
                                0,
                                tornado.routing.Rule(
                                    tornado.routing.PathMatches(r"/service-worker\.js"),
                                    ServiceWorkerRequestHandler
                                )
                            )
                            _TORNADO_ROUTES_INITIALIZED = True
                            break
                    if _TORNADO_ROUTES_INITIALIZED:
                        break
    except Exception as e:
        pass


# --- 3. HTML / JavaScript PWA Injector ---
PWA_INJECTION_JS = """
<script>
(function() {
    try {
        const parentDoc = window.parent.document;
        const parentHead = parentDoc.head;
        const parentWindow = window.parent;

        // 1. Set Parent Document Title
        parentDoc.title = "मराठी प्रश्नमंजुषा - इयत्ता ४ थी";

        // 2. Helper to set or create meta tag
        function setMeta(name, content, isProperty) {
            const attr = isProperty ? 'property' : 'name';
            let tag = parentHead.querySelector(`meta[${attr}="${name}"]`);
            if (!tag) {
                tag = parentDoc.createElement('meta');
                tag.setAttribute(attr, name);
                parentHead.appendChild(tag);
            }
            tag.setAttribute('content', content);
        }

        // 3. Helper to set or create link tag
        function setLink(rel, href, type, sizes) {
            let selector = `link[rel="${rel}"]`;
            if (sizes) selector += `[sizes="${sizes}"]`;
            let link = parentHead.querySelector(selector);
            if (!link) {
                link = parentDoc.createElement('link');
                link.setAttribute('rel', rel);
                parentHead.appendChild(link);
            }
            link.setAttribute('href', href);
            if (type) link.setAttribute('type', type);
            if (sizes) link.setAttribute('sizes', sizes);
        }

        // 4. Inject PWA Metadata
        setMeta('theme-color', '#0B1020');
        setMeta('mobile-web-app-capable', 'yes');
        setMeta('apple-mobile-web-app-capable', 'yes');
        setMeta('apple-mobile-web-app-status-bar-style', 'black-translucent');
        setMeta('apple-mobile-web-app-title', 'मराठी प्रश्नमंजुषा');
        setMeta('application-name', 'मराठी प्रश्नमंजुषा');
        setMeta('description', 'इयत्ता ४ थी शिष्यवृत्ती परीक्षा सराव मराठी प्रश्नमंजुषा');

        // 5. Inject Manifest Link
        setLink('manifest', '/app/static/manifest.json', 'application/manifest+json');

        // 6. Inject App Icons
        setLink('icon', '/app/static/icons/icon-192.png', 'image/png', '192x192');
        setLink('icon', '/app/static/icons/icon-512.png', 'image/png', '512x512');
        setLink('apple-touch-icon', '/app/static/icons/icon-192.png', 'image/png', '192x192');
        setLink('apple-touch-icon', '/app/static/icons/icon-512.png', 'image/png', '512x512');
        setLink('shortcut icon', '/app/static/icons/favicon.png', 'image/png');

        // 7. Register Service Worker on Top-Level Window
        if ('serviceWorker' in parentWindow.navigator) {
            parentWindow.navigator.serviceWorker.register('/sw.js', { scope: '/' })
                .then(function(reg) {
                    console.log('✅ PWA: Service Worker registered at root scope:', reg.scope);
                })
                .catch(function(err) {
                    console.log('ℹ️ PWA: Root scope SW register fallback to /app/static/sw.js:', err.message);
                    parentWindow.navigator.serviceWorker.register('/app/static/sw.js', { scope: '/app/static/' })
                        .then(function(regStatic) {
                            console.log('✅ PWA: Service Worker registered at /app/static/ scope:', regStatic.scope);
                        })
                        .catch(function(err2) {
                            console.warn('⚠️ PWA Service Worker registration error:', err2);
                        });
                });
        }

        // 8. Capture PWA beforeinstallprompt event
        if (!parentWindow._pwaPromptListenerAttached) {
            parentWindow._pwaPromptListenerAttached = true;
            parentWindow.addEventListener('beforeinstallprompt', (e) => {
                parentWindow.deferredPwaPrompt = e;
                console.log('🎉 PWA: beforeinstallprompt captured! Android Chrome can install the app.');
            });

            parentWindow.addEventListener('appinstalled', () => {
                console.log('🎉 PWA: मराठी प्रश्नमंजुषा app was successfully installed!');
                parentWindow.deferredPwaPrompt = null;
            });
        }
    } catch (err) {
        console.warn('PWA Head injection error:', err);
    }
})();
</script>
"""


def inject_pwa():
    """
    Main entrypoint called in app.py to configure and inject PWA capabilities.
    Sets up Tornado routes and injects manifest, icons, metadata, and service worker.
    """
    # 1. Initialize Tornado direct routes
    _setup_tornado_routes()

    # 2. Inject PWA HTML/JS into top-level document
    components.html(PWA_INJECTION_JS, height=0, width=0)
