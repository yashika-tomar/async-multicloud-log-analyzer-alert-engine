from parser import parse_line

def test_successful_log_parsing():
    """Asserts that standard server logs decompose correctly into dictionary values."""
    raw_line = '192.168.1.10 - - [24/May/2026:13:10:00 +0000] "GET /index.html HTTP/1.1" 200'
    result = parse_line(raw_line)
    
    assert result is not None
    assert result["ip"] == "192.168.1.10"
    assert result["status"] == "200"
    assert result["method"] == "GET"
    assert result["path"] == "/index.html"

def test_critical_error_detection_values():
    """Validates anomalous signatures map values correctly for alerting conditions."""
    raw_error_line = '10.0.0.5 - - [24/May/2026:13:11:15 +0000] "POST /api/v1/login HTTP/1.1" 403'
    result = parse_line(raw_error_line)
    
    assert result is not None
    assert result["status"] == "403"

def test_corrupted_log_returns_none():
    """Ensures bad strings or garbled logs do not crash the engine and are safely ignored."""
    bad_line = "This is some random garbage log entry from an unformatted system error text."
    result = parse_line(bad_line)
    
    assert result is None