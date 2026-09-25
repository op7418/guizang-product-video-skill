import http from 'node:http';
import path from 'node:path';
import {readFile, realpath} from 'node:fs/promises';
const types = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.json': 'application/json', '.wav': 'audio/wav', '.mp3': 'audio/mpeg'};
export async function serve(port = 0) {
  const base = await realpath('dist');
  const server = http.createServer(async (req, res) => {
    try {
      const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      const file = await realpath(path.join(base, name === '/' ? 'index.html' : name));
      if (file !== base && !file.startsWith(base + path.sep)) { res.writeHead(403); res.end(); return; }
      const body = await readFile(file); res.writeHead(200, {'Content-Type': types[path.extname(file)] || 'application/octet-stream'}); res.end(body);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(port, '127.0.0.1', resolve); });
  return {server, url: `http://127.0.0.1:${server.address().port}`};
}
