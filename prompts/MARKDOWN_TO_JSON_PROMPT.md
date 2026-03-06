Convert the provided security or intelligence report into canonical Metis Report Engine JSON.

Requirements:
- Output only valid JSON
- Follow schema/metis_report.schema.json
- Preserve all findings, evidence references, metrics, and recommendations when they exist
- Normalize narrative prose into structured fields where possible
- Do not hallucinate unsupported evidence or recommendations
- If a value is unknown, use null or omit the optional field
