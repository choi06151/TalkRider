#!/usr/bin/env node
/* 토크라이더 프로토타입 서버 — 같은 Wi-Fi의 휴대폰이 엽서 QR을 찍어 이미지를 받을 수 있게 한다.
   실행:  node prototype/serve.js        (포트 바꾸기:  PORT=8080 node prototype/serve.js)
   PC 브라우저에서 터미널에 찍힌 주소로 열면, QR 화면의 QR이 그 주소(PC의 Wi-Fi IP)로 자동 생성된다. */
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const ROOT = __dirname, PORT = Number(process.env.PORT) || 5173;
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.ico': 'image/x-icon' };

function lanAddresses() {
  const out = [];
  for (const list of Object.values(os.networkInterfaces())) for (const a of list || []) if (a.family === 'IPv4' && !a.internal) out.push(a.address);
  /* 사설망(192.168 / 10 / 172.16~31)을 먼저 */
  return out.sort((x, y) => (/^(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))/.test(y) ? 1 : 0) - (/^(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))/.test(x) ? 1 : 0));
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/lan.json') {
    const ip = lanAddresses()[0];
    res.writeHead(200, { 'Content-Type': TYPES['.json'], 'Cache-Control': 'no-store' });
    return res.end(JSON.stringify({ base: ip ? `http://${ip}:${PORT}/` : null }));
  }
  let rel = decodeURIComponent(url.pathname); if (rel === '/') rel = '/CAR_PLAYGROUND_prototype.html';
  const file = path.normalize(path.join(ROOT, rel));
  if (!file.startsWith(ROOT + path.sep)) { res.writeHead(403); return res.end('forbidden'); }
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); return res.end('없는 파일이에요'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': st.size, 'Cache-Control': 'no-cache' });
    fs.createReadStream(file).pipe(res);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  const ips = lanAddresses();
  console.log('\n토크라이더 프로토타입 서버');
  console.log(`  이 PC:      http://localhost:${PORT}/`);
  ips.forEach(ip => console.log(`  같은 Wi-Fi: http://${ip}:${PORT}/`));
  if (!ips.length) console.log('  Wi-Fi 주소를 찾지 못했어요. 네트워크 연결을 확인하세요.');
  console.log('\n휴대폰과 PC를 같은 Wi-Fi에 연결하고, 여행 엽서 → QR로 받기 화면의 QR을 찍으세요.');
  console.log('(Windows 방화벽 창이 뜨면 "개인 네트워크" 허용을 눌러 주세요)\n');
});
