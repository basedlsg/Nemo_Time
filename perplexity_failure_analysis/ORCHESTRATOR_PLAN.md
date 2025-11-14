# Perplexity Search Quality Failure - Orchestrated Analysis Plan

## Mission
Conduct comprehensive root cause analysis of why Perplexity API returned 89% irrelevant results (17/19) for a Guangdong solar land survey query despite intent-based query enhancement.

## Orchestration Structure

### Chief Analysis Agent (Orchestrator)
**Role**: Coordinate parallel investigations, synthesize findings, produce actionable recommendations

### Specialized Analysis Agents

#### Agent 1: Query Construction Analyzer
**Focus**: Examine how the enhanced query was built
- Review intent detection output
- Verify keyword injection
- Check site restriction syntax
- Validate province/asset mapping

#### Agent 2: Perplexity API Behavior Analyst
**Focus**: Understand Perplexity's actual search behavior
- Analyze API request payload
- Review API response structure
- Test if `site:.gov.cn` is honored
- Check if Chinese keywords affect ranking

#### Agent 3: Search Result Quality Evaluator
**Focus**: Deep analysis of the 19 returned sources
- Categorize failure types (wrong province, wrong topic, wrong domain)
- Identify patterns in irrelevant results
- Calculate relevance distribution
- Find any salvageable sources

#### Agent 4: Intent Detection Validator
**Focus**: Verify intent detection worked correctly
- Confirm "materials" and "procedure" were detected
- Check if correct keywords were mapped
- Validate keyword selection logic
- Test alternative intent combinations

#### Agent 5: Comparative Search Strategist
**Focus**: Benchmark against alternative approaches
- Compare with direct Google CSE results
- Test alternative query formulations
- Evaluate different Perplexity models
- Assess search recency filter impact

#### Agent 6: Root Cause Synthesizer
**Focus**: Integrate all findings into root cause determination
- Identify primary failure point
- Determine if issue is query construction or API behavior
- Assess if Perplexity is suitable for this use case
- Recommend immediate fixes

## Deliverables

### 1. Individual Agent Reports
Each agent produces detailed analysis in their domain

### 2. Integrated Root Cause Report
Synthesized findings with evidence-based conclusions

### 3. Action Plan
Prioritized fixes with implementation steps

### 4. Alternative Strategy Recommendations
If Perplexity proves unsuitable, propose alternatives

## Timeline
- Agent analyses: Parallel execution
- Synthesis: Sequential after all agents complete
- Final report: Comprehensive with executive summary
