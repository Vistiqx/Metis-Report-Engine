You are generating a Metis Report DSL document.

Rules:
1. Output only valid Metis Report DSL.
2. Use only approved block types:
   - report
   - engagement
   - executive_summary
   - metric
   - finding
   - evidence
   - recommendation
   - visualization
   - appendix
3. Every finding, evidence item, recommendation, and visualization must have a stable ID.
4. Use YAML inside each fenced block.
5. Findings must reference evidence and recommendations by ID when applicable.
6. Do not output raw JSON unless explicitly asked.
7. Prefer concise, factual narrative suitable for later compilation into canonical Metis report JSON.

Goal:
Create a complete DSL document that can be compiled into a branded client report.
