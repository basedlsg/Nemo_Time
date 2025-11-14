"""
Perplexity wrapper for authoritative, citation-backed Q&A
"""

from typing import Dict, Any, List, Optional
import os
import json
import requests
import re


ALLOWLIST_DOMAINS_DEFAULT = [
    ".gov.cn",          # any gov domain
    "ndrc.gov.cn",      # National Development and Reform Commission
    "nea.gov.cn",       # National Energy Administration
    "mnr.gov.cn",       # Ministry of Natural Resources (land/use/survey)
    "mee.gov.cn",       # Ministry of Ecology and Environment (EIA)
    "mohurd.gov.cn",    # Housing/Urban-Rural Development (planning/permitting)
]


def answer_with_perplexity(question: str, province: str, asset: str, *, lang: str = "zh-CN", doc_class: str = None) -> Optional[Dict[str, Any]]:
    """
    Query Perplexity for a precise, sourced answer. Returns dict with
    { answer_zh: str, citations: [{title, url}...] } or None if no useful answer.
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return None

    topic = _infer_topic(question, asset, doc_class)
    allowlist = _build_allowlist(province, topic)
    domain_filter = _build_domain_filter(province, topic)
    # Topic-specific hints
    topic_hints = _topic_hints(question, asset, topic)

    # Formulate a focused search intent prompt
    # Emphasize exact procedural, regulatory, and documentation requirements
    system = (
        "You are a Chinese compliance assistant. Answer ONLY with verified facts from "
        "authoritative Chinese government sources. First provide a 1–3 sentence plain-language summary, "
        "then give a concise, actionable step-by-step answer listing exact required documents, approvals, forms, and responsible agencies. "
        "Cite 3–6 highly relevant official sources that directly support the steps. Do not include unrelated items. "
        "If unsure, state that clearly and ask for clarification."
    )

    # Clean query without site: operators (handled by search_domain_filter parameter)
    user = (
        f"问题：{question}\n\n"
        f"范围与限制：\n"
        f"- 省份：{province}\n- 主题：{asset} 领域相关流程/规定\n"
        f"- 限制来源：优先使用官方政府网站，以及与本主题直接相关的部委/监管机构网站（如 自然资源部/生态环境部/住建部/发改委/能源局/交通运输部/国家铁路局 的官网及省级对口部门）。\n"
        f"- 仅返回与问题直接相关、能指导实际办理的法规/指南/办事流程/技术规范/要件清单。\n"
        f"- 优先2015年及以后仍有效的规范性文件；如为更早文件需注明是否仍然有效。\n"
        f"- 回答语言：{'中文' if (lang or '').lower().startswith('zh') else 'English'}。\n\n"
        f"搜索提示（供你内部使用）：{topic_hints}"
    )

    payload = {
        "model": os.environ.get("PERPLEXITY_MODEL", "sonar-pro"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "search_domain_filter": domain_filter,  # ✅ KEY FIX: Use API parameter instead of query text
        "search_recency_filter": "year",  # Changed from implicit/month to explicit year
        "return_citations": True,
    }

    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=50,
        )
        if resp.status_code >= 400:
            print(f"Perplexity error {resp.status_code}: {resp.text[:200]}")
            return None
        data = resp.json()
        content = (data.get("choices", [{}])[0].get("message", {}) or {}).get("content", "").strip()
        raw_citations: List[str] = data.get("citations") or []

        # Extract any URLs in content as backup
        urls_in_text = _extract_urls(content)
        all_urls = list(dict.fromkeys(raw_citations + urls_in_text))
        # Filter to allowlist domains
        filtered = [u for u in all_urls if _is_allowed(u, allowlist)]
        filtered = _prioritize_relevance(filtered, question, asset, topic)

        # If no clean citations, try a URL-only retrieval pass
        if not filtered:
            urls_only = _perplexity_urls_only(question, province, asset, topic)
            filtered = [u for u in urls_only if _is_allowed(u, allowlist)]
            if not filtered:
                return None

        # Build citations with simple titles (fetching titles is optional and slow)
        citations = [{"title": u, "url": u} for u in filtered[:6]]
        return {"answer_zh": content, "citations": citations}
    except Exception as e:
        print(f"Perplexity call failed: {e}")
        return None


def _extract_urls(text: str) -> List[str]:
    if not text:
        return []
    pat = re.compile(r"https?://[\w\-./%?&#=:+]+", re.IGNORECASE)
    return pat.findall(text)


def _build_allowlist(province: str, topic: str) -> List[str]:
    allow = list(ALLOWLIST_DOMAINS_DEFAULT)
    # Topic-specific additions
    if topic == 'rail_freight':
        allow += ["mot.gov.cn", "nra.gov.cn", "95306.cn", "12306.cn", "china-railway.com.cn"]
    elif topic in ('land_survey', 'permitting', 'siting'):
        allow += ["mnr.gov.cn", "mohurd.gov.cn", "mee.gov.cn"]
    elif topic in ('grid_connection', 'renewables'):
        allow += ["gdwenergy.gov.cn", "ndrc.gov.cn", "nea.gov.cn"]
    # Province-level gov domain
    if province:
        # Generic pattern: *.gd.gov.cn for 广东, *.sd.gov.cn for 山东, *.nmg.gov.cn for 内蒙古
        prov_map = {
            "gd": ["gd.gov.cn"],
            "sd": ["sd.gov.cn"],
            "nm": ["nmg.gov.cn"],
        }
        allow += prov_map.get(province, [])
        # Province department patterns (best-effort)
        if province == 'gd':
            allow += ["td.gd.gov.cn", "nr.gd.gov.cn", "economy.gd.gov.cn", "drc.gd.gov.cn", "gdee.gd.gov.cn"]
    # Include suffix domains (e.g., .gov.cn)
    extra = os.environ.get("PERPLEXITY_ALLOWLIST", "")
    if extra:
        allow += [d.strip() for d in extra.split(",") if d.strip()]
    # Dedup – keep order
    return list(dict.fromkeys(allow))


def _build_domain_filter(province: str, topic: str) -> List[str]:
    """
    Build domain filter list for Perplexity's search_domain_filter parameter.
    This parameter filters search results to only include specified domains.
    Maximum 20 domains supported by Perplexity API.
    """
    # Start with core government domains (without leading dots)
    domains = [
        "gov.cn",           # All Chinese government domains
        "ndrc.gov.cn",      # National Development and Reform Commission
        "nea.gov.cn",       # National Energy Administration
        "mnr.gov.cn",       # Ministry of Natural Resources
        "mee.gov.cn",       # Ministry of Ecology and Environment
        "mohurd.gov.cn",    # Housing and Urban-Rural Development
    ]

    # Add topic-specific domains
    if topic == 'rail_freight':
        domains += ["mot.gov.cn", "nra.gov.cn", "95306.cn", "12306.cn"]
    elif topic in ('land_survey', 'permitting', 'siting'):
        domains += ["mnr.gov.cn", "mohurd.gov.cn", "mee.gov.cn"]
    elif topic in ('grid_connection', 'renewables'):
        domains += ["gdwenergy.gov.cn"]

    # Add province-specific domains
    if province:
        prov_map = {
            "gd": ["gd.gov.cn", "nr.gd.gov.cn", "drc.gd.gov.cn", "td.gd.gov.cn"],
            "sd": ["sd.gov.cn"],
            "nm": ["nmg.gov.cn"],
        }
        domains += prov_map.get(province, [])

    # Deduplicate while preserving order, limit to 20 domains (API max)
    seen = set()
    filtered = []
    for d in domains:
        # Remove leading dots for API compatibility
        clean = d.lstrip('.')
        if clean not in seen:
            seen.add(clean)
            filtered.append(clean)

    return filtered[:20]  # Perplexity API max is 20 domains


def _is_allowed(url: str, allowlist: List[str]) -> bool:
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.lower()
        for d in allowlist:
            if d.startswith("."):
                if domain.endswith(d):
                    return True
            else:
                if domain == d or domain.endswith("." + d):
                    return True
        return False
    except Exception:
        return False


def _topic_hints(question: str, asset: str, topic: str) -> str:
    q = (question or "").lower()
    hints = []
    if topic == 'rail_freight':
        hints += [
            "铁路货物运输规则",
            "铁路货物运价规则",
            "铁路托运 办理流程",
            "零担 整车 货物 托运 铁路",
            "铁路货运 运单 要求",
        ]
        if asset and (asset.lower() == 'coal' or '煤' in question):
            hints += ["煤 炭 铁路 运输 要求", "散装 煤 运输 包装 装载 要求"]
    elif topic in ('land_survey', 'permitting', 'siting'):
        hints += [
            "建设用地 预审 选址 意见",
            "用地 规划 许可 办理 流程",
            "地形 测绘 勘测 定界 流程",
            "国土 空间 规划 一张图",
            "永久 基本 农田 占用 论证",
            "生态 保护 红线 评估",
            "环境 影响 评价 报告 备案",
        ]
        if asset and (asset.lower() == 'solar' or '光伏' in question):
            hints += ["光伏 电站 选址 用地 要求", "光伏 项目 国土 空间 规划"]
    elif topic in ('grid_connection', 'renewables'):
        hints += ["分布式 光伏 并网 办事 指南", "接网 申请 流程", "配网 接入 评审"]
    return " ".join(hints)


def _prioritize_relevance(urls: List[str], question: str, asset: str, topic: str) -> List[str]:
    # Topic-aware preferences
    if topic == 'rail_freight':
        preferred = ["nra.gov.cn", "mot.gov.cn", "95306.cn", "12306.cn", ".gov.cn"]
        bad = ["csrc.gov.cn"]
    elif topic in ('land_survey', 'permitting', 'siting'):
        preferred = ["mnr.gov.cn", "nr.gd.gov.cn", "td.gd.gov.cn", "gd.gov.cn", "mohurd.gov.cn", "mee.gov.cn", ".gov.cn"]
        bad = ["nra.gov.cn", "95306.cn", "12306.cn", "csg.cn"]
    elif topic in ('grid_connection', 'renewables'):
        preferred = ["gdwenergy.gov.cn", "ndrc.gov.cn", "nea.gov.cn", "gd.gov.cn", ".gov.cn"]
        bad = ["csrc.gov.cn"]
    else:
        preferred = ["gd.gov.cn", ".gov.cn", "ndrc.gov.cn", "nea.gov.cn"]
        bad = ["csrc.gov.cn"]
    def score(u: str) -> int:
        s = 0
        for p in preferred:
            if p.startswith("."):
                if u.endswith(p): s += 1
            else:
                if p in u: s += 2
        for b in bad:
            if b in u: s -= 2
        return s
    return sorted(urls, key=score, reverse=True)


def _infer_topic(question: str, asset: str, doc_class: str) -> str:
    q = (question or "").lower()
    a = (asset or "").lower()
    if any(k in q for k in ["rail", "铁路", "托运", "货运", "运价"]):
        return 'rail_freight'
    if any(k in q for k in ["测量", "测绘", "survey", "土地", "用地", "选址", "国土", "规划", "农田", "红线", "环评", "eia", "环境 影响"]):
        return 'land_survey'
    if any(k in q for k in ["并网", "接入", "接网", "grid", "connection"]) or (doc_class == 'grid'):
        return 'grid_connection'
    if a in ('solar', 'wind'):
        return 'renewables'
    return 'general'


def _perplexity_urls_only(question: str, province: str, asset: str, topic: str) -> List[str]:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return []
    domain_filter = _build_domain_filter(province, topic)
    prompt = (
        "只返回与下列主题直接相关的权威来源URL，每行一个，不要任何解释：\n"
        f"问题：{question}\n"
        f"省份：{province}\n主题：{asset}\n"
        "要求：优先官方政府网站以及对应部委/省级对口部门官网页面。最多返回10条。"
    )
    payload = {
        "model": os.environ.get("PERPLEXITY_MODEL", "sonar-pro"),
        "messages": [
            {"role": "system", "content": "Return only URLs, one per line. No explanations."},
            {"role": "user", "content": prompt},
        ],
        "search_domain_filter": domain_filter,  # ✅ Use API parameter for domain filtering
        "search_recency_filter": "year",
        "return_citations": True,
    }
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=40,
        )
        if resp.status_code >= 400:
            return []
        data = resp.json()
        content = (data.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
        return _extract_urls(content)
    except Exception:
        return []
