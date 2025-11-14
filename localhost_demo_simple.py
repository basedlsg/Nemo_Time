#!/usr/bin/env python3
"""
Simple localhost web demo for enhanced query construction with REAL Perplexity API integration
Run this and visit http://localhost:8000 in your browser
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import requests
from lib.intent_detection import build_enhanced_query

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Query Construction Demo with Perplexity</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 32px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 16px; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-weight: 600;
        }
        .result {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            display: none;
        }
        .result.show { display: block; }
        .result h3 { color: #333; margin-bottom: 15px; font-size: 20px; }
        .result-item {
            margin-bottom: 15px;
            padding: 12px;
            background: white;
            border-radius: 6px;
        }
        .result-label {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .result-value {
            color: #333;
            word-wrap: break-word;
        }
        .intent-badge {
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 14px;
            margin-right: 8px;
        }
        .type-badge {
            display: inline-block;
            padding: 6px 16px;
            background: #28a745;
            color: white;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 600;
        }
        .type-badge.generic { background: #6c757d; }
        .search-results {
            margin-top: 20px;
        }
        .search-result-item {
            padding: 15px;
            background: white;
            border-radius: 8px;
            margin-bottom: 12px;
            border-left: 3px solid #667eea;
        }
        .search-result-item a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            word-break: break-all;
        }
        .search-result-item a:hover {
            text-decoration: underline;
        }
        .answer-section {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            line-height: 1.8;
        }
        .error {
            background: #fee;
            border-left: 4px solid #f44;
            padding: 15px;
            border-radius: 8px;
            color: #c33;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Enhanced Query Construction Demo with Perplexity API</h1>
        <p class="subtitle">Test intent-based query enhancement with REAL Perplexity search results</p>
        
        <form id="queryForm">
            <div class="form-group">
                <label for="query">Query (查询):</label>
                <input type="text" id="query" name="query" 
                       placeholder="例如: 什么是光伏发电? 或 光伏项目需要什么材料?" 
                       required>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label for="province">Province (省份):</label>
                    <select id="province" name="province">
                        <option value="gd">广东省 (Guangdong)</option>
                        <option value="sd">山东省 (Shandong)</option>
                        <option value="nm">内蒙古自治区 (Inner Mongolia)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="asset">Asset Type (资产类型):</label>
                    <select id="asset" name="asset">
                        <option value="solar">光伏发电 (Solar)</option>
                        <option value="wind">风力发电 (Wind)</option>
                        <option value="coal">煤电 (Coal)</option>
                    </select>
                </div>
            </div>
            
            <button type="submit">Enhance Query</button>
        </form>
        
        <div class="result" id="result">
            <h3>📊 Results</h3>
            <div class="result-item">
                <div class="result-label">Original Query:</div>
                <div class="result-value" id="originalQuery"></div>
            </div>
            <div class="result-item">
                <div class="result-label">Enhanced Query:</div>
                <div class="result-value" id="enhancedQuery"></div>
            </div>
            <div class="result-item">
                <div class="result-label">Intents Detected:</div>
                <div class="result-value" id="intents"></div>
            </div>
            <div class="result-item">
                <div class="result-label">Enhancement Type:</div>
                <div class="result-value" id="enhancementType"></div>
            </div>
            <div class="result-item">
                <div class="result-label">Document Keywords:</div>
                <div class="result-value" id="docKeywords"></div>
            </div>
            <div class="result-item">
                <div class="result-label">Province & Asset:</div>
                <div class="result-value" id="provinceAsset"></div>
            </div>
            
            <div id="perplexitySection" style="display:none;">
                <h3 style="margin-top: 25px; margin-bottom: 15px;">🔍 Perplexity Search Results</h3>
                <div id="answerSection" class="answer-section"></div>
                <div id="searchResults" class="search-results"></div>
            </div>
        </div>
        
        <div id="loadingIndicator" class="loading" style="display:none;">
            ⏳ Searching Perplexity API for relevant documents...
        </div>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const province = document.getElementById('province').value;
            const asset = document.getElementById('asset').value;
            const submitBtn = e.target.querySelector('button[type="submit"]');
            
            // Show loading
            submitBtn.disabled = true;
            submitBtn.textContent = 'Searching...';
            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('result').classList.remove('show');
            
            try {
                const response = await fetch('/api/enhance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, province, asset })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('result').innerHTML = 
                        `<div class="error">${data.error}</div>`;
                    document.getElementById('result').classList.add('show');
                    return;
                }
                
                // Display query enhancement info
                document.getElementById('originalQuery').textContent = query;
                document.getElementById('enhancedQuery').textContent = data.enhanced_query;
                
                const intentsDiv = document.getElementById('intents');
                if (data.intents_detected && data.intents_detected.length > 0) {
                    intentsDiv.innerHTML = data.intents_detected
                        .map(intent => `<span class="intent-badge">${intent}</span>`)
                        .join('');
                } else {
                    intentsDiv.textContent = 'None detected';
                }
                
                const typeClass = data.enhancement_type === 'intent_based' ? '' : 'generic';
                document.getElementById('enhancementType').innerHTML = 
                    `<span class="type-badge ${typeClass}">${data.enhancement_type}</span>`;
                
                document.getElementById('docKeywords').textContent = 
                    data.doc_keywords_used || 'N/A (using generic keywords)';
                
                document.getElementById('provinceAsset').textContent = 
                    `${data.province_name} - ${data.asset_name}`;
                
                // Display Perplexity results
                if (data.perplexity_answer) {
                    document.getElementById('answerSection').innerHTML = 
                        `<strong>Answer:</strong><br>${data.perplexity_answer.replace(/\\n/g, '<br>')}`;
                    document.getElementById('perplexitySection').style.display = 'block';
                }
                
                if (data.search_results && data.search_results.length > 0) {
                    const resultsHTML = data.search_results.map((url, idx) => 
                        `<div class="search-result-item">
                            <strong>${idx + 1}.</strong> <a href="${url}" target="_blank">${url}</a>
                        </div>`
                    ).join('');
                    document.getElementById('searchResults').innerHTML = 
                        `<h4 style="margin-bottom: 10px;">📎 Source URLs (${data.search_results.length}):</h4>` + resultsHTML;
                } else {
                    document.getElementById('searchResults').innerHTML = 
                        '<div class="error">No URLs found in search results</div>';
                }
                
                document.getElementById('result').classList.add('show');
                
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
                document.getElementById('result').classList.add('show');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Enhance Query';
                document.getElementById('loadingIndicator').style.display = 'none';
            }
        });
    </script>
</body>
</html>"""

def call_perplexity_api(enhanced_query: str) -> dict:
    """
    Call Perplexity API with enhanced query and return results
    """
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        return {
            'error': 'PERPLEXITY_API_KEY environment variable not set. Please set it with: export PERPLEXITY_API_KEY=your_key'
        }
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'sonar-pro',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的中国能源政策研究助手。请基于官方政府文件提供准确的政策信息，并列出所有相关的官方文档URL。'
                },
                {
                    'role': 'user',
                    'content': enhanced_query
                }
            ],
            'search_recency_filter': 'month',
            'return_citations': True,
            'return_related_questions': False
        }
        
        print(f"Calling Perplexity API with query: {enhanced_query[:100]}...")
        
        resp = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if resp.status_code >= 400:
            return {
                'error': f'Perplexity API error {resp.status_code}: {resp.text[:200]}'
            }
        
        data = resp.json()
        
        # Extract answer
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Extract citations/URLs
        citations = data.get('citations', [])
        
        print(f"Perplexity returned {len(citations)} citations")
        
        return {
            'answer': answer,
            'citations': citations,
            'success': True
        }
        
    except requests.exceptions.Timeout:
        return {'error': 'Perplexity API request timed out'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/enhance':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                query = data.get('query', '')
                province = data.get('province', 'gd')
                asset = data.get('asset', 'solar')
                
                # Step 1: Build enhanced query with intent detection
                query_enhancement = build_enhanced_query(query, province, asset)
                enhanced_query = query_enhancement['enhanced_query']
                
                # Step 2: Call Perplexity API with enhanced query
                perplexity_result = call_perplexity_api(enhanced_query)
                
                # Step 3: Combine results
                result = {
                    **query_enhancement,
                    'perplexity_answer': perplexity_result.get('answer', ''),
                    'search_results': perplexity_result.get('citations', []),
                    'perplexity_success': perplexity_result.get('success', False)
                }
                
                if 'error' in perplexity_result:
                    result['error'] = perplexity_result['error']
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': f'Server error: {str(e)}'}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    PORT = 8000
    
    # Check for Perplexity API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    print("=" * 70)
    print("🚀 Enhanced Query Construction Demo with Perplexity API")
    print("=" * 70)
    print()
    
    if not api_key:
        print("⚠️  WARNING: PERPLEXITY_API_KEY not found!")
        print()
        print("To enable Perplexity search, set your API key:")
        print("  export PERPLEXITY_API_KEY=your_api_key_here")
        print()
        print("The demo will still show query enhancement, but won't fetch")
        print("real search results without the API key.")
        print()
    else:
        print("✅ Perplexity API key detected")
        print()
    
    print(f"Server running on http://localhost:{PORT}")
    print()
    print("Open your browser and visit: http://localhost:8000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        server.shutdown()
