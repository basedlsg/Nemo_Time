"""
Objective Committee Report Generator
Generates completely unbiased report with raw data only
"""

import json
from datetime import datetime
from pathlib import Path

def generate_objective_report(results_file):
    """Generate completely objective report with no bias or interpretation"""
    
    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# System Evaluation Data
## Independent Committee Review

**Generated:** {timestamp}  
**Data Source:** {results_file}

---

## Test Configuration

**System Under Test:** RAG-Anything framework  
**Domain:** Chinese energy regulatory compliance  
**Test Structure:** 4 difficulty tiers, 2 queries per tier  
**Total Queries:** 8

**Tier Definitions:**
- Tier 1: Basic terminology, single concept queries
- Tier 2: Province-specific, technical specifications  
- Tier 3: Multi-province coordination, regulatory complexity
- Tier 4: Policy integration, future planning, multi-objective optimization

---

## Raw Test Results

"""
    
    # Process each tier
    for tier_name, tier_results in results.items():
        tier_display = tier_name.replace("_", " ").title()
        report += f"### {tier_display}\n\n"
        
        for i, result in enumerate(tier_results, 1):
            report += f"**Test Case {i}**\n\n"
            report += f"Query ID: {result['query_id']}\n\n"
            report += f"Input Query: {result['query']}\n\n"
            report += f"Difficulty Classification: {result['difficulty']}\n\n"
            report += f"Province Parameter: {result.get('province', 'N/A')}\n\n"
            report += f"Asset Parameter: {result.get('asset', 'N/A')}\n\n"
            report += f"Response Time: {result.get('response_time', 0):.6f} seconds\n\n"
            report += f"System Response Generated: {result.get('success', False)}\n\n"
            
            if result.get('full_response'):
                report += f"System Output:\n```\n{result['full_response']}\n```\n\n"
            
            if result.get('citations'):
                report += f"Citations Provided: {len(result['citations'])}\n\n"
            
            if result.get('error'):
                report += f"Error Message: {result['error']}\n\n"
            
            report += "---\n\n"
    
    # Add raw statistics without interpretation
    total_queries = sum(len(tier_results) for tier_results in results.values())
    successful_responses = sum(1 for tier_results in results.values() 
                             for result in tier_results 
                             if result.get('success', False))
    
    report += f"""## Numerical Data Summary

Total Test Cases: {total_queries}
Responses Generated: {successful_responses}
No Response Generated: {total_queries - successful_responses}

**Response Times (seconds):**
"""
    
    # Add response time data for each query
    for tier_name, tier_results in results.items():
        tier_display = tier_name.replace("_", " ").title()
        report += f"\n{tier_display}:\n"
        for result in tier_results:
            report += f"- {result['query_id']}: {result.get('response_time', 0):.6f}s\n"
    
    report += f"""

---

## Technical Configuration

**Test Environment:**
- Framework: RAG-Anything
- Language Processing: Chinese (Simplified)
- Response Language: Chinese
- Test Date: {timestamp.split()[0]}

**Data Collection Method:**
- Automated test execution
- Response time measurement
- Output capture
- Error logging

---

*This document contains raw test data without analysis or interpretation. All measurements and outputs are presented as recorded by the test system.*
"""
    
    return report

if __name__ == "__main__":
    # Generate objective report
    results_file = "evaluation_results/tiered_evaluation_results.json"
    
    if Path(results_file).exists():
        objective_report = generate_objective_report(results_file)
        
        # Save objective report
        output_file = "evaluation_results/objective_committee_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(objective_report)
        
        print(f"Objective report generated: {output_file}")
    else:
        print(f"Results file not found: {results_file}")
        print("Please run tiered_evaluation_test.py first to generate test data.")