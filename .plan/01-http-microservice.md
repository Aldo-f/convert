# convert — HTTP Microservice Plan

## Task: HTTP Microservice

## Goal
Expose `convert` as a local HTTP service that accepts POST requests with conversion requests and returns converted files.

## Scope (IN)
- HTTP server listening on `localhost:8080`
- POST endpoint `/convert` accepting JSON: `{ "source": "path", "format": "md", "target": "out.txt" }`
- GET endpoint `/health` returning `200 OK` with status
- All conversion logic reused from existing CLI
- No new dependencies beyond Python stdlib + existing convert dependencies

## Scope (OUT)
- Any external network access
- HTTP server running on port 8080 (configurable later)
- File system operations beyond the current CLI scope (e.g. different paths)
- Authentication, TLS, rate limiting, or any security features

## TDD Approach
1. Write tests for HTTP endpoints using `pytest` + `requests`
2. Implement minimal server (Flask/FastAPI) to satisfy tests
3. Add tests for edge cases (invalid JSON, missing fields, etc.)
4. Verify with manual curl tests

## Acceptance Criteria
- `curl -X POST -H "Content-Type: application/json" -d '{"source": "test.txt", "format": "md", "target": "out.md"}' http://localhost:8080/convert` returns 200 with converted file content
- `curl http://localhost:8080/health` returns 200 with "OK"
- All existing convert tests still pass
- No new test failures introduced

## Validation Steps
1. Run `pytest tests/test_http.py` (new test file)
2. Run `python -m convert.cli --help` to verify CLI still works
3. Verify HTTP endpoints with curl commands

## Dependencies
- Python 3.12+
- `fastapi` or `flask` (choose one based on existing dependencies)
- `uvicorn` or `gunicorn` for serving (if needed)

## Dependencies NOT included
- Authentication
- TLS/HTTPS
- Database
- Authentication tokens
- External API calls

## Implementation Notes
- Use existing `convert.convert()` function from CLI
- Return converted file content as JSON response with `Content-Type: application/json`
- Handle file reading/writing inside the service, not in CLI

## Dependencies to Install
- `fastapi`
- `uvicorn` (or `gunicorn`)
- `python-multipart` (if needed for file uploads)

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
python -m pytest tests/test_http.py -q
python -m convert.cli --help
curl http://localhost:8080/health
```

## Notes
- Start with minimal implementation: just the `/convert` endpoint for text conversions
- Add video/audio support later if needed
- Use environment variables for port configuration (default 8080)