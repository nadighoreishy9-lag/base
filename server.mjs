// Minimal static dev server for the Elementor template preview.
// Serves the repo on port 3000 and exposes /__version (newest file mtime)
// so the page can reload itself when a file changes.
import { createServer } from "node:http";
import { readFile, readdir, stat } from "node:fs/promises";
import { extname, join, resolve, sep } from "node:path";

const ROOT = resolve(process.cwd());
const PORT = Number(process.env.PORT ?? 3000);
const HOST = process.env.HOST ?? "0.0.0.0";
const SKIP = new Set([".git", "node_modules"]);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
};

async function newestMtime(dir) {
  let newest = 0;
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (SKIP.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) newest = Math.max(newest, await newestMtime(full));
    else newest = Math.max(newest, (await stat(full)).mtimeMs);
  }
  return newest;
}

function send(res, status, body, type) {
  res.writeHead(status, { "content-type": type, "cache-control": "no-store" });
  res.end(body);
}

createServer(async (req, res) => {
  const pathname = decodeURIComponent(new URL(req.url ?? "/", "http://localhost").pathname);

  if (pathname === "/__version") {
    return send(res, 200, JSON.stringify({ version: await newestMtime(ROOT) }), TYPES[".json"]);
  }

  const target = resolve(ROOT, "." + (pathname.endsWith("/") ? `${pathname}index.html` : pathname));
  if (target !== ROOT && !target.startsWith(ROOT + sep)) {
    return send(res, 403, "Forbidden", "text/plain; charset=utf-8");
  }

  try {
    const body = await readFile(target);
    return send(res, 200, body, TYPES[extname(target).toLowerCase()] ?? "application/octet-stream");
  } catch {
    return send(res, 404, "Not found", "text/plain; charset=utf-8");
  }
}).listen(PORT, HOST, () => {
  console.log(`Nadia template preview running on http://${HOST}:${PORT}`);
});
