# Implementation Notes

## Why use a DSL?
Raw JSON is rigid for AI and unpleasant for humans to review. The DSL gives the model a constrained authoring surface while preserving deterministic compilation.

## Parser strategy
1. Read Markdown file.
2. Extract fenced code blocks whose info string matches an allowed block type.
3. Parse block body as YAML.
4. Validate each block by block-type rules.
5. Compile into canonical JSON.
6. Validate compiled JSON against the Metis Report Engine schema bundle.

## Recommended parser outputs
- compiled JSON
- validation errors
- unresolved references
- warnings about missing optional but recommended fields

## Future Metis compatibility
Metis can later accept:
- raw canonical JSON
- DSL documents
- UI-authored objects

All roads should converge on the same canonical schema.
