const API_HOST = "api.themoviedb.org";
const IMAGE_HOST = "image.tmdb.org";

export default {
  async fetch(request) {
    const origin = request.headers.get("Origin") || "*";
    const cors = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Vary": "Origin"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: cors });
    }

    const incoming = new URL(request.url);
    let upstream;
    if (incoming.pathname.startsWith("/api/3/")) {
      upstream = new URL("https://" + API_HOST + incoming.pathname.slice(4) + incoming.search);
    } else if (incoming.pathname.startsWith("/image/t/p/")) {
      upstream = new URL("https://" + IMAGE_HOST + incoming.pathname.slice(6) + incoming.search);
    } else {
      return new Response("Not found", { status: 404, headers: cors });
    }

    const response = await fetch(upstream.toString(), {
      method: request.method,
      headers: {
        "Accept": request.headers.get("Accept") || "*/*",
        "User-Agent": "ARNIX-HTV/1.0"
      },
      cf: { cacheEverything: incoming.pathname.startsWith("/image/"), cacheTtl: 86400 }
    });
    const headers = new Headers(response.headers);
    for (const [key, value] of Object.entries(cors)) headers.set(key, value);
    headers.delete("Set-Cookie");
    if (incoming.pathname.startsWith("/api/")) {
      headers.set("Cache-Control", "no-store");
    }
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  }
};
