# Roadmap

## v0.1 — MVP
- [x] Core directory structure and toolchain operational
- [x] Environment config loading via pydantic-settings
- [x] Basic Anthropic SDK integration with error handling
- [x] MCP client stub with Pydantic validation
- [x] GPIO abstraction layer (hardware-conditional)
- [x] ≥1 passing end-to-end test

## v0.2 — Hardening
- [ ] Coverage ≥90% on all core modules
- [ ] Pre-commit hooks passing cleanly
- [ ] mypy strict passing cleanly
- [ ] All secrets validated as present at startup
- [ ] Structured logging wired throughout
- [ ] README complete and accurate

## v1.0 — Production-Ready
- [ ] Cloud deployment configuration (Dockerfile or equivalent)
- [ ] CI pipeline (GitHub Actions or equivalent)
- [ ] Security audit passing (bandit + pip-audit clean)
- [ ] Full documentation in docs/
- [ ] CHANGELOG reflects all meaningful changes
