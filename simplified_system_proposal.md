# Simplified System Architecture Proposal
## RAG-Anything + Perplexity Only

**Current Problem:** Google CSE adds complexity without delivering usable results  
**Solution:** Direct RAG-Anything + Perplexity integration

---

## Architecture Comparison

### Current (Complex)
```
Query → CSE Discovery → URL Validation → Document Access → Fallback Templates
         ↓              ↓                ↓
    160+ API calls   100% failure    "Unknown Document"
```

### Proposed (Simple)
```
Query → RAG-Anything Processing → Perplexity Enhancement → Real Citations
         ↓                        ↓                       ↓
    Direct processing        Real-time discovery      Authentic sources
```

---

## Benefits of Simplified Approach

### 1. **Eliminates CSE Bottleneck**
- No URL discovery failures
- No network timeout issues  
- No rate limiting problems
- No domain validation complexity

### 2. **Real Document Access**
- Perplexity provides actual document content
- No "Unknown Document" placeholders
- Authentic government source citations
- Real-time document synthesis

### 3. **Reduced Complexity**
- Single integration point (Perplexity API)
- Simplified error handling
- Faster response times
- Easier maintenance

### 4. **Better Results**
- Actual document retrieval vs. URL discovery
- Real citations vs. broken links
- Current information vs. stale indexes
- Verified sources vs. inaccessible URLs

---

## Implementation Changes

### Remove Components:
- `lib/cse.py` (Google Custom Search)
- `lib/vertex_index.py` (Vector search complexity)
- URL validation and accessibility checking
- Domain allowlist management

### Keep Components:
- `rag_anything_prototype/` (Core RAG processing)
- Perplexity API integration
- `lib/composer.py` (Response formatting)
- `lib/sanitize.py` (Query processing)

### Simplified Flow:
1. **Query Processing:** Normalize and sanitize input
2. **RAG-Anything:** Process with Chinese regulatory context
3. **Perplexity Enhancement:** Real-time document discovery
4. **Response Composition:** Format with authentic citations

---

## Expected Results

### Committee Concerns Addressed:
- ✅ Real document retrieval (via Perplexity)
- ✅ Authentic citations (government sources)
- ✅ No "Unknown Document" placeholders
- ✅ Verifiable information sources
- ✅ Transparent retrieval method

### Performance Improvements:
- Faster response times (no CSE delays)
- Higher success rates (no URL validation failures)
- Better accuracy (real-time document access)
- Simpler deployment (fewer dependencies)

---

## Migration Path

1. **Phase 1:** Test Perplexity-only responses
2. **Phase 2:** Remove CSE dependencies  
3. **Phase 3:** Optimize RAG-Anything integration
4. **Phase 4:** Deploy simplified system

This approach directly addresses the independent committee's core concern: the system should retrieve and cite real documents, not generate templates with placeholder citations.