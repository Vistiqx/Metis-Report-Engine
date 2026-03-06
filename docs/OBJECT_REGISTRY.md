# Object Registry

## Purpose
Define the first-class structured objects recognized by Metis Report Engine.

## Core Objects
- `Report`
- `ReportMetadata`
- `ExecutiveSummary`
- `Finding`
- `Evidence`
- `Recommendation`
- `Metric`
- `RiskModel`
- `Visualization`
- `Appendix`
- `Engagement`

## Platform-Adjacent Objects
- `Asset`
- `Control`
- `Task`
- `ThreatActor`
- `Incident`
- `Source`

## Registry Rules
1. The canonical renderer consumes structured objects, not freeform prose.
2. Findings, evidence, and recommendations must remain linkable by stable IDs.
3. New objects should be added through documented schema evolution.
4. Report types may compose different subsets of these objects but should not redefine them incompatibly.
