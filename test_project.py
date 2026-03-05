import requests, json

desc = """Many residential and commercial solar installations operate below optimal efficiency due to panel misalignment, dust accumulation, temperature variations, or inverter faults. Currently, users often lack real-time monitoring tools to track system performance. A smart monitoring system is required to measure voltage, current, power output, and environmental conditions, analyze efficiency, and notify users of faults or performance drops to maximize renewable energy utilization."""

r = requests.post('http://localhost:5000/api/project/analyze', json={'description': desc})
data = r.json()

print("=== Analysis ===")
print(json.dumps(data.get('analysis'), indent=2))
print(f"\nTotal matches: {data.get('total_matches', 0)}")
print("\nTop 5 professors:")
for p in data.get('professors', [])[:5]:
    print(f"  {p['name']} ({p['college']}) - {p['match_percentage']}% match - domains: {p.get('matching_domains', [])}")
