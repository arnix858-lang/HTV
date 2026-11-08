# TMDB proxy for ARNIX HTV

This Worker relays only TMDB API and image requests. It does not proxy HDRezka.

## Deploy (free Cloudflare Workers)

1. Sign in at https://dash.cloudflare.com/ and open **Workers & Pages**.
2. Create a Worker named `arnix-htv-tmdb-proxy`.
3. Replace its starter code with `worker.js` from this folder and deploy.
4. Copy the Worker URL, for example `https://arnix-htv-tmdb-proxy.<your-subdomain>.workers.dev`.
5. In GitHub open **arnix858-lang/HTV → Settings → Secrets and variables → Actions → New repository secret**.
6. Create secret `TMDB_PROXY_URL` with that Worker URL (no trailing slash).
7. Run the Android workflow again. The app will route TMDB API calls and poster/backdrop images through the Worker.

If the secret is empty, the app uses the normal TMDB endpoints directly. Keep the Worker URL on HTTPS. Cloudflare may apply its own free-plan limits. This Worker is intentionally restricted to GET/HEAD requests and the two TMDB host/path prefixes; do not turn it into a general-purpose open proxy.
