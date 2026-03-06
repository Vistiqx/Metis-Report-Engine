# Metis Report Engine - Build Phase Checklist

## Phase Status Overview

| Phase | Description | Status | Commit Message |
|-------|-------------|--------|----------------|
| 0 | Repository Audit and Plan | ✅ COMPLETE | phase 0 audit architecture plan and execution checklist |
| 1 | Core Compiler and Canonical Pipeline | 🔄 IN PROGRESS | phase 1 implement compiler pipeline normalization and linting |
| 2 | Schema Validation and Error Model | ⏳ PENDING | phase 2 implement schema validation and structured error model |
| 3 | Scoring Metrics Visualization Resolution | ⏳ PENDING | phase 3 implement deterministic scoring charts and visualization registry |
| 4 | Professional Consulting Template System | ⏳ PENDING | phase 4 implement branded consulting template system and themed html rendering |
| 5 | PDF Generation and Render Manifests | ⏳ PENDING | phase 5 implement robust pdf rendering and render manifests |
| 6 | API Implementation | ⏳ PENDING | phase 6 implement api endpoints for validation compilation and rendering |
| 7 | Exports Report Diff Knowledge Base | ⏳ PENDING | phase 7 implement export diff and finding knowledge base utilities |
| 8 | Quality Gates and Regression Fixes | ⏳ PENDING | phase 8 add quality gates regression coverage and hardening fixes |
| 9 | End-to-End Browser Testing | ⏳ PENDING | phase 9 complete end to end browser testing with playwright and devtools remediation |
| 10 | Final Stabilization and Delivery | ⏳ PENDING | phase 10 final stabilization documentation and delivery state |

---

## Phase 0 Checklist

- [x] Inspect all top-level directories
- [x] Read architecture and contract docs
- [x] Map repository structure
- [x] Confirm schema flow
- [x] Identify incomplete placeholder modules
- [x] Identify missing imports/package init issues
- [x] Identify template dependencies
- [x] Create BUILD_EXECUTION_LOG.md
- [x] Create BUILD_PHASE_CHECKLIST.md

---

## Phase 1 Checklist

### Core Compiler Implementation
- [ ] Complete dsl_compiler.py with full DSL parsing
- [ ] Complete report_normalizer.py with all normalization rules
- [ ] Complete finding_expander.py with reference resolution
- [ ] Complete visualization_resolver.py
- [ ] Complete compiler_pipeline.py orchestration
- [ ] Fix visualization registry imports (svg_charts.py missing functions)

### Testing
- [ ] Add unit tests for DSL block parsing
- [ ] Add unit tests for multiline handling
- [ ] Add unit tests for list handling
- [ ] Add unit tests for severity normalization
- [ ] Add unit tests for finding expansion
- [ ] Add unit tests for visualization resolution
- [ ] Add unit tests for report lint warnings and errors

### Commit
- [ ] Run tests
- [ ] Fix failures
- [ ] Commit with: phase 1 implement compiler pipeline normalization and linting
- [ ] Push to GitHub

---

## Phase 2 Checklist

### Schema Validation
- [ ] Complete schema_validator.py
- [ ] Wire validation against metis_report.schema.json
- [ ] Wire validation against metis_report_dsl.schema.json
- [ ] Implement structured error envelope per ERROR_MODEL.md

### Testing
- [ ] Test valid canonical JSON passes
- [ ] Test invalid canonical JSON fails with structured error
- [ ] Test valid DSL passes
- [ ] Test invalid DSL fails with structured error
- [ ] Test broken references fail
- [ ] Test malformed block inputs fail cleanly

### Commit
- [ ] Run tests
- [ ] Commit with: phase 2 implement schema validation and structured error model
- [ ] Push to GitHub

---

## Phase 3 Checklist

### Scoring and Visualizations
- [ ] Complete risk_calculator.py
- [ ] Wire scoring into compiler pipeline
- [ ] Complete svg_charts.py (add missing functions)
- [ ] Complete risk_matrix.py
- [ ] Complete chart_registry.py
- [ ] Complete chart_cache.py
- [ ] Add risk trend support

### Testing
- [ ] Test visualization resolvers return expected definitions
- [ ] Test SVG/HTML chart outputs are deterministic
- [ ] Test cache behavior
- [ ] Test scoring outputs remain stable

### Commit
- [ ] Run tests
- [ ] Commit with: phase 3 implement deterministic scoring charts and visualization registry
- [ ] Push to GitHub

---

## Phase 4 Checklist

### Professional Consulting Template
- [ ] Complete template integration
- [ ] Integrate theme tokens
- [ ] Update html_renderer to support template selection
- [ ] Support theme profile selection
- [ ] Support visualization injection
- [ ] Support ToC generation

### Testing
- [ ] Render example reports to HTML
- [ ] Verify template selection works
- [ ] Verify theme profile selection works
- [ ] Verify no missing template includes

### Commit
- [ ] Run tests
- [ ] Commit with: phase 4 implement branded consulting template system and themed html rendering
- [ ] Push to GitHub

---

## Phase 5 Checklist

### PDF and Manifests
- [ ] Complete pdf_renderer.py
- [ ] Integrate Playwright rendering robustly
- [ ] Ensure correct print settings
- [ ] Integrate render_manifest.py
- [ ] Generate manifest alongside output
- [ ] Handle PDF failures gracefully

### Testing
- [ ] Render example canonical JSON to PDF
- [ ] Render compiled DSL to PDF
- [ ] Verify PDF files created
- [ ] Verify manifest contains expected metadata

### Commit
- [ ] Run tests
- [ ] Commit with: phase 5 implement robust pdf rendering and render manifests
- [ ] Push to GitHub

---

## Phase 6 Checklist

### API Implementation
- [ ] Complete all API routes
- [ ] Implement GET /health
- [ ] Implement POST /validate-dsl
- [ ] Implement POST /compile-dsl
- [ ] Implement POST /validate-report-json
- [ ] Implement POST /render-html
- [ ] Implement POST /render-pdf
- [ ] Ensure structured errors on failure
- [ ] Wire to real logic, not mocks

### Testing
- [ ] Unit tests for API routes
- [ ] Integration tests with FastAPI test client
- [ ] Happy path and error path coverage
- [ ] PDF endpoint returns useful metadata

### Commit
- [ ] Run tests
- [ ] Commit with: phase 6 implement api endpoints for validation compilation and rendering
- [ ] Push to GitHub

---

## Phase 7 Checklist

### Supporting Utilities
- [ ] Complete export_manager.py
- [ ] Complete report_diff.py
- [ ] Complete finding_library.py
- [ ] Support JSON, Markdown, HTML exports

### Testing
- [ ] Export tests
- [ ] Diff tests
- [ ] Knowledge base access tests

### Commit
- [ ] Run tests
- [ ] Commit with: phase 7 implement export diff and finding knowledge base utilities
- [ ] Push to GitHub

---

## Phase 8 Checklist

### Quality and Hardening
- [ ] Enforce quality gates
- [ ] Add regression fixture coverage
- [ ] Add golden-path regression tests
- [ ] Ensure linting integrates cleanly
- [ ] Add missing package init files
- [ ] Remove dead code and placeholders
- [ ] Improve logs and messages

### Testing
- [ ] Full unit test suite
- [ ] Full integration test suite
- [ ] API tests
- [ ] Render tests

### Commit
- [ ] Run tests
- [ ] Commit with: phase 8 add quality gates regression coverage and hardening fixes
- [ ] Push to GitHub

---

## Phase 9 Checklist

### End-to-End Browser Testing
- [ ] Run application locally
- [ ] Generate HTML previews from example inputs
- [ ] Use Playwright CLI to test preview loads
- [ ] Verify rendered HTML contains expected sections
- [ ] Verify charts appear
- [ ] Verify consulting template renders correctly
- [ ] Use Chrome DevTools CLI to inspect console errors
- [ ] Fix any end-to-end issues found
- [ ] Rerun until stable

### Testing
- [ ] Multiple pass verification
- [ ] Inspect failures
- [ ] Patch code
- [ ] Rerun e2e tests
- [ ] Repeat until stable

### Commit
- [ ] Run tests
- [ ] Commit with: phase 9 complete end to end browser testing with playwright and devtools remediation
- [ ] Push to GitHub

---

## Phase 10 Checklist

### Final Stabilization
- [ ] Run full tests again
- [ ] Run representative end-to-end flows
- [ ] Verify example inputs all work
- [ ] Update build log
- [ ] Ensure README explains how to run the app
- [ ] Ensure project can be started by another engineer
- [ ] Commit all changes
- [ ] Push final state to GitHub

### Success Criteria
- [ ] Repository is in stable working state
- [ ] Tests pass
- [ ] Final push attempted
- [ ] Final summary written to build log

### Commit
- [ ] Commit with: phase 10 final stabilization documentation and delivery state
- [ ] Push to GitHub

---

## Git Operations Log

| Phase | Commit Hash | Push Status | Notes |
|-------|-------------|-------------|-------|
| 0 | TBD | TBD | Initial audit and planning |

