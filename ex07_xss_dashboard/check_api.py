"""
Smoke test for exercise 7 — hits both dashboard routes and asserts on
the raw response text (an alert() can't be observed over plain HTTP,
so we check the markup itself).
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

RAW_SCRIPT_TAG = "<script>alert('xss1')</script>"
RAW_ATTRIBUTE_BREAKOUT = 'x" onerror="alert(\'xss2\')'
ESCAPED_SCRIPT_TAG = "&lt;script&gt;alert(&#39;xss1&#39;)&lt;/script&gt;"


def check(label: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")


def main() -> None:
    safe = requests.get(f"{BASE_URL}/dashboard")
    check("safe dashboard returns 200", safe.status_code == 200)
    check(
        "safe dashboard escapes the <script> tag as text",
        RAW_SCRIPT_TAG not in safe.text and ESCAPED_SCRIPT_TAG in safe.text,
    )
    check(
        "safe dashboard escapes the attribute breakout",
        'onerror="alert(' not in safe.text,
    )
    check(
        "safe dashboard has CSP header",
        safe.headers.get("Content-Security-Policy") == "default-src 'self'",
    )

    insecure = requests.get(f"{BASE_URL}/dashboard-inseguro")
    check("insecure dashboard returns 200", insecure.status_code == 200)
    check(
        "insecure dashboard leaks the raw <script> tag (expected, for contrast)",
        RAW_SCRIPT_TAG in insecure.text,
    )
    check(
        "insecure dashboard leaks the raw attribute breakout (expected, for contrast)",
        'onerror="alert(\'xss2\')"' in insecure.text,
    )


if __name__ == "__main__":
    main()
