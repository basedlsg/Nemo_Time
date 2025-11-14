# Agent 3: Search Result Quality Evaluation Report

## Mission
Deep analysis of the 19 returned sources to identify failure patterns and categorize issues.

## Overall Quality Metrics

| Metric | Value | Target | Gap |
|--------|-------|--------|-----|
| Relevant Sources (4-5/5) | 2 (10.5%) | 15+ (80%) | -69.5% |
| Marginally Relevant (3/5) | 1 (5.3%) | 3 (15%) | -9.7% |
| Irrelevant (1-2/5) | 16 (84.2%) | 1 (5%) | +79.2% |
| .gov.cn Domains | 0 (0%) | 19 (100%) | -100% |
| Guangdong-specific | 1 (5.3%) | 19 (100%) | -94.7% |
| Solar/PV-specific | 2 (10.5%) | 19 (100%) | -89.5% |

**Overall Grade**: F (10.5% relevance rate)

## Failure Pattern Analysis

### Pattern 1: Wrong Domain Type (84% of results)
**Count**: 16/19 sources

**Categories**:
1. **Commercial Sites** (8 sources):
   - guoturen.com, baogao.com, hanzesp.com, hbtfhn.com, hbtcxcl.com, wjstjh.com, zdl8.net, kuliion.com
   - **Issue**: Private companies, not government authorities

2. **News/Media** (3 sources):
   - eastmoney.com, oliannews.com, aki-driving.com
   - **Issue**: Secondary sources, not primary regulatory documents

3. **Industry Portals** (2 sources):
   - chinarpte.com, zbcg.sdhsg.com
   - **Issue**: Industry aggregators, not official policy sources

4. **Professional Services** (1 source):
   - shanghai.dacheng.com (law firm)
   - **Issue**: Legal services, not government documents

5. **Corporate** (2 sources):
   - pipechina.com.cn (CSR report), sgsonline.com.cn
   - **Issue**: Corporate documents, not regulatory guidance

### Pattern 2: Wrong Geographic Scope (68% of results)
**Count**: 13/19 sources

**Wrong Provinces**:
- Shanghai: 2 sources (#2, #9)
- Qinghai: 1 source (#11)
- Hunan: 1 source (#19)
- Unspecified/National: 9 sources

**Correct Province** (Guangdong): 1 source (#3 - possibly)

**Issue**: Query specified "广东省" but most results ignore this

### Pattern 3: Wrong Topic (63% of results)
**Count**: 12/19 sources

**Unrelated Topics**:
- Pipeline infrastructure (#5)
- General procurement (#15)
- Driving/automotive (#13)
- Generic sitemaps (#4, #6, #8, #16, #18, #19)
- Lawyer profiles (#9)
- Industry directories (#7, #10, #14)

**Issue**: No connection to photovoltaic, land surveying, or energy policy

### Pattern 4: Wrong Document Type (100% of results)
**Count**: 19/19 sources

**What We Got**:
- Sitemaps: 6 sources
- News articles: 3 sources
- Company pages: 4 sources
- Industry directories: 3 sources
- CSR report: 1 source
- Lawyer profile: 1 source
- Unclear: 1 source

**What We Needed**:
- Policy documents (政策文件)
- Application guides (申请指南)
- Material checklists (材料清单)
- Procedural manuals (办事指南)
- Implementation rules (实施细则)

**Issue**: Zero official government procedural documents

## Detailed Source Categorization

### Tier 1: Potentially Salvageable (2 sources)

#### Source #1: guoturen.com/page/difangfagui
- **Score**: 4/5
- **Type**: Local regulations aggregator
- **Pros**: May contain Guangdong policies
- **Cons**: Secondary source, not official
- **Salvageable**: Yes, as a pointer to official documents

#### Source #3: finance.eastmoney.com/...
- **Score**: 3/5
- **Type**: Financial news with policy updates
- **Pros**: May mention recent Guangdong PV policies
- **Cons**: News interpretation, not primary source
- **Salvageable**: Partially, for context only

### Tier 2: Completely Irrelevant (17 sources)

**Geographic Mismatch** (4 sources):
- #2: Shanghai (wrong province)
- #9: Shanghai (wrong province)
- #11: Qinghai (wrong province)
- #19: Hunan (wrong province)

**Topic Mismatch** (6 sources):
- #5: Pipeline CSR report
- #13: Driving/automotive
- #14: Generic industry info
- #15: Procurement portal
- #17: Corporate mobile portal
- #7, #10: Supplier directories

**Useless Navigation Pages** (7 sources):
- #4, #6, #8, #16, #18: Sitemaps
- #12: News scroll page

## Root Cause of Poor Results

### Cause 1: Search Engine Behavior
**Observation**: Results look like generic web search, not targeted government document search
**Implication**: Perplexity treated this as broad web search, not specialized regulatory search

### Cause 2: Keyword Dilution
**Observation**: 12 document keywords may have caused search to match ANY keyword
**Example**: "材料" (materials) matches supplier sites, "清单" (list) matches directories

### Cause 3: No Domain Enforcement
**Observation**: Zero .gov.cn domains despite `site:.gov.cn` in query
**Implication**: Domain restriction completely ignored

### Cause 4: Recency Bias
**Observation**: News sites and recent updates prioritized over stable policy documents
**Implication**: `search_recency_filter: 'month'` hurt more than helped

### Cause 5: Poor Chinese Government Site Indexing
**Observation**: Even marginally relevant sources are commercial aggregators, not official sites
**Implication**: Perplexity may not have good coverage of .gov.cn domains

## Expected vs Actual Results

### Expected (High-Quality Results):
```
1. http://drc.gd.gov.cn/policy/solar_land_survey_materials_2024.pdf [5/5]
   - Guangdong DRC official material checklist

2. http://nr.gd.gov.cn/land/photovoltaic_survey_procedures.pdf [5/5]
   - Guangdong Natural Resources Dept survey procedures

3. http://gd.gov.cn/energy/solar_project_application_guide.pdf [5/5]
   - Guangdong government official application guide

4. http://nea.gov.cn/policy/distributed_solar_management.pdf [4/5]
   - National Energy Administration (national context)

5. http://gd.csg.cn/grid/solar_connection_requirements.pdf [5/5]
   - Guangdong Power Grid connection requirements
```

### Actual (Low-Quality Results):
```
1. guoturen.com - Commercial regulations aggregator [4/5]
2. baogao.com - Shanghai report site [1/5]
3. eastmoney.com - Financial news [3/5]
4-19. Various sitemaps, supplier directories, wrong provinces [1/5]
```

**Quality Gap**: 95% of expected value missing

## Recommendations

### Immediate Quality Improvements

#### 1. Post-Search Filtering
Since Perplexity won't filter, we must:
```python
def filter_results(citations):
    filtered = []
    for url in citations:
        if '.gov.cn' in url:  # Only government domains
            if any(province in url for province in ['gd.gov.cn', 'guangdong']):  # Guangdong priority
                filtered.append(url)
    return filtered
```

#### 2. Result Validation
Check each result for:
- Domain type (.gov.cn required)
- Geographic relevance (Guangdong keywords)
- Topic relevance (solar/photovoltaic keywords)
- Document type (PDF, policy, guide)

#### 3. Fallback Strategy
If <3 relevant results:
- Query specific known government sites directly
- Use Google CSE as backup
- Return error message requesting manual search

### Strategic Quality Assurance

#### 1. Known Source Database
Build a database of known Guangdong government sites:
```python
KNOWN_SOURCES = [
    'drc.gd.gov.cn',  # Development & Reform Commission
    'nr.gd.gov.cn',   # Natural Resources
    'gd.gov.cn',      # Provincial government
    'gd.csg.cn',      # Power grid
    'nea.gov.cn',     # National Energy Admin
]
```

#### 2. Direct Site Search
Query these sites directly instead of relying on Perplexity:
```python
for site in KNOWN_SOURCES:
    query = f"site:{site} 光伏 土地勘测 材料"
    # Use site-specific search or scraping
```

#### 3. Quality Scoring System
Implement automated relevance scoring:
```python
def score_result(url, title, content):
    score = 0
    if '.gov.cn' in url: score += 40
    if 'gd.gov.cn' in url or '广东' in title: score += 30
    if '光伏' in title or '太阳能' in title: score += 20
    if '材料' in title or '流程' in title: score += 10
    return score
```

## Conclusion

**The search results are catastrophically poor** (10.5% relevance rate).

**Primary Issues**:
1. ❌ Zero .gov.cn domains (100% failure on domain requirement)
2. ❌ 95% wrong geographic scope (not Guangdong)
3. ❌ 89% wrong topic (not solar/land survey)
4. ❌ 100% wrong document type (no official guides)

**Root Cause**: Perplexity API is not suitable for targeted government document retrieval.

**Recommendation**: Abandon Perplexity for source retrieval, use only for answer generation with pre-validated sources.
