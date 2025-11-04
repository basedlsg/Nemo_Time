module.exports = async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Ingest-Token');
  res.setHeader('Access-Control-Max-Age', '3600');
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  const PROJECT_ID = process.env.PROJECT_ID || 'day-planner-london-mvp';
  const REGION = process.env.GCF_REGION || process.env.REGION || 'asia-east2';
  let TARGET = process.env.HEALTH_URL || `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/nemo-health`;
  if (!/^https?:\/\//i.test(TARGET)) {
    TARGET = `https://${TARGET}`;
  }

  try {
    const resp = await fetch(TARGET, { method: 'GET' });
    if (resp.ok) {
      const text = await resp.text();
      res.status(resp.status);
      res.setHeader('Content-Type', resp.headers.get('content-type') || 'application/json');
      return res.end(text);
    }
    // Fallback degraded response if CF is protected or unavailable
    res.status(200);
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ status: 'degraded', region: 'unknown', commit: 'unknown', error: `health upstream ${resp.status}` }));
  } catch (e) {
    res.status(200);
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ status: 'degraded', error: String(e) }));
  }
}
