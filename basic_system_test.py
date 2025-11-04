"""
Basic System Test - Tests core components without complex dependencies
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_core_libraries():
    """Test core library functions"""
    logger.info("Testing core library functions...")
    
    results = {
        "sanitize": {"available": False, "success": False},
        "composer": {"available": False, "success": False},
        "cse": {"available": False, "success": False},
        "perplexity": {"available": False, "success": False}
    }
    
    # Test sanitize
    try:
        from lib.sanitize import normalize_query
        test_query = "分布式光伏发电项目如何备案？"
        normalized = normalize_query(test_query)
        results["sanitize"] = {
            "available": True,
            "success": bool(normalized),
            "input": test_query,
            "output": normalized
        }
    except Exception as e:
        results["sanitize"]["error"] = str(e)
    
    # Test composer
    try:
        from lib.composer import compose_response
        # Mock candidates for testing
        mock_candidates = [
            {
                "title": "分布式光伏发电管理办法",
                "content": "分布式光伏发电项目应当按照国家有关规定进行备案...",
                "url": "http://example.com/doc1"
            }
        ]
        response = compose_response(mock_candidates, "分布式光伏发电项目如何备案？", "zh-CN")
        results["composer"] = {
            "available": True,
            "success": bool(response and response.get("answer_zh")),
            "response_preview": str(response.get("answer_zh", ""))[:100] + "..." if response.get("answer_zh") else "No answer"
        }
    except Exception as e:
        results["composer"]["error"] = str(e)
    
    # Test CSE
    try:
        from lib.cse import discover_documents
        urls = discover_documents("gd", "solar", "grid")
        results["cse"] = {
            "available": True,
            "success": isinstance(urls, list),
            "urls_found": len(urls) if isinstance(urls, list) else 0
        }
    except Exception as e:
        results["cse"]["error"] = str(e)
    
    # Test Perplexity (if available)
    try:
        # Check if perplexity module exists
        import importlib.util
        spec = importlib.util.find_spec("lib.perplexity")
        
        if spec is not None:
            from lib.perplexity import answer_with_perplexity
            
            perplexity_result = answer_with_perplexity(
                "分布式光伏发电项目如何备案？",
                "gd",
                "solar",
                lang="zh-CN",
                doc_class="grid"
            )
            
            results["perplexity"] = {
                "available": True,
                "success": bool(perplexity_result and perplexity_result.get("citations")),
                "citations_count": len(perplexity_result.get("citations", [])) if perplexity_result else 0,
                "answer_preview": str(perplexity_result.get("answer_zh", ""))[:100] + "..." if perplexity_result and perplexity_result.get("answer_zh") else "No answer"
            }
        else:
            results["perplexity"] = {
                "available": False,
                "error": "Perplexity module not found"
            }
            
    except Exception as e:
        results["perplexity"]["error"] = str(e)
    
    return results

def test_20_queries_with_composer():
    """Test 20 queries using the composer function directly"""
    logger.info("Testing 20 queries with composer function...")
    
    test_queries = [
        {
            "id": "solar_basic_filing",
            "query": "分布式光伏发电项目如何备案？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["备案", "分布式光伏", "申请"]
        },
        {
            "id": "wind_grid_connection", 
            "query": "风电项目并网需要什么条件？",
            "province": "sd",
            "asset": "wind",
            "expected_keywords": ["并网", "风电", "条件"]
        },
        {
            "id": "coal_environmental",
            "query": "煤电项目环保要求有哪些？",
            "province": "nm",
            "asset": "coal",
            "expected_keywords": ["环保", "煤电", "要求"]
        },
        {
            "id": "guangdong_renewable_approval",
            "query": "广东省新能源项目审批流程包括哪些步骤？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["广东", "审批", "流程"]
        },
        {
            "id": "grid_technical_standards",
            "query": "电网接入技术标准对设备有什么要求？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["电网", "技术标准", "设备"]
        },
        {
            "id": "solar_capacity_limits",
            "query": "分布式光伏装机容量有什么限制？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["装机容量", "限制"]
        },
        {
            "id": "wind_environmental_impact",
            "query": "风电项目环境影响评价需要哪些材料？",
            "province": "sd",
            "asset": "wind",
            "expected_keywords": ["环境影响", "材料"]
        },
        {
            "id": "coal_safety_requirements",
            "query": "煤电项目安全生产有什么规定？",
            "province": "nm",
            "asset": "coal",
            "expected_keywords": ["安全生产", "规定"]
        },
        {
            "id": "renewable_subsidy_policy",
            "query": "可再生能源补贴政策最新变化是什么？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["补贴政策", "变化"]
        },
        {
            "id": "grid_connection_fees",
            "query": "电网接入费用如何计算？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["接入费用", "计算"]
        },
        {
            "id": "shandong_wind_planning",
            "query": "山东省风电发展规划有哪些重点区域？",
            "province": "sd",
            "asset": "wind",
            "expected_keywords": ["山东", "发展规划", "区域"]
        },
        {
            "id": "coal_emission_monitoring",
            "query": "煤电厂排放监测要求是什么？",
            "province": "nm",
            "asset": "coal",
            "expected_keywords": ["排放监测", "要求"]
        },
        {
            "id": "distributed_solar_metering",
            "query": "分布式光伏计量装置安装有什么标准？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["计量装置", "标准"]
        },
        {
            "id": "wind_noise_standards",
            "query": "风电项目噪声控制标准是多少？",
            "province": "sd",
            "asset": "wind",
            "expected_keywords": ["噪声控制", "标准"]
        },
        {
            "id": "coal_water_usage",
            "query": "煤电项目用水指标有什么限制？",
            "province": "nm",
            "asset": "coal",
            "expected_keywords": ["用水指标", "限制"]
        },
        {
            "id": "solar_land_use_policy",
            "query": "光伏项目土地使用政策有哪些变化？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["土地使用", "政策"]
        },
        {
            "id": "offshore_wind_permits",
            "query": "海上风电项目需要哪些许可证？",
            "province": "sd",
            "asset": "wind",
            "expected_keywords": ["海上风电", "许可证"]
        },
        {
            "id": "coal_ash_disposal",
            "query": "煤电厂粉煤灰处置有什么规定？",
            "province": "nm",
            "asset": "coal",
            "expected_keywords": ["粉煤灰", "处置"]
        },
        {
            "id": "energy_storage_integration",
            "query": "储能系统与新能源项目如何配套？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["储能系统", "配套"]
        },
        {
            "id": "cross_provincial_transmission",
            "query": "跨省电力输送项目审批程序是什么？",
            "province": "gd",
            "asset": "solar",
            "expected_keywords": ["跨省", "审批程序"]
        }
    ]
    
    query_results = []
    
    try:
        from lib.composer import compose_response
        from lib.sanitize import normalize_query
        
        for query_data in test_queries:
            start_time = time.time()
            
            try:
                # Normalize query
                normalized_query = normalize_query(query_data["query"])
                
                # Create mock candidates (simulating search results)
                mock_candidates = [
                    {
                        "title": f"{query_data['asset']}项目相关规定",
                        "content": f"关于{query_data['query']}的相关规定和要求...",
                        "url": f"http://example.com/{query_data['province']}/{query_data['asset']}/doc1"
                    },
                    {
                        "title": f"{query_data['province']}省能源管理办法",
                        "content": f"根据{query_data['province']}省的相关政策，{query_data['asset']}项目需要...",
                        "url": f"http://example.com/{query_data['province']}/policy/doc2"
                    }
                ]
                
                # Compose response
                response = compose_response(mock_candidates, normalized_query, "zh-CN")
                response_time = time.time() - start_time
                
                # Calculate accuracy score
                accuracy_score = calculate_accuracy_score(response, query_data)
                
                query_results.append({
                    "query_id": query_data["id"],
                    "query": query_data["query"],
                    "province": query_data["province"],
                    "asset": query_data["asset"],
                    "response_time": response_time,
                    "success": bool(response and response.get("answer_zh")),
                    "accuracy_score": accuracy_score,
                    "response_preview": str(response.get("answer_zh", ""))[:200] + "..." if response and response.get("answer_zh") else "No answer"
                })
                
            except Exception as e:
                query_results.append({
                    "query_id": query_data["id"],
                    "query": query_data["query"],
                    "province": query_data["province"],
                    "asset": query_data["asset"],
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e),
                    "accuracy_score": 0.0
                })
            
            # Small delay between queries
            time.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Failed to test queries: {str(e)}")
        return {"error": f"Failed to test queries: {str(e)}"}
    
    return query_results

def calculate_accuracy_score(response: dict, query_data: dict) -> float:
    """Calculate a simple accuracy score based on response content"""
    if not response or not response.get("answer_zh"):
        return 0.0
    
    answer = response.get("answer_zh", "")
    expected_keywords = query_data.get("expected_keywords", [])
    
    if not expected_keywords:
        return 0.5  # Default score if no keywords
    
    answer_lower = answer.lower()
    keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
    keyword_score = keyword_matches / len(expected_keywords)
    
    # Check response length (longer responses generally better)
    length_score = min(1.0, len(answer) / 200)  # Normalize to 200 chars
    
    # Check for citations
    citations_score = 0.3 if response.get("citations") else 0.0
    
    # Weighted score
    total_score = (keyword_score * 0.5) + (length_score * 0.3) + (citations_score * 0.2)
    
    return min(1.0, total_score)

def generate_rollout_assessment(core_results: dict, query_results: list) -> dict:
    """Generate rollout readiness assessment"""
    
    # Calculate metrics
    total_queries = len(query_results)
    successful_queries = sum(1 for q in query_results if q.get("success", False))
    success_rate = successful_queries / total_queries if total_queries > 0 else 0
    
    accuracy_scores = [q["accuracy_score"] for q in query_results if q.get("success", False)]
    avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    
    response_times = [q["response_time"] for q in query_results if q.get("success", False)]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Assess core components
    core_components_working = sum(1 for comp in core_results.values() if comp.get("success", False))
    total_core_components = len(core_results)
    core_success_rate = core_components_working / total_core_components if total_core_components > 0 else 0
    
    perplexity_available = core_results.get("perplexity", {}).get("available", False)
    
    # Calculate readiness score
    readiness_factors = {
        "core_components": core_success_rate,
        "query_success_rate": success_rate,
        "accuracy_score": avg_accuracy,
        "response_time": min(1.0, 5.0 / max(avg_response_time, 0.1)),  # Target <5s
        "perplexity_integration": 0.5 if perplexity_available else 0.0
    }
    
    readiness_score = (
        readiness_factors["core_components"] * 0.3 +
        readiness_factors["query_success_rate"] * 0.25 +
        readiness_factors["accuracy_score"] * 0.25 +
        readiness_factors["response_time"] * 0.15 +
        readiness_factors["perplexity_integration"] * 0.05
    )
    
    # Determine critical issues
    critical_issues = []
    warnings = []
    
    if core_success_rate < 0.8:
        critical_issues.append(f"Core components not fully functional: {core_success_rate:.1%} success rate")
    
    if success_rate < 0.8:
        critical_issues.append(f"Query success rate too low: {success_rate:.1%} (target: >80%)")
    
    if avg_accuracy < 0.6:
        critical_issues.append(f"Average accuracy too low: {avg_accuracy:.2f} (target: >0.6)")
    
    if avg_response_time > 10.0:
        critical_issues.append(f"Response time too high: {avg_response_time:.2f}s (target: <10s)")
    
    # Warnings
    if success_rate < 0.9:
        warnings.append(f"Query success rate could be improved: {success_rate:.1%}")
    
    if avg_accuracy < 0.7:
        warnings.append(f"Accuracy could be improved: {avg_accuracy:.2f}")
    
    if not perplexity_available:
        warnings.append("Perplexity integration not available")
    
    # Determine readiness
    if readiness_score >= 0.8 and len(critical_issues) == 0:
        overall_readiness = "READY"
        go_no_go = "GO"
    elif readiness_score >= 0.6 and len(critical_issues) <= 1:
        overall_readiness = "READY_WITH_CONDITIONS"
        go_no_go = "CONDITIONAL_GO"
    else:
        overall_readiness = "NOT_READY"
        go_no_go = "NO_GO"
    
    return {
        "overall_readiness": overall_readiness,
        "go_no_go_decision": go_no_go,
        "readiness_score": readiness_score,
        "readiness_factors": readiness_factors,
        "metrics": {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": success_rate,
            "average_accuracy": avg_accuracy,
            "average_response_time": avg_response_time,
            "core_success_rate": core_success_rate,
            "perplexity_available": perplexity_available
        },
        "critical_issues": critical_issues,
        "warnings": warnings,
        "recommendations": generate_recommendations(readiness_score, critical_issues, warnings, core_results)
    }

def generate_recommendations(readiness_score: float, critical_issues: list, warnings: list, core_results: dict) -> list:
    """Generate recommendations based on assessment"""
    recommendations = []
    
    if readiness_score < 0.8:
        recommendations.append("Improve system reliability and performance before full rollout")
    
    if critical_issues:
        recommendations.append("Address all critical issues before proceeding with deployment")
    
    # Component-specific recommendations
    if not core_results.get("sanitize", {}).get("success", False):
        recommendations.append("Fix query sanitization functionality")
    
    if not core_results.get("composer", {}).get("success", False):
        recommendations.append("Fix response composition functionality")
    
    if not core_results.get("cse", {}).get("success", False):
        recommendations.append("Fix document discovery functionality")
    
    if not core_results.get("perplexity", {}).get("available", False):
        recommendations.append("Implement Perplexity integration for enhanced responses")
    
    # General recommendations
    recommendations.extend([
        "Implement comprehensive monitoring and alerting",
        "Plan for gradual traffic migration with rollback capability",
        "Establish clear operational procedures and team training",
        "Set up automated backup and recovery procedures",
        "Conduct load testing under production conditions",
        "Implement proper error handling and logging",
        "Set up health check endpoints for monitoring"
    ])
    
    return recommendations

def generate_report(results: dict) -> str:
    """Generate comprehensive verification report"""
    assessment = results["assessment"]
    core_results = results["core_results"]
    query_results = results["query_results"]
    
    report = f"""# Production RAG System Verification Report

## Executive Summary

**Verification Date:** {results['timestamp']}
**Overall Readiness:** {assessment['overall_readiness']}
**Go/No-Go Decision:** {assessment['go_no_go_decision']}
**Readiness Score:** {assessment['readiness_score']:.2f}/1.0

## Core Component Analysis

### Component Status
"""
    
    for component, result in core_results.items():
        status = "✓" if result.get("success", False) else "✗"
        available = "✓" if result.get("available", False) else "✗"
        report += f"- **{component.upper()}:** Available: {available}, Working: {status}\n"
        if result.get("error"):
            report += f"  - Error: {result['error']}\n"
    
    report += f"""
### Core System Metrics
- **Component Success Rate:** {assessment['metrics']['core_success_rate']:.1%}
- **Perplexity Integration:** {'Available' if assessment['metrics']['perplexity_available'] else 'Not Available'}

## Query Response Analysis (20 Test Queries)

### Overall Metrics
- **Total Queries:** {assessment['metrics']['total_queries']}
- **Successful Queries:** {assessment['metrics']['successful_queries']}
- **Success Rate:** {assessment['metrics']['success_rate']:.1%}
- **Average Accuracy Score:** {assessment['metrics']['average_accuracy']:.3f}
- **Average Response Time:** {assessment['metrics']['average_response_time']:.2f}s

### Query Performance by Asset Type

"""
    
    # Group queries by asset type
    assets = {}
    for query in query_results:
        asset = query.get('asset', 'unknown')
        if asset not in assets:
            assets[asset] = []
        assets[asset].append(query)
    
    for asset, queries in assets.items():
        successful = [q for q in queries if q.get('success', False)]
        if successful:
            avg_accuracy = sum(q['accuracy_score'] for q in successful) / len(successful)
            avg_response_time = sum(q['response_time'] for q in successful) / len(successful)
        else:
            avg_accuracy = 0
            avg_response_time = 0
        
        report += f"""#### {asset.upper()} Asset Queries
- **Total:** {len(queries)}
- **Successful:** {len(successful)}
- **Success Rate:** {len(successful)/len(queries):.1%}
- **Avg Accuracy:** {avg_accuracy:.3f}
- **Avg Response Time:** {avg_response_time:.2f}s

"""
    
    # Top and bottom performing queries
    successful_queries = [q for q in query_results if q.get('success', False)]
    if successful_queries:
        top_queries = sorted(successful_queries, key=lambda x: x['accuracy_score'], reverse=True)[:5]
        bottom_queries = sorted(successful_queries, key=lambda x: x['accuracy_score'])[:5]
        
        report += "### Top Performing Queries\n\n"
        for i, query in enumerate(top_queries, 1):
            report += f"{i}. **{query['query_id']}** (Score: {query['accuracy_score']:.3f}, Time: {query['response_time']:.2f}s)\n"
            report += f"   - {query['query']}\n\n"
        
        if len(successful_queries) > 5:
            report += "### Lowest Performing Queries\n\n"
            for i, query in enumerate(bottom_queries, 1):
                report += f"{i}. **{query['query_id']}** (Score: {query['accuracy_score']:.3f}, Time: {query['response_time']:.2f}s)\n"
                report += f"   - {query['query']}\n\n"
    
    # Issues and recommendations
    if assessment['critical_issues']:
        report += "## Critical Issues\n\n"
        for issue in assessment['critical_issues']:
            report += f"- ❌ {issue}\n"
        report += "\n"
    
    if assessment['warnings']:
        report += "## Warnings\n\n"
        for warning in assessment['warnings']:
            report += f"- ⚠️ {warning}\n"
        report += "\n"
    
    report += "## Recommendations\n\n"
    for rec in assessment['recommendations']:
        report += f"- 📋 {rec}\n"
    
    # Final assessment
    report += f"""
## Final Assessment as Lead Engineer

**Decision:** {assessment['go_no_go_decision']}

"""
    
    if assessment['go_no_go_decision'] == "GO":
        report += """✅ **System is ready for production rollout.**

The system has passed all critical tests and meets production readiness criteria. The core components are functional, query success rate is acceptable, and response times are within target ranges.
"""
    elif assessment['go_no_go_decision'] == "CONDITIONAL_GO":
        report += """⚠️ **System is ready with conditions.**

The system meets most criteria but has some issues that should be addressed. Consider a phased rollout with close monitoring and be prepared for quick rollback if issues arise.
"""
    else:
        report += """❌ **System is not ready for production rollout.**

Critical issues must be resolved before deployment. The system does not meet minimum production readiness criteria.
"""
    
    report += f"""
## Lead Engineer Strategic Recommendations

Based on this comprehensive verification, as a lead engineer, here are my strategic recommendations:

### Immediate Actions (Next 1-2 weeks):
1. **Fix Critical Issues:** Address all identified critical issues before any deployment consideration
2. **Component Stabilization:** Ensure all core components (sanitize, composer, CSE) are fully functional
3. **Error Handling:** Implement robust error handling and logging throughout the system
4. **Monitoring Setup:** Deploy comprehensive monitoring and alerting infrastructure

### Short-term Actions (1-2 months):
1. **Perplexity Integration:** Complete Perplexity integration to enhance response quality
2. **Performance Optimization:** Optimize response times through caching and resource scaling
3. **Testing Infrastructure:** Implement automated testing and CI/CD pipeline
4. **Documentation:** Complete operational procedures and team training materials

### Medium-term Strategy (3-6 months):
1. **Gradual Migration:** Plan and execute gradual traffic migration from current system
2. **Advanced Monitoring:** Implement advanced analytics and performance monitoring
3. **Capacity Planning:** Establish capacity planning and auto-scaling capabilities
4. **Continuous Improvement:** Set up feedback loops for continuous system improvement

### Risk Mitigation:
1. **Rollback Procedures:** Establish and test clear rollback procedures
2. **Parallel Running:** Run new system in parallel with current system during migration
3. **Monitoring Alerts:** Set up comprehensive alerting for all critical metrics
4. **Team Training:** Ensure operations team is fully trained on new system

### Success Metrics:
- Query success rate > 95%
- Average accuracy score > 0.75
- Response time < 5 seconds (95th percentile)
- System availability > 99.9%
- Zero critical incidents during first month

---

*Report generated on {datetime.utcnow().isoformat()}*
*Lead Engineer Assessment: {'APPROVED' if assessment['go_no_go_decision'] == 'GO' else 'CONDITIONAL' if assessment['go_no_go_decision'] == 'CONDITIONAL_GO' else 'REJECTED'} for Production Deployment*
"""
    
    return report

def main():
    """Run the verification"""
    logger.info("Starting basic system verification...")
    
    # Test core components
    core_results = test_core_libraries()
    
    # Test 20 queries
    query_results = test_20_queries_with_composer()
    
    # Handle error case
    if isinstance(query_results, dict) and "error" in query_results:
        logger.error(f"Query testing failed: {query_results['error']}")
        query_results = []
    
    # Generate assessment
    assessment = generate_rollout_assessment(core_results, query_results)
    
    # Save results
    results_dir = Path("verification_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    full_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "core_results": core_results,
        "query_results": query_results,
        "assessment": assessment
    }
    
    # Save JSON results
    with open(results_dir / f"basic_verification_{timestamp}.json", "w") as f:
        json.dump(full_results, f, indent=2, default=str)
    
    # Generate report
    report = generate_report(full_results)
    with open(results_dir / f"basic_verification_report_{timestamp}.md", "w") as f:
        f.write(report)
    
    # Print summary
    print("\n" + "="*80)
    print("PRODUCTION SYSTEM VERIFICATION COMPLETE")
    print("="*80)
    print(f"Overall Readiness: {assessment['overall_readiness']}")
    print(f"Go/No-Go Decision: {assessment['go_no_go_decision']}")
    print(f"Readiness Score: {assessment['readiness_score']:.2f}/1.0")
    
    metrics = assessment['metrics']
    print(f"\nKey Metrics:")
    print(f"  Core Component Success Rate: {metrics['core_success_rate']:.1%}")
    print(f"  Query Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Average Accuracy: {metrics['average_accuracy']:.2f}")
    print(f"  Average Response Time: {metrics['average_response_time']:.2f}s")
    print(f"  Perplexity Available: {'✓' if metrics['perplexity_available'] else '✗'}")
    
    print(f"\nCore Components:")
    for component, result in core_results.items():
        status = "✓" if result.get("success", False) else "✗"
        available = "✓" if result.get("available", False) else "✗"
        print(f"  {component.upper()}: Available {available}, Working {status}")
    
    if assessment['critical_issues']:
        print(f"\nCritical Issues ({len(assessment['critical_issues'])}):")
        for issue in assessment['critical_issues']:
            print(f"  ❌ {issue}")
    
    if assessment['warnings']:
        print(f"\nWarnings ({len(assessment['warnings'])}):")
        for warning in assessment['warnings']:
            print(f"  ⚠️ {warning}")
    
    print(f"\nDetailed results saved to: verification_results/basic_verification_{timestamp}.json")
    print(f"Report saved to: verification_results/basic_verification_report_{timestamp}.md")
    print("="*80)
    
    # Lead Engineer Summary
    print("\n" + "="*80)
    print("LEAD ENGINEER ASSESSMENT")
    print("="*80)
    
    if assessment['go_no_go_decision'] == "GO":
        print("✅ RECOMMENDATION: PROCEED WITH PRODUCTION DEPLOYMENT")
        print("   System meets all critical criteria for production rollout.")
    elif assessment['go_no_go_decision'] == "CONDITIONAL_GO":
        print("⚠️  RECOMMENDATION: CONDITIONAL DEPLOYMENT WITH MONITORING")
        print("   System is functional but requires close monitoring and quick rollback capability.")
    else:
        print("❌ RECOMMENDATION: DO NOT DEPLOY TO PRODUCTION")
        print("   Critical issues must be resolved before deployment consideration.")
    
    print(f"\nNext Steps:")
    for i, rec in enumerate(assessment['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    print("="*80)

if __name__ == "__main__":
    main()