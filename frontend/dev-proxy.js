// Minimal local proxy for Nemo frontend
// - Proxies localhost requests to deployed Cloud Functions
// - Injects Identity Token via gcloud for private endpoints
// - Adds permissive CORS so the static page can call it

// Requirements: Node 18+, gcloud installed and authenticated
// Usage:
//   node frontend/dev-proxy.js
// Then open frontend/index.html in a browser

import http from 'node:http';
import { spawnSync } from 'node:child_process';

const PROJECT_ID = process.env.PROJECT_ID || 'day-planner-london-mvp';
const REGION = process.env.REGION || 'asia-east2';
const HEALTH_URL = process.env.HEALTH_URL || `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/nemo-health`;
const QUERY_URL = process.env.QUERY_URL || `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/nemo-query`;
const INGEST_URL = process.env.INGEST_URL || `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/nemo-ingest`;

function getIdToken() {
  const res = spawnSync('gcloud', ['auth', 'print-identity-token'], { encoding: 'utf8' });
  if (res.status !== 0) {
    console.error('Failed to get identity token:', res.stderr);
    return null;
  }
  return res.stdout.trim();
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Ingest-Token');
}

function proxy({ targetUrl, req, res, injectAuth = true }) {
  const idToken = injectAuth ? getIdToken() : null;
  const url = new URL(targetUrl);

  const chunks = [];
  req.on('data', (d) => chunks.push(d));
  req.on('end', async () => {
    try {
      const body = chunks.length ? Buffer.concat(chunks) : undefined;
      const resp = await fetch(url, {
        method: req.method,
        headers: {
          'Content-Type': req.headers['content-type'] || 'application/json',
          ...(injectAuth && idToken ? { Authorization: `Bearer ${idToken}` } : {}),
          ...(req.headers['x-ingest-token'] ? { 'X-Ingest-Token': req.headers['x-ingest-token'] } : {}),
        },
        body: body && ['POST','PUT','PATCH'].includes(req.method) ? body : undefined,
      });

      const text = await resp.text();
      setCors(res);
      res.statusCode = resp.status;
      res.setHeader('Content-Type', resp.headers.get('content-type') || 'application/json');
      res.end(text);
    } catch (e) {
      setCors(res);
      res.statusCode = 502;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ error: true, message: String(e) }));
    }
  });
}

// Health proxy on 8080
http.createServer((req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
  if (req.url === '/' || req.url === '/health') {
    return proxy({ targetUrl: HEALTH_URL, req, res });
  }
  res.statusCode = 404; res.end('Not Found');
}).listen(8080, () => console.log('Health proxy: http://localhost:8080'));

// Query proxy on 8081 (supports local stub mode)
http.createServer((req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }

  // Optional stub mode for offline UI testing
  if (process.env.LOCAL_STUB === 'true' && req.method === 'POST') {
    const chunks = [];
    req.on('data', (d) => chunks.push(d));
    req.on('end', () => {
      try {
        const body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString('utf8')) : {};
        const now = Date.now();
        const stub = {
          mode: 'vertex_rag',
          answer_zh: `${body.province?.toUpperCase() || 'GD'}省${body.asset === 'solar' ? '光伏' : body.asset === 'wind' ? '风电' : '煤电'}并网验收一般需要：1）项目核准或备案文件；2）设备试运行报告；3）并网调试记录；4）安全生产管理制度等。具体以当地电网公司发布的办事指南为准。`,
          citations: [
            {
              title: '广东省分布式光伏并网管理办法（示例）',
              url: 'https://gd.gov.cn/example.pdf',
              effective_date: '2024-06-01'
            },
            {
              title: '南方电网并网业务指南（示例）',
              url: 'https://www.csg.cn/example.html'
            }
          ],
          trace_id: `stub-${now}`,
          elapsed_ms: 1234
        };
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify(stub));
      } catch (e) {
        res.statusCode = 500;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({ error: true, message: String(e) }));
      }
    });
    return;
  }

  // Frontend posts to base; map to query function
  return proxy({ targetUrl: QUERY_URL, req, res });
}).listen(8081, () => console.log('Query proxy:  http://localhost:8081'));

// Ingest proxy on 8082 (manual use)
http.createServer((req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
  return proxy({ targetUrl: INGEST_URL, req, res });
}).listen(8082, () => console.log('Ingest proxy: http://localhost:8082'));
