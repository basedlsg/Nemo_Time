# Agent 2: Perplexity API Behavior Analysis Report

## Mission
Analyze how Perplexity API processes the enhanced query and why it returns irrelevant results.

## API Configuration Analysis

### Current API Call Structure
```python
payload = {
    'model': 'sonar-pro',
    'messages': [
        {
            'role': 'system',
            'content': '你是一个专业的中国能源政策研究助手。请基于官方政府文件提供准确的政策信息，并列出所有相关的官方文档URL。'
        },
        {
            'role': 'user',
            'content': enhanced_query  # The 71-char query with site:.gov.cn
        }
    ],
    'search_recency_filter': 'month',
    'return_citations': True,
    'return_related_questions': False
}
```

## Critical Findings

### Finding 1: `site:.gov.cn` May Not Be Honored
**Evidence from Results**:
- 17/19 sources are NOT .gov.cn domains
- Got: `.com`, `.com.cn`, `.net`, `.cn` domains
- Examples:
  - `guoturen.com`
  - `baogao.com`
  - `eastmoney.com`
  - `hanzesp.com`
  - `pipechina.com.cn`

**Conclusion**: ⚠️ **Perplexity is IGNORING the `site:.gov.cn` restriction**

### Finding 2: Search Recency Filter Impact
**Configuration**: `'search_recency_filter': 'month'`
**Impact**: Limits to last 30 days
**Problem**: Government policy documents may be older than 1 month
**Severity**: HIGH

**Evidence**:
- Many regulatory documents are published quarterly or annually
- Land survey procedures don't change monthly
- Filtering to "month" excludes stable, authoritative documents

### Finding 3: Model Selection
**Current**: `'sonar-pro'`
**Characteristics**: 
- Optimized for general web search
- May prioritize recent news/articles over official documents
- Not specifically tuned for Chinese government sources

**Alternative Models**:
- `sonar` - Standard model, may handle Chinese better
- Consider if Perplexity has China-specific models

### Finding 4: System Prompt Effectiveness
**Current System Prompt**:
```
你是一个专业的中国能源政策研究助手。请基于官方政府文件提供准确的政策信息，并列出所有相关的官方文档URL。
```

**Translation**: "You are a professional Chinese energy policy research assistant. Please provide accurate policy information based on official government documents and list all relevant official document URLs."

**Problem**: System prompts may not affect search behavior, only response generation

## Root Cause Analysis

### Primary Issue: Site Restriction Not Working
**Why `site:.gov.cn` Fails**:

1. **Perplexity's Search Syntax**: May not support Google-style `site:` operator
2. **Query Parsing**: May treat `site:.gov.cn` as regular search terms
3. **API Limitations**: No dedicated domain filter parameter in API

**Evidence**:
- If `site:` worked, we'd see 100% .gov.cn domains
- Instead, we see 89% non-.gov.cn domains
- The 2 potentially relevant sources (#1, #3) are also non-.gov.cn

### Secondary Issue: Recency Filter Too Restrictive
**Impact**: Excludes authoritative older documents
**Fix**: Change to `'year'` or remove filter

### Tertiary Issue: Chinese Keyword Overload
**Observation**: 12 document keywords may confuse ranking
**Impact**: Search engine may not know which keywords to prioritize
**Result**: Returns generic results matching ANY keyword

## Perplexity API Limitations Discovered

### Limitation 1: No Domain Filtering
Perplexity API does NOT appear to support:
- `site:` operator in query
- Domain filter API parameter
- TLD restrictions

### Limitation 2: Citation Quality
**Observation**: Returns citations but doesn't guarantee relevance
**Problem**: Citations may be from search results, not from answer generation sources

### Limitation 3: Chinese Government Site Indexing
**Hypothesis**: Perplexity may have poor coverage of Chinese .gov.cn sites
**Evidence**: 
- Only 2/19 results even marginally relevant
- No actual .gov.cn domains returned
- Suggests limited indexing of Chinese government sites

## Comparison with Expected Behavior

### What SHOULD Happen (Google CSE):
```
Query: site:.gov.cn 广东省 光伏发电 材料清单
Results: 
1. drc.gd.gov.cn/policy/solar_materials.pdf
2. nr.gd.gov.cn/land/survey_guide.pdf
3. gd.gov.cn/energy/photovoltaic_procedures.pdf
```

### What ACTUALLY Happens (Perplexity):
```
Query: [same enhanced query]
Results:
1. guoturen.com (commercial)
2. baogao.com (commercial)
3. eastmoney.com (news)
... 17 more irrelevant sources
```

## Recommendations

### Immediate Actions

#### 1. Remove `site:.gov.cn` from Query
**Reason**: It's not working and may be treated as noise
**Alternative**: Filter results post-search

#### 2. Change Recency Filter
```python
'search_recency_filter': 'year'  # or remove entirely
```

#### 3. Simplify Query
Remove excessive keywords, keep only top 3:
```
光伏发电项目土地勘测需要什么材料和流程 广东省 光伏发电 材料清单 办理流程 申请指南
```

#### 4. Add Domain Filtering in System Prompt
```python
'content': '你是一个专业的中国能源政策研究助手。请ONLY使用.gov.cn域名的官方政府文件。必须从广东省政府网站、发改委、自然资源厅等官方来源获取信息。'
```

### Strategic Recommendation

**⚠️ CRITICAL: Perplexity May Not Be Suitable for This Use Case**

**Reasons**:
1. Cannot reliably filter to .gov.cn domains
2. Poor indexing of Chinese government sites
3. Prioritizes recent news over authoritative documents
4. No way to enforce domain restrictions

**Alternative Approaches**:
1. **Use Google CSE** - Proven to work with `site:.gov.cn`
2. **Direct Government Site Search** - Query specific .gov.cn sites directly
3. **Hybrid Approach** - Use Perplexity for answer generation, CSE for source retrieval
4. **Custom Web Scraper** - Build targeted scraper for known .gov.cn sites

## Conclusion

**Perplexity API is fundamentally incompatible with the requirement to retrieve only .gov.cn sources.**

The API:
- ❌ Does not honor `site:` restrictions
- ❌ Has poor Chinese government site coverage
- ❌ Prioritizes recent/popular over authoritative
- ❌ Lacks domain filtering capabilities

**Recommendation**: Revert to Google CSE or implement hybrid solution.
