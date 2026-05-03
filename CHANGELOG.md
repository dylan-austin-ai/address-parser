# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to it.

## [Unreleased]

### Added
- **New Agent Capabilities**: Introduced specialized agents including `api_design.py`, `ceo_review.py`, `changelog.py`, `examples.py`, `performance.py`, `planner.py`, and `performance.py`.
- **Advanced Orchestration**: Added `approval.py` for human-in-the-loop workflows and enhanced the `pipeline.py` for parallel audit fan-out.
- **Post-Quantum Security**: Integrated SPHINCS+ post-quantum artifact attestation and chain-of-custody verification tools.
- **New Documentation**: Added comprehensive Architecture Decision Records (ADRs 001-008), build guides, and detailed project-specific briefs for Phase 4.
- **Enhanced CLI**: Added `--task-file` flag to the `run-pipeline` command.
- **Spatial Intelligence**: Introduced H3 hexagonal spatial binning and Census ZCTA spatial integration capabilities.
- **Enrichment Engine**: Implemented `ZipCodeDataGenerator` for Census and HUD data integration, including population density and urbanization classification.
- **Project Templates**: Added multiple new project structures for testing (e.g., `address-parser`, `attestation-test`, `phase2-verify`).
- **Environment Management**: Added `EnvironmentManager` for adaptive batch sizing based on available system memory and hardware (CPU/GPU) detection.

### Changed
- **Core Architecture**: Transitioned to a multi-agent pipeline with enhanced memory schemas and parallel execution support.
- **Agent Logic**: Updated existing agents (`coder.py`, `documenter.py`, `legal_privacy.py`, `qa.py`, `responsible_ai.py`, `security_auditor.py`) to support Phase 4 requirements.
- **Data Processing**: Updated the orchestrator to support large-scale parallel chunk processing via `ProcessPoolExecutor`.
- **Documentation**: Updated `README.md`, `ARCHITECTURE.md`, and `CLAUDE.md` to reflect the new phased development roadmap and system capabilities.

### Fixed
- **Test Reliability**: Fixed stale test assertions in `evals/test_coder.py` and `evals/test_qa_documenter.py` following agent updates.
- **Build System**: Fixed `pyproject.toml` build backend to ensure successful `pip install -e .` execution.
- **Documentation Bugs**: Corrected prerequisites in `docs/HOW_TO_RUN_YOUR_OWN_PROJECT.md`.
- **Logic Errors**: Resolved bugs in memory schema handling and phase-specific testing routines.

### Removed
- *No breaking changes or removals reported in this version.*