# Implementation Plan

- [x] 1. Add intent detection function
  - Create `detect_query_intent()` with comprehensive keyword patterns for 10 intent types
  - Map definition, materials, timeline, environment, procedure, approval, coordination, market, technical, and future intents
  - Use simple string matching for performance (avoid heavy NLP)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.2_

- [x] 2. Create document type keyword mapping
  - Implement `get_document_keywords()` to map intents to specific Chinese document terms
  - Include targeted keywords like "材料清单", "实施细则", "环评指南", "市场准入" etc.
  - Support multiple intents per query by combining keywords
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.3_

- [x] 3. Build enhanced query construction
  - Create `build_enhanced_query()` function to replace generic "政府政策 官方文件"
  - Integrate intent detection with existing province/asset enhancement
  - Maintain fallback to current behavior when no intent detected
  - Add metadata tracking for intents detected and enhancement type
  - _Requirements: 1.5, 2.5, 3.3, 5.4, 5.5_

- [ ] 4. Modify existing query enhancement function
  - Update `enhanced_query_perplexity_with_precision()` to use intent-based enhancement
  - Replace generic keyword addition with targeted document type keywords
  - Preserve existing response structure while adding intent metadata
  - _Requirements: 3.1, 3.4_

- [ ] 5. Create relevance testing framework
  - Implement before/after comparison using the 20 test queries from analysis
  - Score relevance based on document types returned vs. query intent expectations
  - Generate detailed gap analysis for queries that don't improve
  - Track improvement from 78% baseline to 90%+ target
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 6. Add performance monitoring
  - Log intent detection performance and processing times
  - Track enhancement type distribution (intent_based vs. generic)
  - Monitor relevance scores over time
  - _Requirements: Performance optimization_

- [ ]* 7. Create validation and error handling
  - Add intent detection validation to prevent over-matching
  - Implement fallback strategies for edge cases
  - Add query enhancement result validation
  - _Requirements: Error handling and robustness_