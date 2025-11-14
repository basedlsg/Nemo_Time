# Enhanced Query Construction Demo with Perplexity API Integration

## What This Does

This demo now **actually calls the Perplexity API** to get real search results with links to government documents. It's not just showing you the enhanced query anymore - it's using that query to fetch real results!

## Features

✅ **Intent Detection** - Detects query intents (materials, procedure, approval, etc.)  
✅ **Smart Keywords** - Adds targeted Chinese document keywords based on detected intents  
✅ **Province & Asset Context** - Includes province and asset type in the search  
✅ **Real Perplexity Search** - Actually calls Perplexity API and returns results  
✅ **Live URLs** - Shows actual government document URLs from search results  
✅ **Answer Generation** - Displays Perplexity's answer based on found documents  

## Setup

### 1. Get Your Perplexity API Key

You need a Perplexity API key. Get one at: https://www.perplexity.ai/settings/api

### 2. Set the Environment Variable

```bash
export PERPLEXITY_API_KEY=your_api_key_here
```

### 3. Run the Demo

```bash
python3 localhost_demo_simple.py
```

### 4. Open Your Browser

Visit: http://localhost:8000

## How It Works

### Before (What You Saw)
```
Query: 光伏发电项目土地勘测需要什么材料和流程
↓
Enhanced Query: 光伏发电项目土地勘测需要什么材料和流程 广东省 光伏发电 材料清单 申请指南...
↓
[STOPPED HERE - No actual search]
```

### Now (What Happens)
```
Query: 光伏发电项目土地勘测需要什么材料和流程
↓
Enhanced Query: 光伏发电项目土地勘测需要什么材料和流程 广东省 光伏发电 材料清单 申请指南...
↓
Perplexity API Call with Enhanced Query
↓
Real Search Results with URLs:
  1. http://drc.gd.gov.cn/solar_materials_guide_2024.pdf
  2. http://nea.gov.cn/policy/solar_survey_requirements.pdf
  3. http://gd.csg.cn/procedures/land_survey_process.pdf
↓
Answer: Based on official documents, the materials required include...
```

## What You'll See

### Query Enhancement Section
- Original query
- Enhanced query with keywords
- Detected intents (materials, procedure, etc.)
- Enhancement type (intent_based or generic)
- Document keywords used
- Province & asset context

### Perplexity Search Results Section (NEW!)
- **Answer**: Perplexity's generated answer based on found documents
- **Source URLs**: List of actual government document URLs
- **Citation count**: How many sources were found

## Example Queries to Try

### Chinese Queries (Best Results)
```
光伏发电项目土地勘测需要什么材料和流程？
风电项目并网需要哪些审批文件？
煤电项目环评流程是什么？
分布式光伏装机容量限制标准？
```

### English Queries (Will use generic enhancement)
```
What are the requirements for solar project approval?
How to connect wind power to the grid?
```

## Troubleshooting

### "PERPLEXITY_API_KEY environment variable not set"
- You forgot to set the API key
- Run: `export PERPLEXITY_API_KEY=your_key`

### "No URLs found in search results"
- The query might be too vague
- Try a more specific Chinese regulatory query
- Check if your API key is valid

### "Perplexity API error 401"
- Your API key is invalid or expired
- Get a new key from Perplexity settings

### "Request timed out"
- Network issue or Perplexity API is slow
- Try again in a moment

## Technical Details

### API Call Flow
1. User submits query in browser
2. Backend builds enhanced query using intent detection
3. Backend calls Perplexity API with enhanced query
4. Perplexity searches and returns answer + citations
5. Frontend displays both query enhancement and search results

### Perplexity API Configuration
- **Model**: `sonar-pro` (best for search)
- **Search Recency**: Last month
- **Return Citations**: Enabled
- **Timeout**: 30 seconds

### Intent Detection Keywords
The system detects these intents and adds corresponding keywords:
- **definition** → 定义, 概念, 含义
- **materials** → 材料清单, 申请指南, 所需材料
- **procedure** → 实施细则, 操作指南, 办理流程
- **approval** → 审批流程, 核准程序, 备案要求
- **timeline** → 时间要求, 办理期限, 审批时限
- And more...

## Next Steps

This demo proves the integration works. To use this in production:

1. ✅ Intent detection is working
2. ✅ Query enhancement is working  
3. ✅ Perplexity API integration is working
4. ✅ Real URLs are being returned

Now you can integrate this into your main RAG system!
