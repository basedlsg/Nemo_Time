# Agent 1: Query Construction Analysis Report

## Mission
Analyze how the enhanced query was constructed and identify any issues in the query building process.

## Test Query
**Original**: "光伏发电项目土地勘测需要什么材料和流程"  
**Translation**: "What materials and procedures are required for land surveying of photovoltaic projects"  
**Province**: Guangdong (gd)  
**Asset**: Solar (solar)

## Query Construction Flow Analysis

### Step 1: Intent Detection
**Function**: `detect_query_intent(query)`

**Keywords Matched**:
- "需要什么材料" → **materials** intent
- "流程" → **procedure** intent

**Result**: ✅ CORRECT
- Detected: `["materials", "procedure"]`
- Both intents are accurate for the query

### Step 2: Document Keyword Mapping
**Function**: `get_document_keywords(intents)`

**Mapping Applied**:
```python
"materials" → "材料清单 申请指南 所需材料 申请材料 文件要求 资料清单"
"procedure" → "实施细则 操作指南 具体程序 办事指南 办理流程 实施办法"
```

**Result**: ✅ CORRECT
- Keywords are highly relevant for Chinese government documents
- Covers official terminology used in regulatory documents

### Step 3: Enhanced Query Construction
**Function**: `build_enhanced_query(query, province, asset)`

**Components Added**:
1. Province name: "广东省"
2. Asset name: "光伏发电"
3. Document keywords: (from step 2)
4. Site restriction: "site:.gov.cn"

**Final Enhanced Query**:
```
光伏发电项目土地勘测需要什么材料和流程 广东省 光伏发电 材料清单 申请指南 所需材料 申请材料 文件要求 资料清单 实施细则 操作指南 具体程序 办事指南 办理流程 实施办法 site:.gov.cn
```

**Result**: ✅ CORRECT CONSTRUCTION
- All components properly included
- Syntax is valid
- Keywords are appropriate

## Critical Finding

### ⚠️ QUERY IS CORRECTLY CONSTRUCTED

The query construction logic is **working as designed**. The problem is NOT in how we build the query.

### Evidence:
1. Intent detection: ✅ Accurate
2. Keyword mapping: ✅ Relevant
3. Province/asset injection: ✅ Correct
4. Site restriction: ✅ Present (`site:.gov.cn`)

## Potential Issues Identified

### Issue 1: Query Length
**Observation**: Enhanced query is 71 characters (Chinese) + keywords
**Impact**: May be too long for some search engines to process effectively
**Severity**: MEDIUM

### Issue 2: Keyword Density
**Observation**: 12 document-type keywords added
**Impact**: May dilute search focus or confuse ranking algorithms
**Severity**: LOW-MEDIUM

### Issue 3: Site Restriction Placement
**Observation**: `site:.gov.cn` is at the END of the query
**Impact**: Some search engines may not properly apply site restrictions when placed at the end
**Severity**: HIGH - **LIKELY ROOT CAUSE**

## Recommendations

### Immediate Fix: Reorder Query Components
```python
# Current (potentially problematic):
enhanced_query = f"{base_query} {doc_keywords} site:.gov.cn"

# Recommended:
enhanced_query = f"site:.gov.cn {base_query} {doc_keywords}"
```

### Alternative Fix: Use Perplexity's Domain Parameter
Instead of `site:.gov.cn` in query string, use API parameter if available:
```python
payload = {
    'model': 'sonar-pro',
    'messages': [...],
    'search_domain_filter': ['.gov.cn'],  # If supported
    ...
}
```

### Optimization: Reduce Keyword Count
Limit to top 3-5 most relevant keywords per intent:
```python
"materials" → "材料清单 申请指南 所需材料"  # Reduced from 6
"procedure" → "实施细则 办理流程 操作指南"  # Reduced from 6
```

## Conclusion

**Query construction is NOT the primary failure point**. The logic correctly:
- Detects intents
- Maps to relevant keywords
- Includes province and asset context
- Adds site restriction

**The failure likely occurs in**:
1. How Perplexity interprets/honors the `site:.gov.cn` restriction
2. How Perplexity ranks results with many Chinese keywords
3. Perplexity's understanding of Chinese regulatory document types

**Next Investigation**: Agent 2 must analyze Perplexity API behavior.
