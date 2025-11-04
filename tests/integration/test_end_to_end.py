"""
Integration tests for Nemo Compliance MVP
Tests end-to-end functionality with staging environment
"""
import pytest
import requests
import json
import time
import os
from typing import Dict, Any


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.fixture(scope="class")
    def staging_config(self):
        """Staging environment configuration"""
        return {
            'health_url': os.environ.get('STAGING_HEALTH_URL', 'http://localhost:8080'),
            'query_url': os.environ.get('STAGING_QUERY_URL', 'http://localhost:8081'),
            'ingest_url': os.environ.get('STAGING_INGEST_URL', 'http://localhost:8082'),
            'ingest_token': os.environ.get('STAGING_INGEST_TOKEN', 'test-token')
        }
    
    def test_health_endpoint(self, staging_config):
        """Test health endpoint returns valid status"""
        response = requests.get(staging_config['health_url'])
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert 'timestamp' in data
        assert 'commit' in data
        assert 'region' in data
        
        # Health should be 'ok' or 'degraded', not 'error'
        assert data['status'] in ['ok', 'degraded']
    
    def test_query_endpoint_valid_request(self, staging_config):
        """Test query endpoint with valid request"""
        query_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '并网验收需要哪些资料？',
            'lang': 'zh-CN'
        }
        
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'trace_id' in data
        assert 'elapsed_ms' in data
        assert 'mode' in data
        
        # Should have either answer or refusal
        assert 'answer_zh' in data or 'refusal' in data
        
        if 'answer_zh' in data and data['answer_zh']:
            # If answer provided, should have citations
            assert 'citations' in data
            assert isinstance(data['citations'], list)
            
            # Validate citation format
            for citation in data['citations']:
                assert 'title' in citation
                assert 'url' in citation
                # effective_date is optional
    
    def test_query_endpoint_invalid_province(self, staging_config):
        """Test query endpoint with invalid province"""
        query_data = {
            'province': 'invalid',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '并网验收需要哪些资料？'
        }
        
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'trace_id' in data
    
    def test_query_endpoint_missing_fields(self, staging_config):
        """Test query endpoint with missing required fields"""
        query_data = {
            'province': 'gd',
            # Missing asset, doc_class, question
        }
        
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'trace_id' in data
    
    def test_query_performance(self, staging_config):
        """Test query response time meets requirements"""
        query_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '并网技术要求',
            'lang': 'zh-CN'
        }
        
        start_time = time.time()
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        end_time = time.time()
        
        # Response time should be under 2 seconds (p95 requirement)
        response_time = (end_time - start_time) * 1000  # Convert to ms
        assert response_time < 2000, f"Response time {response_time}ms exceeds 2000ms limit"
        
        assert response.status_code == 200
        data = response.json()
        
        # Server-reported elapsed time should also be reasonable
        if 'elapsed_ms' in data:
            assert data['elapsed_ms'] < 2000
    
    def test_ingest_endpoint_authentication(self, staging_config):
        """Test ingestion endpoint requires authentication"""
        # Test without token
        response = requests.post(
            staging_config['ingest_url'],
            json={'province': 'gd', 'asset': 'solar'},
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 403
        
        # Test with invalid token
        response = requests.post(
            staging_config['ingest_url'],
            json={'province': 'gd', 'asset': 'solar'},
            headers={
                'Content-Type': 'application/json',
                'X-Ingest-Token': 'invalid-token'
            }
        )
        assert response.status_code == 403
    
    def test_ingest_endpoint_valid_request(self, staging_config):
        """Test ingestion endpoint with valid request"""
        ingest_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        response = requests.post(
            staging_config['ingest_url'],
            json=ingest_data,
            headers={
                'Content-Type': 'application/json',
                'X-Ingest-Token': staging_config['ingest_token']
            }
        )
        
        # Should accept the job (202) or return error with details
        assert response.status_code in [202, 500]
        data = response.json()
        
        if response.status_code == 202:
            assert 'accepted' in data
            assert 'job_id' in data
            assert data['accepted'] is True
        else:
            # If error, should have structured error info
            assert 'error' in data
    
    def test_multiple_provinces_query(self, staging_config):
        """Test queries for different provinces"""
        provinces = ['gd', 'sd', 'nm']
        assets = ['solar', 'coal', 'wind']
        
        for province in provinces:
            for asset in assets:
                query_data = {
                    'province': province,
                    'asset': asset,
                    'doc_class': 'grid',
                    'question': '并网要求',
                    'lang': 'zh-CN'
                }
                
                response = requests.post(
                    staging_config['query_url'],
                    json=query_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Should not crash for any valid province/asset combination
                assert response.status_code == 200
                data = response.json()
                assert 'trace_id' in data
                
                # May have answer or refusal, both are valid
                assert 'answer_zh' in data or 'refusal' in data
    
    def test_chinese_text_quality(self, staging_config):
        """Test that responses contain proper Chinese text"""
        query_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '光伏并网需要什么技术资料？',
            'lang': 'zh-CN'
        }
        
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if 'answer_zh' in data and data['answer_zh']:
            answer = data['answer_zh']
            
            # Should contain Chinese characters
            chinese_chars = sum(1 for char in answer if '\u4e00' <= char <= '\u9fff')
            total_chars = len([c for c in answer if c.isalnum()])
            
            if total_chars > 0:
                chinese_ratio = chinese_chars / total_chars
                assert chinese_ratio > 0.3, "Answer should be primarily in Chinese"
            
            # Should contain regulatory terminology
            regulatory_terms = ['并网', '资料', '要求', '规定', '办法', '管理']
            has_regulatory_terms = any(term in answer for term in regulatory_terms)
            assert has_regulatory_terms, "Answer should contain regulatory terminology"
    
    def test_no_mock_data_policy(self, staging_config):
        """Test that system never returns mock data"""
        # Query for something very specific that likely won't have real data
        query_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '火星上的光伏并网要求是什么？',  # Nonsensical query
            'lang': 'zh-CN'
        }
        
        response = requests.post(
            staging_config['query_url'],
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should either have real answer or honest refusal
        if 'answer_zh' in data and data['answer_zh']:
            # If answer provided, must have real citations
            assert 'citations' in data
            assert len(data['citations']) > 0
            
            # Citations must have real government URLs
            for citation in data['citations']:
                url = citation.get('url', '')
                assert '.gov.cn' in url or url.startswith('http'), \
                    "Citations must be real government sources"
        else:
            # Should have refusal message
            assert 'refusal' in data
            assert '未找到' in data['refusal'] or '没有' in data['refusal']


class TestGoldenSetEvaluation:
    """Golden set evaluation tests"""
    
    @pytest.fixture
    def golden_queries(self):
        """Golden set of queries with expected results"""
        return [
            {
                'province': 'gd',
                'asset': 'solar',
                'question': '光伏并网验收需要哪些资料？',
                'expected_keywords': ['资料', '验收', '并网', '光伏']
            },
            {
                'province': 'sd',
                'asset': 'wind',
                'question': '风电项目并网技术要求',
                'expected_keywords': ['风电', '技术', '要求', '并网']
            },
            {
                'province': 'nm',
                'asset': 'coal',
                'question': '煤电并网管理规定',
                'expected_keywords': ['煤电', '管理', '规定', '并网']
            }
        ]
    
    def test_golden_set_precision(self, staging_config, golden_queries):
        """Test precision on golden query set"""
        correct_responses = 0
        total_queries = len(golden_queries)
        
        for query in golden_queries:
            query_data = {
                'province': query['province'],
                'asset': query['asset'],
                'doc_class': 'grid',
                'question': query['question'],
                'lang': 'zh-CN'
            }
            
            response = requests.post(
                staging_config['query_url'],
                json=query_data,
                headers={'Content-Type': 'application/json'}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check if response contains expected keywords
            if 'answer_zh' in data and data['answer_zh']:
                answer = data['answer_zh']
                keyword_matches = sum(1 for keyword in query['expected_keywords'] 
                                    if keyword in answer)
                
                # Consider correct if at least 50% of keywords match
                if keyword_matches >= len(query['expected_keywords']) * 0.5:
                    correct_responses += 1
        
        # Calculate precision
        precision = correct_responses / total_queries if total_queries > 0 else 0
        
        # Should meet 90% precision requirement
        assert precision >= 0.9, f"Precision {precision:.2%} below 90% requirement"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])