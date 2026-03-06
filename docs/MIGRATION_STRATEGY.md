# Migration Strategy

## Purpose
Define how the engine will evolve across schema and component versions.

## Strategy
1. version schemas explicitly
2. preserve compatibility within major versions
3. provide migration notes for breaking changes
4. update example fixtures alongside migrations
5. emit render manifests including schema version

## Migration Types
- DSL input migrations
- canonical report JSON migrations
- visualization contract migrations
- template / component migrations

## Rule
No breaking schema update should be introduced without:
- version increment
- migration note
- updated fixtures
