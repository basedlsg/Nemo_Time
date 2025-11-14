#!/usr/bin/env python3
"""
Localhost web demo for enhanced query construction with intent detection
Run this and visit http://localhost:5000 in your browser
"""

from flask import Flask, render_template_string, request, jsonify
from lib.intent_detection import build_enhanced_query
import sys

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Query Construction Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }
        .form-group {
            margin-bottom: 20px;
        }
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
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            display: none;
        }
        .result.show {
            display: block;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .result h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
        }
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
            margin-bottom: 8px;
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
        .type-badge.generic {
            background: #6c757d;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .loading.show {
            display: block;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Enhanced Query Construction Demo</h1>
        <p class="subtitle">Test intent-based query enhancement for Chinese regulatory queries</p>
        
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
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Processing...</p>
        </div>
        
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
        </div>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const province = document.getElementById('province').value;
            const asset = document.getElementById('asset').value;
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('result').classList.remove('show');
            
            try {
                const response = await fetch('/enhance', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query, province, asset })
                });
                
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').classList.remove('show');
                
                // Display results
                document.getElementById('originalQuery').textContent = query;
                document.getElementById('enhancedQuery').textContent = data.enhanced_query;
                
                // Display intents as badges
                const intentsDiv = document.getElementById('intents');
                if (data.intents_detected.length > 0) {
                    intentsDiv.innerHTML = data.intents_detected
                        .map(intent => `<span class="intent-badge">${intent}</span>`)
                        .join('');
                } else {
                    intentsDiv.textContent = 'None detected';
                }
                
                // Display enhancement type
                const typeClass = data.enhancement_type === 'intent_based' ? '' : 'generic';
                document.getElementById('enhancementType').innerHTML = 
                    `<span class="type-badge ${typeClass}">${data.enhancement_type}</span>`;
                
                // Display document keywords
                document.getElementById('docKeywords').textContent = 
                    data.doc_keywords_used || 'N/A (using generic keywords)';
                
                // Display province and asset
                document.getElementById('provinceAsset').textContent = 
                    `${data.province_name} - ${data.asset_name}`;
                
                // Show result
                document.getElementById('result').classList.add('show');
                
            } catch (error) {
                document.getElementById('loading').classList.remove('show');
                alert('Error: ' + error.message);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/enhance', methods=['POST'])
def enhance():
    try:
        data = request.json
        query = data.get('query', '')
        province = data.get('province', 'gd')
        asset = data.get('asset', 'solar')
        
        result = build_enhanced_query(query, province, asset)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Enhanced Query Construction Demo Server")
    print("=" * 70)
    print()
    print("Server starting on http://localhost:5000")
    print()
    print("Open your browser and visit: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
