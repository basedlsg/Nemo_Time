# Alternative Document Discovery Options (No CSE)
## Objective Analysis of Viable Approaches for Chinese Government Documents

**Date**: November 14, 2024
**Context**: CSE has 0% success rate, need proven alternative for .gov.cn document discovery

---

## EXECUTIVE SUMMARY

**Recommended Approach**: **Option 3 (Manual Curation + Automation Hybrid)** - Proven, pragmatic, production-ready in 1-2 weeks

**Why Not Others:**
- Bing/Baidu APIs: Same issues as CSE (unreliable Chinese gov site indexing)
- Perplexity: Already proven 89% failure rate
- Pure scraping: Legal/technical complexity, high maintenance

---

## OPTION 1: Bing Web Search API

### How It Works
Microsoft's Bing Search API with Chinese market support

### Implementation
```python
import requests

def search_with_bing(query, province, asset):
    endpoint = "https://api.bing.microsoft.com/v7.0/search"

    # Build site-restricted query
    search_query = f"{query} site:.gov.cn {province} {asset}"

    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY
    }

    params = {
        "q": search_query,
        "mkt": "zh-CN",  # Chinese market
        "count": 50,
        "offset": 0
    }

    response = requests.get(endpoint, headers=headers, params=params)
    results = response.json()

    # Extract URLs
    urls = [result['url'] for result in results.get('webPages', {}).get('value', [])]

    # Filter for .gov.cn
    gov_urls = [u for u in urls if '.gov.cn' in u]

    return gov_urls
```

### Pros
- ✅ Official API with SLA
- ✅ Better Chinese site coverage than Google
- ✅ Supports site: operator
- ✅ Pricing: $7/1000 queries (cheaper than CSE)
- ✅ 50 results per query (vs. 10 for CSE)

### Cons
- ❌ Still dependent on Bing's gov.cn indexing (unproven)
- ❌ Rate limits: 3 calls/second, 1000/month on free tier
- ❌ May have same issues as CSE (poor Chinese gov indexing)

### Validation Steps
1. Sign up: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
2. Test query: "广东 光伏 并网 site:.gov.cn"
3. Check if results contain actual .gov.cn URLs
4. Verify URLs are accessible

### Estimated Implementation Time
- 2-4 hours if Bing returns valid results
- **Risk**: May fail for same reasons as CSE

**Verdict**: 🟡 **Worth 2-hour test, but high risk of same failure**

---

## OPTION 2: Direct Web Scraping (Selenium/Beautiful Soup)

### How It Works
Directly scrape known provincial government websites

### Target Sites
```python
KNOWN_GOV_SITES = {
    'gd': {
        'base_url': 'https://drc.gd.gov.cn',
        'search_path': '/search',
        'energy_path': '/zwgk/zdlyxx/',  # Energy info section
    },
    'sd': {
        'base_url': 'http://drc.shandong.gov.cn',
        'search_path': '/search.jsp',
        'energy_path': '/art/2024/energy/',
    },
    'nm': {
        'base_url': 'https://fgw.nmg.gov.cn',
        'search_path': '/search',
        'energy_path': '/zwgk/xxgk/zdgz/',  # Key work areas
    }
}
```

### Implementation
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def scrape_gov_site(province, keywords):
    """
    Scrape specific government site for documents
    """
    config = KNOWN_GOV_SITES[province]

    # Setup headless browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    # Navigate to energy section
    url = config['base_url'] + config['energy_path']
    driver.get(url)
    time.sleep(3)  # Wait for dynamic content

    # Parse page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find document links (site-specific selectors)
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        text = a_tag.get_text(strip=True)

        # Check if relevant
        if any(kw in text for kw in keywords):
            full_url = href if href.startswith('http') else config['base_url'] + href
            links.append({
                'url': full_url,
                'title': text
            })

    driver.quit()
    return links

# Usage
solar_docs_gd = scrape_gov_site('gd', ['光伏', '太阳能', '分布式'])
```

### Pros
- ✅ **Direct access** - no dependency on search engines
- ✅ **Guaranteed gov sources** - scraping actual gov sites
- ✅ **No API costs** - free (except compute)
- ✅ **Customizable** - can adapt per site structure

### Cons
- ❌ **High maintenance** - sites change structure frequently
- ❌ **Site-specific code** - need separate scraper per province
- ❌ **Legal gray area** - may violate terms of service
- ❌ **Rate limiting risk** - gov sites may block aggressive scraping
- ❌ **Dynamic content** - requires Selenium (slow, resource-intensive)
- ❌ **Fragile** - breaks when sites redesign

### Estimated Implementation Time
- 40-60 hours for 3 provinces (20h per site)
- Ongoing maintenance: 5-10 hours/month

**Verdict**: ❌ **Not Recommended** - too fragile, high maintenance

---

## OPTION 3: Manual Curation + Automation Hybrid ✅ **RECOMMENDED**

### How It Works
Combine human curation with automated processing

### Phase 1: Seed Collection (Human)
1. **Hire research assistant** (or do yourself): 8-16 hours
2. **Collect 50-100 key documents**:
   - Visit provincial development & reform commission sites
   - Download actual regulatory PDFs/documents
   - Organize by province/asset/doc_class
3. **Catalog with metadata**:
   ```json
   {
     "url": "https://drc.gd.gov.cn/files/solar_grid_2024.pdf",
     "title": "广东省分布式光伏发电项目并网管理办法",
     "province": "gd",
     "asset": "solar",
     "doc_class": "grid",
     "effective_date": "2024-01-15",
     "authority": "广东省发展改革委",
     "downloaded_date": "2024-11-14",
     "checksum": "abc123..."
   }
   ```

### Phase 2: Automated Processing (System)
1. **Upload to GCS**: Store raw documents
2. **Document AI OCR**: Extract text
3. **Metadata extraction**: Parse effective dates, authorities
4. **Chunking**: Sentence-aware Chinese chunking
5. **Embedding**: Vertex AI text-embedding-004
6. **Index**: Upsert to Vertex AI Vector Search

### Phase 3: Incremental Updates (Monthly)
1. **Monitor gov sites** (manual check once/month)
2. **Add new documents** as discovered
3. **Update corpus** incrementally

### Implementation
```python
import json
import hashlib
from google.cloud import storage
from document_processor import process_document

# 1. Seed corpus structure
SEED_CORPUS = [
    {
        "url": "https://drc.gd.gov.cn/attachment/0/572/572345/3624872.pdf",
        "title": "广东省分布式光伏发电项目管理暂行办法",
        "province": "gd",
        "asset": "solar",
        "doc_class": "grid",
        "local_path": "./seed_docs/gd_solar_grid_001.pdf"
    },
    # ... 49 more documents
]

# 2. Batch processing function
def ingest_seed_corpus(corpus_list):
    """
    Process pre-collected documents
    """
    results = []

    for doc in corpus_list:
        try:
            # Download if URL provided
            if not doc.get('local_path'):
                content = download_document(doc['url'])
                local_path = save_temp(content)
            else:
                local_path = doc['local_path']

            # Process through existing pipeline
            processed = process_document(
                local_path,
                province=doc['province'],
                asset=doc['asset'],
                doc_class=doc['doc_class']
            )

            results.append({
                'doc': doc,
                'status': 'success',
                'chunks_created': len(processed.get('chunks', []))
            })

        except Exception as e:
            results.append({
                'doc': doc,
                'status': 'failed',
                'error': str(e)
            })

    return results

# 3. Usage
results = ingest_seed_corpus(SEED_CORPUS)
print(f"Successfully processed: {sum(1 for r in results if r['status'] == 'success')}/50")
```

### Pros
- ✅ **Guaranteed quality** - every document verified
- ✅ **100% .gov.cn sources** - no commercial site contamination
- ✅ **Fast to production** - 1-2 weeks vs. 2-3 months
- ✅ **Proven approach** - used by enterprise RAG systems
- ✅ **Leverages existing pipeline** - DocAI, Vertex AI all work
- ✅ **Scalable** - can grow corpus incrementally
- ✅ **Low risk** - no dependency on unreliable APIs
- ✅ **Cost-effective** - one-time curation cost

### Cons
- ❌ **Manual work upfront** - 8-16 hours for seed collection
- ❌ **Not fully automated** - requires monthly maintenance
- ❌ **Limited coverage** - starts with 50-100 docs (not 1000s)

### Cost Breakdown
```
Seed Collection:
  - Research assistant: $200-400 (8-16h @ $25/h)
  - OR: Your time: 8-16 hours

Processing (one-time):
  - Document AI: ~$3-5 (50 docs × 20 pages × $1.50/1000 pages)
  - Vertex AI: ~$0.10 (embeddings)
  - Cloud Storage: ~$0.50
  - Total: ~$4-6

Monthly Maintenance:
  - Monitor + add 5-10 new docs: 2-4 hours/month
  - Processing: ~$0.50/month
```

### Estimated Implementation Time
- Week 1: Seed collection (8-16 hours)
- Week 2: Batch processing + validation (8-12 hours)
- **Total**: 16-28 hours to production

**Verdict**: ✅ **STRONGLY RECOMMENDED** - pragmatic, proven, low risk

---

## OPTION 4: Chinese Search Engines (Baidu/Sogou)

### Baidu Web Search API
```python
import requests

def search_baidu(query):
    # Baidu does not have official public API
    # Requires enterprise account or screen scraping
    pass
```

### Reality Check
- ❌ **No public API** - Baidu doesn't offer web search API to general public
- ❌ **Enterprise only** - requires business license in China
- ❌ **Scraping TOS violation** - against Baidu terms of service
- ❌ **CAPTCHA challenges** - aggressive bot detection

**Verdict**: ❌ **Not Viable** - no public API access

---

## OPTION 5: Government API Integration (If Available)

### Research Needed
Investigate if Chinese government ministries provide APIs:

**Potential Sources:**
1. **National Development and Reform Commission (NDRC)**
   - Website: https://www.ndrc.gov.cn
   - Check for: 开放数据 (open data), API接口 (API interface)

2. **National Energy Administration (NEA)**
   - Website: http://www.nea.gov.cn
   - Check for: 政府信息公开 (government information disclosure)

3. **Provincial Data Portals**
   - Guangdong: https://data.gd.gov.cn
   - Shandong: http://data.sd.gov.cn
   - Inner Mongolia: Check provincial gov portal

### Validation Steps
```bash
# Check if open data portals exist
curl https://data.gd.gov.cn/api/
curl http://data.sd.gov.cn/api/

# Look for energy-related datasets
# Check for API documentation
```

### Pros (If Available)
- ✅ **Official source** - most authoritative
- ✅ **Structured data** - likely JSON/XML
- ✅ **Reliable** - government-maintained

### Cons
- ❌ **Unknown availability** - may not exist
- ❌ **Bureaucratic access** - may require government approval
- ❌ **Limited to published data** - may not include all regulations

**Verdict**: 🟡 **Worth 4-hour research** - could be ideal if exists

**Action**: I can research this right now

---

## OPTION 6: Pre-Indexed Document Repositories

### Check Existing Resources

**Academic/Research Repositories:**
1. **China Law Translate**: https://www.chinalawtranslate.com
   - English translations of Chinese laws
   - May have structured database

2. **PKU Law Database**: http://en.pkulaw.cn
   - Peking University legal database
   - Subscription required

3. **Lexis China**: Legal database with Chinese regulations
   - Enterprise subscription

### Pros (If Accessible)
- ✅ **Pre-curated** - already organized
- ✅ **Structured** - likely searchable
- ✅ **Validated** - academic/legal quality

### Cons
- ❌ **Paywalls** - expensive subscriptions ($1000s/year)
- ❌ **Energy focus unclear** - may not cover specific sectors
- ❌ **Outdated** - legal databases lag behind policy changes

**Verdict**: 🟡 **Check free tiers** - may provide seed documents

---

## COMPARISON MATRIX

| Option | Time to Production | Reliability | Cost | Maintenance | Risk |
|--------|-------------------|-------------|------|-------------|------|
| **1. Bing API** | 2-4 hours | 🟡 Unknown | $7/1K queries | Low | High (may fail like CSE) |
| **2. Direct Scraping** | 40-60 hours | 🟡 Fragile | Free | High (5-10h/mo) | Very High |
| **3. Manual Curation ✅** | 16-28 hours | ✅ High | ~$200-400 | Low (2-4h/mo) | Very Low |
| **4. Baidu API** | N/A | ❌ No access | N/A | N/A | N/A |
| **5. Gov API** | 4h research | 🟡 If exists | Free | Low | Medium |
| **6. Repositories** | 8h research | 🟡 If accessible | High | Low | Medium |

---

## RECOMMENDED IMPLEMENTATION PLAN

### Week 1: Validate + Seed Collection

**Day 1-2**: Quick validation tests (8 hours)
- [ ] Test Bing API (2 hours)
- [ ] Research gov APIs (4 hours)
- [ ] Check legal repositories (2 hours)

**Day 3-5**: Seed document collection (16-24 hours)
- [ ] Hire VA or do yourself
- [ ] Collect 50 documents (10 per province/asset combo)
- [ ] Organize in structured format
- [ ] Create metadata catalog

### Week 2: Processing Pipeline

**Day 1-2**: Batch processing (8 hours)
- [ ] Upload to GCS
- [ ] Run Document AI OCR
- [ ] Extract metadata
- [ ] Create chunks

**Day 3**: Vector indexing (4 hours)
- [ ] Generate embeddings
- [ ] Upsert to Vertex AI
- [ ] Validate retrieval

**Day 4-5**: End-to-end testing (8 hours)
- [ ] Test queries against real corpus
- [ ] Validate citations
- [ ] Measure accuracy

### Total Timeline: **10-12 working days**

---

## FINAL RECOMMENDATION

**Primary Path**: **Option 3 (Manual Curation + Automation Hybrid)**

**Rationale:**
1. **Proven**: Every enterprise RAG system starts with curated corpus
2. **Fast**: 2 weeks vs. 2-3 months debugging search APIs
3. **Reliable**: 100% .gov.cn sources, zero contamination
4. **Scalable**: Start with 50, grow to 200, then 500+
5. **Cost-effective**: $200-400 one-time vs. ongoing API costs
6. **Low risk**: No dependencies on unreliable external services

**Fallback**: If you discover gov APIs in research phase, integrate those for automatic updates

**Not Recommended**: CSE, Bing API, direct scraping, Baidu - all have proven or high-probability failure modes

---

## NEXT STEPS

1. **Decision point**: Choose Option 3 (recommended) or allocate 8h for validation tests
2. **If Option 3**:
   - Define seed corpus scope (which regulations to prioritize)
   - Allocate 16 hours for collection (hire VA or self)
   - Schedule 2-week sprint for implementation
3. **Alternative**: I can research gov APIs right now (30 min) before you decide

**Question**: Should I research Chinese government open data APIs to see if Option 5 is viable?
