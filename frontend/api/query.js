async function callCloudFunction(bodyText) {
  const PROJECT_ID = process.env.PROJECT_ID || 'day-planner-london-mvp';
  const REGION = process.env.GCF_REGION || process.env.REGION || 'asia-east2';
  let TARGET = process.env.QUERY_URL || `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/nemo-query`;
  if (!/^https?:\/\//i.test(TARGET)) {
    TARGET = `https://${TARGET}`;
  }
  const resp = await fetch(TARGET, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: bodyText
  });
  const text = await resp.text();
  return { status: resp.status, text, contentType: resp.headers.get('content-type') || 'application/json' };
}

async function callPerplexity(body, res) {
  try {
    const apiKey = process.env.PERPLEXITY_API_KEY;
    if (!apiKey) throw new Error('Perplexity key not configured');
    const topic = inferTopic(body.question || '', body.asset || '', body.doc_class || '');
    const allowlist = buildAllowlist(body.province || '', topic);
    const siteFilters = allowlist.filter(d=>!d.startsWith('.')).map(d=>`site:${d}`).join(' ');
    const suffixFilters = allowlist.filter(d=>d.startsWith('.')).join(' ');
    const hints = topicHints(body.question || '', body.asset || '', topic);
    const system = 'You are a Chinese compliance assistant. First provide a 1–3 sentence plain-language summary, then a concise step-by-step answer with exact required documents and agencies. Cite 3–6 highly relevant official sources. If unsure, say so.';
    const user = `问题：${body.question}\n\n范围与限制：\n- 省份：${body.province}\n- 主题：${body.asset} 领域相关流程/规定\n- 限制来源：优先 *.gov.cn 及本主题对应部委/省级对口网站。\n- 仅返回与问题直接相关、可指导办理的法规/指南/流程/要件清单。\n- 回答语言：${(body.lang||'zh-CN').toLowerCase().startsWith('zh')?'中文':'English'}。\n\n搜索提示（供你内部使用）：${siteFilters} ${suffixFilters} ${hints}`;
    const payload = {
      model: process.env.PERPLEXITY_MODEL || 'sonar-pro',
      messages: [ { role: 'system', content: system }, { role: 'user', content: user } ],
      return_citations: true
    };
    const p = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST', headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!p.ok) throw new Error(`Perplexity ${p.status}`);
    const data = await p.json();
    const content = (data.choices?.[0]?.message?.content || '').trim();
    const urlsInText = extractUrls(content);
    // Combine Perplexity citations and any urls found in the answer text
    let merged = [...(data.citations || []), ...urlsInText].filter(Boolean);
    // Filter to allowlist
    merged = merged.filter(u => isAllowed(u, allowlist));
    // Deduplicate preserving order
    const seen = new Set();
    const filtered = [];
    for (const u of merged) { if (!seen.has(u)) { seen.add(u); filtered.push(u); } }
    const citations = filtered.slice(0, 6).map(u => ({ title: u, url: u }));
    const zh = (body.lang||'zh-CN').toLowerCase().startsWith('zh');
    const traceId = `perq-${Math.random().toString(16).slice(2,10)}`;
    let respBody;
    if (content) {
      respBody = zh ? { answer_zh: content, citations, trace_id: traceId, mode: 'perplexity_qa' }
                    : { answer: content, citations, trace_id: traceId, mode: 'perplexity_qa' };
    } else if (citations.length) {
      // Provide link-only message when content empty but sources exist
      const msg = zh ? '为您找到相关来源文档：' : 'Found related source documents:';
      respBody = zh ? { answer_zh: msg, citations, trace_id: traceId, mode: 'perplexity_links' }
                    : { answer: msg, citations, trace_id: traceId, mode: 'perplexity_links' };
    } else {
      const err = zh ? '未找到直接相关的一手来源。' : 'No directly relevant primary sources found.';
      respBody = { error: true, message: err, trace_id: traceId };
      return res.status(404).json(respBody);
    }
    res.status(200).json(respBody);
  } catch (e) {
    res.status(502).json({ error: true, message: String(e) });
  }
}

function inferTopic(q, asset, docClass) {
  q = (q||'').toLowerCase(); const a=(asset||'').toLowerCase();
  if (q.includes('rail')||q.includes('铁路')||q.includes('托运')||q.includes('货运')||q.includes('运价')) return 'rail_freight';
  if (q.includes('测量')||q.includes('测绘')||q.includes('survey')||q.includes('土地')||q.includes('用地')||q.includes('选址')||q.includes('国土')||q.includes('规划')||q.includes('农田')||q.includes('红线')||q.includes('环评')||q.includes('eia')) return 'land_survey';
  if (q.includes('并网')||q.includes('接入')||q.includes('接网')||q.includes('grid')||q.includes('connection')||docClass==='grid') return 'grid_connection';
  if (['solar','wind'].includes(a)) return 'renewables';
  return 'general';
}

function buildAllowlist(province, topic){
  let allow = ['.gov.cn','ndrc.gov.cn','nea.gov.cn','mnr.gov.cn','mee.gov.cn','mohurd.gov.cn'];
  if (topic==='rail_freight') allow.push('mot.gov.cn','nra.gov.cn','95306.cn','12306.cn','china-railway.com.cn');
  if (topic==='grid_connection'||topic==='renewables') allow.push('gdwenergy.gov.cn');
  if (province==='gd') allow.push('gd.gov.cn','td.gd.gov.cn','nr.gd.gov.cn','economy.gd.gov.cn','drc.gd.gov.cn');
  return Array.from(new Set(allow));
}

function topicHints(question, asset, topic){
  const hints=[]; const q=(question||'');
  if (topic==='rail_freight') hints.push('铁路货物运输规则','铁路货物运价规则','铁路托运 办理流程','零担 整车 货物 托运 铁路','铁路货运 运单 要求','site:nra.gov.cn','site:mot.gov.cn');
  if (topic==='land_survey') hints.push('建设用地 预审 选址 意见','用地 规划 许可 办理 流程','地形 测绘 勘测 定界 流程','国土 空间 规划 一张图','永久 基本 农田 占用 论证','生态 保护 红线 评估','环境 影响 评价 报告 备案','site:mnr.gov.cn','site:mee.gov.cn','site:mohurd.gov.cn');
  if ((asset||'').toLowerCase()==='solar' || q.includes('光伏')) hints.push('光伏 电站 选址 用地 要求','光伏 项目 国土 空间 规划');
  if (topic==='grid_connection') hints.push('分布式 光伏 并网 办事 指南','接网 申请 流程','配网 接入 评审');
  return hints.join(' ');
}

function extractUrls(text){
  if (!text) return [];
  const re = /(https?:\/\/[^\s)\]\>"']+)/g;
  const out = []; let m;
  while ((m = re.exec(text)) !== null) out.push(m[1]);
  return out;
}

function isAllowed(url, allowlist){
  try {
    const u = new URL(url);
    const d = u.hostname.toLowerCase();
    for (const a of allowlist){
      if (a.startsWith('.')) { if (d.endsWith(a)) return true; }
      else { if (d === a || d.endsWith('.'+a)) return true; }
    }
    return false;
  } catch { return false; }
}

module.exports = async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Ingest-Token');
  res.setHeader('Access-Control-Max-Age', '3600');
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  try {
    const bodyText = typeof req.body === 'string' ? req.body : JSON.stringify(req.body || {});
    // Try Cloud Function first (if set to public). Fallback to Perplexity if 401/403 or not configured.
    const cf = await callCloudFunction(bodyText).catch(() => null);
    if (cf && cf.status >= 200 && cf.status < 300) {
      res.status(cf.status);
      res.setHeader('Content-Type', cf.contentType);
      return res.end(cf.text);
    }
    if (cf && (cf.status === 401 || cf.status === 403)) {
      // fallback to perplexity
      return await callPerplexity(JSON.parse(bodyText || '{}'), res);
    }
    // If Cloud Function unreachable or other error, fallback too
    return await callPerplexity(JSON.parse(bodyText || '{}'), res);
  } catch (e) {
    res.status(502);
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: true, message: String(e) }));
  }
}
