# Changelog

## [0.2.0] - 2026-05-15

### Added
- Inline code comment tool (`add_inline_comment`)
- General MR comment tool (`add_mr_comment`)
- File content retrieval with sensitive data masking
- Retry logic for inline comments (tries nearby lines)
- Content-Type header fix for GitLab discussions API

### Changed
- Updated system prompt to instruct agent to post comments
- Improved error handling with response body in error messages

## [0.1.0] - 2026-05-10

### Added
- Initial agent with LangGraph
- MR details fetching
- MR changes/diff fetching
- OpenAI GPT-4o integration
- SSL bypass for corporate proxy (xyz)
