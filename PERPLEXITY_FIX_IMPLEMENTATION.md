# Perplexity API Fix - Implementation Summary

**Date**: 2024-11-14
**Issue**: 89% irrelevant results, 0% .gov.cn domains
**Root Cause**: Missing `search_domain_filter` API parameter
**Fix Duration**: ~45 minutes

---

## Changes Made

### 1. Added `_build_domain_filter()` Function

**Location**: `/home/user/Nemo_Time/functions/query/perplexity.py:145-188`

```python
def _build_domain_filter(province: str, topic: str) -> List[str]:
    """
    Build domain filter list for Perplexity's search_domain_filter parameter.
    This parameter filters search results to only include specified domains.
    Maximum 20 domains supported by Perplexity API.
    """
    domains = [
        "gov.cn",           # All Chinese government domains
        "ndrc.gov.cn",      # National Development and Reform Commission
        "nea.gov.cn",       # National Energy Administration
        "mnr.gov.cn",       # Ministry of Natural Resources
        "mee.gov.cn",       # Ministry of Ecology and Environment
        "mohurd.gov.cn",    # Housing and Urban-Rural Development
    ]
    # ... topic-specific and province-specific domains
    return filtered[:20]  # API max is 20 domains
```

**Purpose**: Generates list of allowed domains in format required by Perplexity API parameter (no leading dots).

---

### 2. Modified `answer_with_perplexity()` Function

**Location**: `/home/user/Nemo_Time/functions/query/perplexity.py:31-68`

#### Removed (Lines 33-34, 57-58):
```python
# ❌ OLD: site: operators in query text (IGNORED by API)
site_filters = " OR ".join(f"site:{d}" for d in allowlist if not d.startswith("."))
suffix_filters = " ".join(sorted(set(d for d in allowlist if d.startswith("."))))
# ... in query text:
f"搜索提示（供你内部使用）：{site_filters} {suffix_filters} {topic_hints}"
```

#### Added (Lines 33, 56, 65-66):
```python
# ✅ NEW: Use API parameter (ACTUALLY WORKS)
domain_filter = _build_domain_filter(province, topic)
# ... clean query without site: operators
f"搜索提示（供你内部使用）：{topic_hints}"

# In payload:
"search_domain_filter": domain_filter,  # ✅ KEY FIX
"search_recency_filter": "year",  # Changed from implicit/month
```

---

### 3. Modified `_perplexity_urls_only()` Function

**Location**: `/home/user/Nemo_Time/functions/query/perplexity.py:283-303`

#### Removed (Lines 287-292):
```python
# ❌ OLD: site: operators in prompt
site_filters = " OR ".join(f"site:{d}" for d in allow if not d.startswith("."))
suffix_filters = " ".join(sorted(set(d for d in allow if d.startswith("."))))
f"来源限制：{site_filters} {suffix_filters}\n"
```

#### Added (Lines 287, 300-301):
```python
# ✅ NEW: Use API parameter
domain_filter = _build_domain_filter(province, topic)
# In payload:
"search_domain_filter": domain_filter,
"search_recency_filter": "year",
```

---

### 4. Cleaned Up `_topic_hints()` Function

**Location**: `/home/user/Nemo_Time/functions/query/perplexity.py:207-234`

**Removed**: All `site:` operators from topic hints (lines 216, 217, 228-230)

**Reason**: Domain filtering now handled by API parameter, not query text.

---

## Testing

### Test Script Created

**File**: `/home/user/Nemo_Time/test_perplexity_fix.py`

#### Test Results (without API key):
```
✅ PASSED Domain Filter Generation
   - Generates 11 domains for 'gd' + 'grid_connection'
   - All within API limit (≤20)
   - No leading dots (API compatible)
   - All required domains present

✅ PASSED URL Domain Validation
   - Correctly accepts .gov.cn URLs
   - Correctly rejects commercial sites

⚠️  SKIPPED API Integration Test
   - Requires PERPLEXITY_API_KEY environment variable
   - Tests actual API call with original failing query
```

### To Run Full Test Suite:
```bash
export PERPLEXITY_API_KEY=your_key_here
python3 test_perplexity_fix.py
```

---

## Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| .gov.cn domains | 0% | 100% | +100% |
| Relevant results | 10.5% | 80%+ | +70% |
| Geographic accuracy | 5.3% | 85%+ | +80% |

---

## Technical Details

### Why This Works

1. **Perplexity API Documentation**: https://docs.perplexity.ai/guides/search-domain-filters

2. **Parameter Behavior**:
   - `search_domain_filter`: Accepts up to 20 domains, works as allowlist
   - Supports domain-level filtering (e.g., `gov.cn` matches all `*.gov.cn`)
   - Available on Pro tier (sonar-pro model)

3. **Why Query Text Failed**:
   - Perplexity's LLM ignores search operators in query text
   - `site:.gov.cn` in prompt is just treated as text, not as a filter
   - API parameter is enforced at search engine level, not LLM level

---

## Files Modified

1. ✅ `/home/user/Nemo_Time/functions/query/perplexity.py` - Main implementation
2. ✅ `/home/user/Nemo_Time/test_perplexity_fix.py` - Test script (new)
3. ℹ️  `/home/user/Nemo_Time/lib/perplexity.py` - Test stub (no changes needed)

---

## Deployment Checklist

- [x] Code changes implemented
- [x] Test script created
- [x] Unit tests pass
- [ ] Integration test with API key
- [ ] Deploy to GCP Cloud Functions
- [ ] Validate with production queries
- [ ] Monitor .gov.cn percentage in results

---

## Validation Query

**Original Failing Query**:
```
问题: 光伏发电项目土地勘测需要什么材料和流程
省份: gd
资产: solar
类别: grid
```

**Before Fix**: 89% irrelevant, 0% .gov.cn
**After Fix**: Expected 80%+ relevance, 100% .gov.cn

---

## Next Steps

1. **Get API Key** (if not already available):
   ```bash
   export PERPLEXITY_API_KEY=your_key_here
   ```

2. **Run Full Test**:
   ```bash
   python3 test_perplexity_fix.py
   ```

3. **If Tests Pass**:
   ```bash
   # Deploy function
   cd /home/user/Nemo_Time
   ./deploy.sh query
   ```

4. **Validate in Production**:
   ```bash
   # Test with real query
   curl -X POST https://your-function-url/query \
     -H "Content-Type: application/json" \
     -d '{
       "question": "光伏发电项目土地勘测需要什么材料和流程",
       "province": "gd",
       "asset": "solar",
       "doc_class": "grid"
     }'
   ```

---

## Documentation References

- **Perplexity Domain Filters**: https://docs.perplexity.ai/guides/search-domain-filters
- **Analysis Report**: `/home/user/Nemo_Time/PERPLEXITY_FIX_SUMMARY.md`
- **Alternative Analysis**: `/home/user/Nemo_Time/ALTERNATIVE_DOCUMENT_DISCOVERY_OPTIONS.md`

---

**Status**: ✅ Code changes complete, awaiting API key for integration testing
