"""Diagnostic script to test the exact same payload as PowerShell script.

This script mimics exactly what the PowerShell test does to help diagnose
any discrepancies between local testing and PowerShell testing.
"""
import json
import requests
from pathlib import Path

def diagnose_production_test():
    """Diagnose the production test scenario."""
    
    # Load the exact same fixture file
    fixture_path = Path(__file__).parents[1] / "examples" / "reports" / "meta-ai-glasses-risk-assessment.example.json"
    
    print("=" * 70)
    print("DIAGNOSTIC: Production Test Scenario")
    print("=" * 70)
    print(f"\nFixture path: {fixture_path}")
    print(f"Fixture exists: {fixture_path.exists()}")
    print(f"Fixture size: {fixture_path.stat().st_size} bytes")
    
    # Load and inspect the fixture
    with open(fixture_path) as f:
        report = json.load(f)
    
    print(f"\nFixture top-level keys: {list(report.keys())}")
    print(f"report.id: {report['report'].get('id')}")
    print(f"report.type: {report['report'].get('type')}")
    print(f"engagement.id: {report['engagement'].get('id')}")
    print(f"engagement.scope_summary present: {'scope_summary' in report['engagement']}")
    print(f"findings count: {len(report.get('findings', []))}")
    print(f"evidence count: {len(report.get('evidence', []))}")
    print(f"recommendations count: {len(report.get('recommendations', []))}")
    print(f"visualizations count: {len(report.get('visualizations', []))}")
    
    # Check each finding for domain
    print("\n--- Finding domain check ---")
    for finding in report.get('findings', []):
        has_domain = 'domain' in finding
        print(f"  {finding['id']}: has domain = {has_domain}, value = {finding.get('domain', 'MISSING')}")
    
    # Check each evidence for domain
    print("\n--- Evidence domain check ---")
    for evidence in report.get('evidence', []):
        has_domain = 'domain' in evidence
        print(f"  {evidence['id']}: has domain = {has_domain}, value = {evidence.get('domain', 'MISSING')}")
    
    # Check each recommendation for domain and action
    print("\n--- Recommendation domain + action check ---")
    for rec in report.get('recommendations', []):
        has_domain = 'domain' in rec
        has_action = 'action' in rec and rec['action'] is not None
        action_type = rec['action'].get('type', 'MISSING') if has_action else 'N/A'
        has_action_desc = has_action and 'description' in rec['action']
        print(f"  {rec['id']}: domain={has_domain}, action={has_action}, action.type={action_type}, action.desc={has_action_desc}")
    
    # Check visualizations
    print("\n--- Visualization type check ---")
    valid_types = ["kpi_cards", "severity_distribution", "risk_matrix", 
                  "financial_exposure_chart", "comparison_bar_chart", "timeline", 
                  "recommendation_priority", "appendix_table"]
    for viz in report.get('visualizations', []):
        is_valid = viz['type'] in valid_types
        print(f"  {viz['id']}: type={viz['type']}, valid={is_valid}")
    
    # Check appendices
    print("\n--- Appendix content check ---")
    for app in report.get('appendices', []):
        has_content = 'content' in app and app['content']
        print(f"  \"{app.get('title', 'Untitled')}\": content present = {has_content}")
    
    # Now test with the server
    print("\n" + "=" * 70)
    print("TESTING AGAINST DEV SERVER")
    print("=" * 70)
    
    server_url = "http://192.168.239.197:8000"
    print(f"\nServer URL: {server_url}")
    
    # Test health
    print("\n1. Health check...")
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test validation with wrapped payload (production shape)
    print("\n2. Validation with wrapped payload (production shape)...")
    wrapped_payload = {"report": report}
    print(f"   Payload keys: {list(wrapped_payload.keys())}")
    print(f"   Wrapped report keys: {list(wrapped_payload['report'].keys())}")
    
    try:
        response = requests.post(
            f"{server_url}/validate-report-json",
            json=wrapped_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Response status: {response.status_code}")
        result = response.json()
        print(f"   Valid: {result.get('valid')}")
        print(f"   Status: {result.get('status')}")
        
        if not result.get('valid') and 'error' in result:
            print(f"   ERROR DETAILS:")
            print(f"   Code: {result['error'].get('code')}")
            print(f"   Message: {result['error'].get('message')}")
            print(f"   Number of errors: {len(result['error'].get('details', []))}")
            for i, err in enumerate(result['error'].get('details', [])[:10]):
                path = '.'.join(str(p) for p in err.get('path', [])) if err.get('path') else 'root'
                print(f"     {i+1}. {path}: {err.get('message')}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test PDF render (includes quality gates)
    print("\n3. PDF render (includes quality gates)...")
    try:
        response = requests.post(
            f"{server_url}/render-pdf",
            json={"report": report, "template": "professional"},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"   Response status: {response.status_code}")
        result = response.json()
        print(f"   Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"   PDF path: {result.get('pdf_path')}")
            print(f"   PDF size: {result.get('pdf_size')} bytes")
            print("   SUCCESS!")
        else:
            print(f"   FAILED!")
            detail = result.get('detail', {})
            if isinstance(detail, dict):
                print(f"   Message: {detail.get('message')}")
                if 'quality_gates' in detail:
                    print(f"   Quality gates passed: {detail['quality_gates'].get('passed')}")
                    print(f"   Error count: {detail['quality_gates'].get('error_count')}")
                    for err in detail['quality_gates'].get('errors', []):
                        print(f"     - {err.get('gate')}: {err.get('message')}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_production_test()
