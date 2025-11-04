"""
Simple verification test to check if the production system components work
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

async def test_current_system():
    """Test the current system components"""
    logger.info("Testing current system components...")
    
    results = {
        "current_system_tests": {},
        "perplexity_integration": {},
        "test_queries": []
    }
    
    # Test current system query function
    try:
        from functions.query.main import query_handler
        from flask import Request
        
        # Create a mock request
        class MockRequest:
            def __init__(self, json_data):
                self._json = json_data
                self.method = 'POST'
            
            def get_json(self, silent=True):
                return self._json
        
        # Test query
        test_request = MockRequest({
            "province": "gd",
            "asset": "solar", 
            "doc_class": "grid",
            "question": "分布式光伏发电项目如何备案？",
            "lang": "zh-CN"
        })
        
        start_time = time.time()
        response = query_handler(test_request)
        response_time = time.time() - start_time
        
        results["current_system_tests"]["query_function"] = {
            "success": True,
            "response_time": response_time,
            "status_code": response.status_code if hasattr(response, 'status_code') else 200
        }
        
    except Exception as e:
        results["current_system_tests"]["query_function"] = {
            "success": False,
            "error": str(e)
        }
    
    # Test Perplexity integration
    try:
        # Check if perplexity module exists
        import importlib.util
        spec = importlib.util.find_spec("lib.perplexity")
        
        if spec is not None:
            from lib.perplexity import answer_with_perplexity
            
            start_time = time.time()
            perplexity_result = answer_with_perplexity(
                "分布式光伏发电项目如何备案？",
                "gd",
                "solar",
                lang="zh-CN",
                doc_class="grid"
            )
            response_time = time.time() - start_time
            
            results["perplexity_integration"] = {
                "available": True,
                "success": bool(perplexity_result and perplexity_result.get("citations")),
                "response_time": response_time,
                "citations_count": len(perplexity_result.get("citations", [])) if perplexity_result else 0
            }
        else:
            results["perplexity_integration"] = {
                "available": False,
                "error": "Perplexity module not found"
            }
            
    except Exception as e:
        results["perplexity_integration"] = {
            "available": False,
            "error": str(e)
        }
    
    return results

async def test_20_queries():
    """Test 20 different queries with the current system"""
    logger.info("Testing 20 queries with current system...")
    
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
    
    # Import query handler
    try:
        from functions.query.main import query_handler
        
        class MockRequest:
            def __init__(self, json_data):
                self._json = json_data
                self.method = 'POST'
            
            def get_json(self, silent=True):
                return self._json
        
        for query_data in test_queries:
            start_time = time.time()
            
            try:
                # Create request
                test_request = MockRequest({
                    "province": query_data["province"],
                    "asset": query_data["asset"],
                    "doc_class": "grid",
                    "question": query_data["query"],
                    "lang": "zh-CN"
                })
                
                # Execute query
                response = query_handler(test_request)
                response_time = time.time() - start_time
                
                # Try to get response data
                response_data = {}
                if hasattr(response, 'get_json'):
                    response_data = response.get_json()
                elif hasattr(response, 'data'):
                    try:
                        response_data = json.loads(response.data.decode('utf-8'))
                    except:
                        response_data = {"raw_response": str(response.data)}
                
                # Calculate accuracy score (simplified)
                accuracy_score = calculate_accuracy_score(response_data, query_data)
                
                query_results.append({
                    "query_id": query_data["id"],
                    "query": query_data["query"],
                    "province": query_data["province"],
                    "asset": query_data["asset"],
                    "response_time": response_time,
                    "success": True,
                    "accuracy_score": accuracy_score,
                    "response_preview": str(response_data.get("answer_zh", ""))[:200] + "..." if response_data.get("answer_zh") else "No answer"
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
            await asyncio.sleep(0.5)
    
    except Exception as e:
        logger.error(f"Failed to import query handler: {str(e)}")
        return {"error": f"Failed to import query handler: {str(e)}"}
    
    return query_results

def calculate_accuracy_score(response_data: dict, query_data: dict) -> float:
    """Calculate a simple accuracy score based on response content"""
    if not response_data or response_data.get("error"):
        return 0.0
    
    answer = response_data.get("answer_zh", "")
    if not answer:
        return 0.0
    
    # Check for expected keywords
    expected_keywords = query_data.get("expected_keywords", [])
    if not expected_keywords:
        return 0.5  # Default score if no keywords
    
    answer_lower = answer.lower()
    keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
    keyword_score = keyword_matches / len(expected_keywords)
    
    # Check response length (longer responses generally better)
    length_score = min(1.0, len(answer) / 200)  # Normalize to 200 chars
    
    # Check for citations
    citations_score = 0.3 if response_data.get("citations") else 0.0
    
    # Weighted score
    total_score = (keyword_score * 0.5) + (length_score * 0.3) + (citations_score * 0.2)
    
    return min(1.0, total_score)

def generate_rollout_assessment(system_results: dict, query_results: list) -> dict:
    """Generate rollout readiness assessment"""
    
    # Calculate metrics
    total_queries = len(query_results)
    successful_queries = sum(1 for q in query_results if q["success"])
    success_rate = successful_queries / total_queries if total_queries > 0 else 0
    
    accuracy_scores = [q["accuracy_score"] for q in query_results if q["success"]]
    avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    
    response_times = [q["response_time"] for q in query_results if q["success"]]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Assess system components
    current_system_working = system_results.get("current_system_tests", {}).get("query_function", {}).get("success", False)
    perplexity_available = system_results.get("perplexity_integration", {}).get("available", False)
    
    # Calculate readiness score
    readiness_factors = {
        "system_functionality": 1.0 if current_system_working else 0.0,
        "query_success_rate": success_rate,
        "accuracy_score": avg_accuracy,
        "response_time": min(1.0, 10.0 / max(avg_response_time, 0.1)),  # Target <10s
        "perplexity_integration": 0.5 if perplexity_available else 0.0
    }
    
    readiness_score = (
        readiness_factors["system_functionality"] * 0.3 +
        readiness_factors["query_success_rate"] * 0.25 +
        readiness_factors["accuracy_score"] * 0.25 +
        readiness_factors["response_time"] * 0.15 +
        readiness_factors["perplexity_integration"] * 0.05
    )
    
    # Determine critical issues
    critical_issues = []
    warnings = []
    
    if not current_system_working:
        critical_issues.append("Current system query function not working")
    
    if success_rate < 0.8:
        critical_issues.append(f"Query success rate too low: {success_rate:.2%} (target: >80%)")
    
    if avg_accuracy < 0.6:
        critical_issues.append(f"Average accuracy too low: {avg_accuracy:.2f} (target: >0.6)")
    
    if avg_response_time > 15.0:
        critical_issues.append(f"Response time too high: {avg_response_time:.2f}s (target: <15s)")
    
    # Warnings
    if success_rate < 0.9:
        warnings.append(f"Query success rate could be improved: {success_rate:.2%}")
    
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
            "system_functionality": current_system_working,
            "perplexity_available": perplexity_available
        },
        "critical_issues": critical_issues,
        "warnings": warnings,
        "recommendations": generate_recommendations(readiness_score, critical_issues, warnings)
    }

def generate_recommendations(readiness_score: float, critical_issues: list, warnings: list) -> list:
    """Generate recommendations based on assessment"""
    recommendations = []
    
    if readiness_score < 0.8:
        recommendations.append("Improve system reliability and performance before full rollout")
    
    if critical_issues:
        recommendations.append("Address all critical issues before proceeding with deployment")
    
    if warnings:
        recommendations.append("Consider addressing warnings to improve system performance")
    
    # General recommendations
    recommendations.extend([
        "Implement comprehensive monitoring and alerting",
        "Plan for gradual traffic migration with rollback capability",
        "Establish clear operational procedures and team training",
        "Set up automated backup and recovery procedures",
        "Conduct load testing under production conditions"
    ])
    
    return recommendations

async def main():
    """Run the verification"""
    logger.info("Starting production system verification...")
    
    # Test system components
    system_results = await test_current_system()
    
    # Test 20 queries
    query_results = await test_20_queries()
    
    # Generate assessment
    assessment = generate_rollout_assessment(system_results, query_results)
    
    # Save results
    results_dir = Path("verification_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    full_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "system_results": system_results,
        "query_results": query_results,
        "assessment": assessment
    }
    
    # Save JSON results
    with open(results_dir / f"verification_{timestamp}.json", "w") as f:
        json.dump(full_results, f, indent=2, default=str)
    
    # Generate report
    report = generate_report(full_results)
    with open(results_dir / f"verification_report_{timestamp}.md", "w") as f:
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
    print(f"  Query Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Average Accuracy: {metrics['average_accuracy']:.2f}")
    print(f"  Average Response Time: {metrics['average_response_time']:.2f}s")
    print(f"  System Functionality: {'✓' if metrics['system_functionality'] else '✗'}")
    print(f"  Perplexity Available: {'✓' if metrics['perplexity_available'] else '✗'}")
    
    if assessment['critical_issues']:
        print(f"\nCritical Issues ({len(assessment['critical_issues'])}):")
        for issue in assessment['critical_issues']:
            print(f"  ❌ {issue}")
    
    if assessment['warnings']:
        print(f"\nWarnings ({len(assessment['warnings'])}):")
        for warning in assessment['warnings']:
            print(f"  ⚠️ {warning}")
    
    print(f"\nDetailed results saved to: verification_results/verification_{timestamp}.json")
    print(f"Report saved to: verification_results/verification_report_{timestamp}.md")
    print("="*80)

def generate_report(results: dict) -> str:
    """Generate comprehensive verification report"""
    assessment = results["assessment"]
    system_results = results["system_results"]
    query_results = results["query_results"]
    
    report = f"""# Production RAG System Verification Report

## Executive Summary

**Verification Date:** {results['timestamp']}
**Overall Readiness:** {assessment['overall_readiness']}
**Go/No-Go Decision:** {assessment['go_no_go_decision']}
**Readiness Score:** {assessment['readiness_score']:.2f}/1.0

## System Component Analysis

### Current System Status
- **Query Function:** {'✓ Working' if system_results.get('current_system_tests', {}).get('query_function', {}).get('success', False) else '✗ Failed'}
- **Response Time:** {system_results.get('current_system_tests', {}).get('query_function', {}).get('response_time', 0):.2f}s

### Perplexity Integration
- **Available:** {'Yes' if system_results.get('perplexity_integration', {}).get('available', False) else 'No'}
- **Success:** {'Yes' if system_results.get('perplexity_integration', {}).get('success', False) else 'No'}
- **Response Time:** {system_results.get('perplexity_integration', {}).get('response_time', 0):.2f}s
- **Citations:** {system_results.get('perplexity_integration', {}).get('citations_count', 0)}

## Query Response Analysis (20 Test Queries)

### Overall Metrics
- **Total Queries:** {assessment['metrics']['total_queries']}
- **Successful Queries:** {assessment['metrics']['successful_queries']}
- **Success Rate:** {assessment['metrics']['success_rate']:.1%}
- **Average Accuracy Score:** {assessment['metrics']['average_accuracy']:.3f}
- **Average Response Time:** {assessment['metrics']['average_response_time']:.2f}s

### Query Performance by Category

"""
    
    # Group queries by category
    categories = {}
    for query in query_results:
        category = query.get('asset', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(query)
    
    for category, queries in categories.items():
        successful = [q for q in queries if q['success']]
        if successful:
            avg_accuracy = sum(q['accuracy_score'] for q in successful) / len(successful)
            avg_response_time = sum(q['response_time'] for q in successful) / len(successful)
        else:
            avg_accuracy = 0
            avg_response_time = 0
        
        report += f"""#### {category.upper()} Queries
- **Total:** {len(queries)}
- **Successful:** {len(successful)}
- **Success Rate:** {len(successful)/len(queries):.1%}
- **Avg Accuracy:** {avg_accuracy:.3f}
- **Avg Response Time:** {avg_response_time:.2f}s

"""
    
    # Top and bottom performing queries
    successful_queries = [q for q in query_results if q['success']]
    if successful_queries:
        top_queries = sorted(successful_queries, key=lambda x: x['accuracy_score'], reverse=True)[:5]
        bottom_queries = sorted(successful_queries, key=lambda x: x['accuracy_score'])[:5]
        
        report += "### Top Performing Queries\n\n"
        for i, query in enumerate(top_queries, 1):
            report += f"{i}. **{query['query_id']}** (Score: {query['accuracy_score']:.3f}, Time: {query['response_time']:.2f}s)\n"
            report += f"   - {query['query']}\n\n"
        
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
## Final Assessment

**Decision:** {assessment['go_no_go_decision']}

"""
    
    if assessment['go_no_go_decision'] == "GO":
        report += "✅ **System is ready for production rollout.**\n\n"
    elif assessment['go_no_go_decision'] == "CONDITIONAL_GO":
        report += "⚠️ **System is ready with conditions.**\n\n"
    else:
        report += "❌ **System is not ready for production rollout.**\n\n"
    
    report += f"""
## Lead Engineer Recommendations

Based on this verification, as a lead engineer, I recommend:

1. **Immediate Actions:**
   - Address all critical issues before any deployment
   - Implement comprehensive monitoring and alerting
   - Establish clear rollback procedures

2. **Short-term (1-2 weeks):**
   - Improve query accuracy through better document processing
   - Optimize response times through caching and resource scaling
   - Complete Perplexity integration if not available

3. **Medium-term (1-2 months):**
   - Implement automated testing and CI/CD pipeline
   - Establish operational procedures and team training
   - Plan for gradual traffic migration

4. **Long-term (3-6 months):**
   - Continuous performance optimization
   - Advanced monitoring and analytics
   - Capacity planning and scaling strategies

---

*Report generated on {datetime.utcnow().isoformat()}*
"""
    
    return report

if __name__ == "__main__":
    asyncio.run(main())