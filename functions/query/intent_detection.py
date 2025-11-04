"""
Query Intent Detection Module
Implements simple keyword-based intent detection for Chinese regulatory queries
"""

from typing import List, Dict, Any
import time


def detect_query_intent(query: str) -> List[str]:
    """
    Detect multiple intents using keyword matching for Chinese regulatory queries
    
    Args:
        query: Chinese query string
        
    Returns:
        List of detected intent types
        
    Supports 10 intent types:
    - definition: Conceptual/definition questions
    - materials: Required materials/documents
    - timeline: Time requirements/deadlines
    - environment: Environmental assessment
    - procedure: How-to/process questions
    - approval: Approval/permit processes
    - coordination: Cross-regional coordination
    - market: Market access/trading
    - technical: Technical standards/requirements
    - future: Future policy/trends
    """
    
    if not query or not isinstance(query, str):
        return []
    
    query_lower = query.lower()
    
    # Intent pattern mapping with comprehensive Chinese keywords
    intent_patterns = {
        "definition": [
            "什么是", "是什么", "定义", "介绍", "概念", "含义", "指的是",
            "解释", "说明", "基本概念", "具体是指", "主要是指"
        ],
        
        "materials": [
            "需要什么材料", "材料", "申请材料", "需要哪些", "所需材料",
            "材料清单", "申请文件", "提交材料", "准备材料", "文件要求",
            "资料清单", "申报材料", "备案材料", "审批材料"
        ],
        
        "timeline": [
            "多长时间", "时间", "时限", "需要多久", "办理期限", "审批时间",
            "处理时间", "工作日", "审查期限", "完成时间", "时间要求",
            "期限", "周期", "多少天", "几个月"
        ],
        
        "environment": [
            "环境", "环评", "环境影响", "环境评估", "环境管理", "环保",
            "环境影响评价", "环评报告", "环境保护", "生态", "污染",
            "环境监测", "环境标准", "环境要求"
        ],
        
        "procedure": [
            "如何", "怎么", "流程", "程序", "步骤", "具体程序", "办理流程",
            "申请流程", "操作流程", "处理流程", "审批流程", "实施流程",
            "办事流程", "手续", "办理程序"
        ],
        
        "approval": [
            "审批", "许可证", "审批指南", "许可清单", "申请程序", "核准",
            "备案", "审查", "批准", "许可", "证书", "执照", "资质",
            "审批程序", "核准程序", "备案程序"
        ],
        
        "coordination": [
            "协调", "跨省", "跨区域", "部门协调", "协调机制", "统筹",
            "多部门", "联合", "配合", "衔接", "协同", "跨部门",
            "区域协调", "省际协调"
        ],
        
        "market": [
            "市场交易", "准入", "交易规则", "结算", "市场准入", "交易",
            "市场", "准入条件", "交易机制", "市场机制", "交易平台",
            "市场化", "竞价", "招标"
        ],
        
        "technical": [
            "标准", "技术要求", "排放", "监测", "技术标准", "技术规范",
            "技术条件", "技术参数", "设备要求", "装机容量", "技术指标",
            "性能要求", "质量标准", "安全标准", "接入", "并网", "电网",
            "改造", "灵活性", "容量", "功率"
        ],
        
        "future": [
            "未来", "调整", "趋势", "发展", "政策预期", "规划展望",
            "前景", "预测", "变化", "改革", "发展方向", "政策走向",
            "未来政策", "发展规划", "长远规划", "目标", "碳达峰", "碳中和"
        ]
    }
    
    detected_intents = []
    
    # Check each intent pattern
    for intent, keywords in intent_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_intents.append(intent)
    
    return detected_intents


def get_document_keywords(intents: List[str]) -> str:
    """
    Map detected intents to specific Chinese document type keywords
    
    Args:
        intents: List of detected intent types
        
    Returns:
        Space-separated string of document type keywords
    """
    
    if not intents:
        return ""
    
    # Document type keyword mapping for each intent
    doc_type_mapping = {
        "definition": "定义 基本概念 介绍 说明 概念解释",
        
        "materials": "材料清单 申请指南 所需材料 申请材料 文件要求 资料清单",
        
        "timeline": "审批时限 流程时间 办理期限 时间要求 处理时间 审查期限",
        
        "environment": "环评指南 环境管理 环境影响评价 环境评估 环保要求 生态保护",
        
        "procedure": "实施细则 操作指南 具体程序 办事指南 办理流程 实施办法",
        
        "approval": "审批指南 许可清单 申请程序 审批流程 核准程序 备案程序",
        
        "coordination": "协调机制 跨区域 部门协调 统筹管理 联合管理 协同机制",
        
        "market": "市场准入 交易规则 结算办法 市场机制 交易机制 准入条件",
        
        "technical": "技术标准 监测要求 具体指标 技术规范 技术条件 设备要求",
        
        "future": "政策预期 发展趋势 规划展望 政策调整 发展规划 未来政策"
    }
    
    keywords = []
    for intent in intents:
        if intent in doc_type_mapping:
            keywords.append(doc_type_mapping[intent])
    
    return " ".join(keywords)


def build_enhanced_query(query: str, province: str, asset: str) -> Dict[str, Any]:
    """
    Build enhanced query with intent-specific document keywords
    
    Args:
        query: Original user query
        province: Province code (gd, sd, nm)
        asset: Asset type (solar, wind, coal)
        
    Returns:
        Dictionary with enhanced query and metadata
    """
    
    # Province mapping
    province_names = {
        'gd': '广东省',
        'sd': '山东省', 
        'nm': '内蒙古自治区'
    }
    
    # Asset mapping
    asset_names = {
        'solar': '光伏发电',
        'wind': '风力发电',
        'coal': '煤电'
    }
    
    province_name = province_names.get(province, province)
    asset_name = asset_names.get(asset, asset)
    
    # Detect query intent
    intents = detect_query_intent(query)
    
    # Get targeted document keywords
    doc_keywords = get_document_keywords(intents)
    
    # Build enhanced query
    base_query = f"{query} {province_name} {asset_name}"
    
    if doc_keywords:
        # Intent-based enhancement
        enhanced_query = f"{base_query} {doc_keywords} site:.gov.cn"
        enhancement_type = "intent_based"
    else:
        # Fallback to current generic approach
        enhanced_query = f"{base_query} 政府政策 官方文件 site:.gov.cn"
        enhancement_type = "generic"
    
    return {
        "enhanced_query": enhanced_query,
        "intents_detected": intents,
        "enhancement_type": enhancement_type,
        "doc_keywords_used": doc_keywords,
        "province_name": province_name,
        "asset_name": asset_name
    }


def validate_intent_detection(query: str, intents: List[str]) -> bool:
    """
    Validate that detected intents make sense for the query
    
    Args:
        query: Original query string
        intents: List of detected intents
        
    Returns:
        True if intents are valid, False otherwise
    """
    
    if not intents:
        return True  # No intents is valid
    
    # Basic validation rules
    if len(intents) > 3:
        return False  # Too many intents likely indicates over-matching
    
    # Check for conflicting intents (optional - can be expanded)
    conflicting_pairs = [
        ("definition", "procedure"),  # Asking what vs how
    ]
    
    for intent1, intent2 in conflicting_pairs:
        if intent1 in intents and intent2 in intents:
            # Allow if query is complex enough (more lenient threshold)
            if len(query) < 8:  # Very short queries shouldn't have conflicting intents
                return False
    
    return True


def log_intent_performance(query: str, intents: List[str], processing_time: float) -> Dict[str, Any]:
    """
    Log intent detection performance for monitoring
    
    Args:
        query: Original query
        intents: Detected intents
        processing_time: Processing time in seconds
        
    Returns:
        Performance metrics dictionary
    """
    
    metrics = {
        "query_length": len(query),
        "intents_detected": len(intents),
        "processing_time_ms": processing_time * 1000,
        "enhancement_type": "intent_based" if intents else "generic",
        "intents": intents,
        "timestamp": time.time()
    }
    
    # Log to console for now (can be extended to proper logging system)
    print(f"Intent Detection Performance: {metrics}")
    
    return metrics