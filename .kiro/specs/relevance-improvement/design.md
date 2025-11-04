# Design Document

## Overview

Implement simple query intent detection to improve document relevance from 78% to 90%+ by adding targeted document type keywords instead of generic "政府政策 官方文件" for all queries.

## Architecture

### Intent Detection Engine

```python
def detect_query_intent(query: str) -> list:
    """Detect multiple intents using keyword matching"""
    intent_patterns = {
        "definition": ["什么是", "是什么", "定义", "介绍"],
        "materials": ["需要什么材料", "材料", "申请材料", "需要哪些", "所需材料"],
        "timeline": ["多长时间", "时间", "时限", "需要多久", "办理期限"],
        "environment": ["环境", "环评", "环境影响", "环境评估", "环境管理"],
        "procedure": ["如何", "怎么", "流程", "程序", "步骤", "具体程序"],
        "approval": ["审批", "许可证", "审批指南", "许可清单", "申请程序"],
        "coordination": ["协调", "跨省", "跨区域", "部门协调", "协调机制"],
        "market": ["市场交易", "准入", "交易规则", "结算", "市场准入"],
        "technical": ["标准", "技术要求", "排放", "监测", "技术标准"],
        "future": ["未来", "调整", "趋势", "发展", "政策预期", "规划展望"]
    }
    
    detected_intents = []
    for intent, keywords in intent_patterns.items():
        if any(keyword in query for keyword in keywords):
            detected_intents.append(intent)
    
    return detected_intents
```

### Document Type Mapping

```python
def get_document_keywords(intents: list) -> str:
    """Map intents to specific document type keywords"""
    doc_type_mapping = {
        "definition": "定义 基本概念 介绍 说明",
        "materials": "材料清单 申请指南 所需材料 申请材料",
        "timeline": "审批时限 流程时间 办理期限 时间要求",
        "environment": "环评指南 环境管理 环境影响评价 环境评估",
        "procedure": "实施细则 操作指南 具体程序 办事指南",
        "approval": "审批指南 许可清单 申请程序 审批流程",
        "coordination": "协调机制 跨区域 部门协调 统筹管理",
        "market": "市场准入 交易规则 结算办法 市场机制",
        "technical": "技术标准 监测要求 具体指标 技术规范",
        "future": "政策预期 发展趋势 规划展望 政策调整"
    }
    
    keywords = []
    for intent in intents:
        if intent in doc_type_mapping:
            keywords.append(doc_type_mapping[intent])
    
    return " ".join(keywords)
```

## Components and Interfaces

### Enhanced Query Builder

```python
def build_enhanced_query(query: str, province: str, asset: str) -> dict:
    """Build query with intent-specific document keywords"""
    
    # Detect query intent
    intents = detect_query_intent(query)
    
    # Get targeted document keywords
    doc_keywords = get_document_keywords(intents)
    
    # Build enhanced query
    base_query = f"{query} {province} {asset}"
    
    if doc_keywords:
        enhanced_query = f"{base_query} {doc_keywords} site:.gov.cn"
        enhancement_type = "intent_based"
    else:
        # Fallback to current approach
        enhanced_query = f"{base_query} 政府政策 官方文件 site:.gov.cn"
        enhancement_type = "generic"
    
    return {
        "enhanced_query": enhanced_query,
        "intents_detected": intents,
        "enhancement_type": enhancement_type,
        "doc_keywords_used": doc_keywords
    }
```

### Integration Point

Modify existing `enhanced_query_perplexity_with_precision()` function:

```python
def enhanced_query_perplexity_with_precision(query: str, province: str, asset: str) -> dict:
    # ... existing code ...
    
    # Replace generic enhancement with intent-based enhancement
    query_enhancement = build_enhanced_query(query, province_name, asset_name)
    
    # ... rest of function using query_enhancement["enhanced_query"] ...
    
    return {
        "success": True,
        "response": enhanced_response,
        "query_enhanced": query_enhancement["enhanced_query"],
        "intents_detected": query_enhancement["intents_detected"],
        "enhancement_type": query_enhancement["enhancement_type"],
        "retrieval_time": 1.2,
        "enhancement_level": "intent_precision"
    }
```

## Data Models

### Intent Detection Result

```python
@dataclass
class IntentDetectionResult:
    intents: List[str]
    doc_keywords: str
    enhancement_type: str
    confidence_score: float
```

### Query Enhancement Result

```python
@dataclass
class QueryEnhancementResult:
    original_query: str
    enhanced_query: str
    intents_detected: List[str]
    doc_keywords_used: str
    enhancement_type: str
    expected_relevance_improvement: float
```

## Error Handling

### Fallback Strategy

1. **No Intent Detected**: Fall back to current generic enhancement
2. **Multiple Conflicting Intents**: Combine all relevant keywords
3. **Performance Issues**: Cache intent detection results for common queries
4. **Empty Results**: Retry with broader document keywords

### Validation

```python
def validate_intent_detection(query: str, intents: list) -> bool:
    """Validate that detected intents make sense for the query"""
    if not intents:
        return True  # No intents is valid
    
    # Basic validation rules
    if len(intents) > 3:
        return False  # Too many intents likely indicates over-matching
    
    return True
```

## Testing Strategy

### Before/After Comparison

1. **Baseline Test**: Run current system on 20 test queries
2. **Enhanced Test**: Run intent-based system on same queries
3. **Relevance Scoring**: Compare document types returned vs. expected
4. **Gap Analysis**: Identify queries that still need improvement

### Test Cases by Intent Type

```python
test_cases = {
    "definition": ["什么是光伏?", "风电是什么?", "煤电项目是什么?"],
    "materials": ["光伏项目备案需要什么材料?", "煤电项目需要哪些许可证?"],
    "timeline": ["光伏项目审批需要多长时间?"],
    "environment": ["山东省风电项目环境评估有什么特殊要求?"],
    "procedure": ["风电项目如何接入电网?"],
    "complex": ["内蒙古煤电项目在碳达峰目标下的灵活性改造政策要求?"]
}
```

### Success Metrics

- **Overall Relevance**: 78% → 90%+
- **Definition Queries**: 85% → 95%+ (should get concept docs)
- **Procedural Queries**: 70% → 90%+ (should get implementation guides)
- **Environmental Queries**: 65% → 85%+ (should get EIA-specific docs)
- **Complex Queries**: 75% → 85%+ (should get comprehensive policy docs)

## Performance Considerations

### Optimization Strategies

1. **Keyword Caching**: Cache intent detection for common query patterns
2. **Parallel Processing**: Run intent detection alongside existing enhancements
3. **Minimal Overhead**: Keep intent detection under 10ms per query
4. **Memory Efficiency**: Use simple string operations, avoid heavy NLP

### Monitoring

```python
def log_intent_performance(query: str, intents: list, processing_time: float):
    """Log intent detection performance for monitoring"""
    metrics = {
        "query_length": len(query),
        "intents_detected": len(intents),
        "processing_time_ms": processing_time * 1000,
        "enhancement_type": "intent_based" if intents else "generic"
    }
    # Log to monitoring system
```

This design provides a simple, effective solution to boost relevance by matching query intent to appropriate document types, directly addressing the gaps identified in your 78% relevance analysis.