import requests
import json

# Base URL for the backend API
BASE_URL = "http://localhost:5000/analyze"

# Test cases for edge case analysis
TEST_CASES = [
    # Empty input
    {"name": "Empty Input", "input": "", "expected_status": 400, "expected_error": "No message provided"},

    # Extremely long input
    {"name": "Extremely Long Input", "input": "a" * 10001, "expected_status": 200},

    # Special characters
    {"name": "Special Characters", "input": "!@#$%^&*()_+=-[]{}|;:'\",.<>?/`~", "expected_status": 200},

    # Non-English input
    {"name": "Non-English Input (Chinese)", "input": "您的账户已被锁定", "expected_status": 200},
    {"name": "Non-English Input (Arabic)", "input": "تم قفل حسابك", "expected_status": 200},
    {"name": "Non-English Input (Russian)", "input": "Ваш аккаунт заблокирован", "expected_status": 200},

    # Mixed content
    {"name": "Mixed Content", "input": "Click here! 🔥🔥🔥 http://example.com", "expected_status": 200},

    # Ambiguous input
    {"name": "Ambiguous Input", "input": "Your account has been locked. Contact us.", "expected_status": 200},

    # Malformed input
    {"name": "Malformed Input", "input": "\x00\x01\x02\x03", "expected_status": 200},

    # Valid input (safe message)
    {"name": "Valid Input (Safe)", "input": "Your package is out for delivery.", "expected_status": 200},

    # Valid input (scam message)
    {"name": "Valid Input (Scam)", "input": "You've won a free iPhone! Click here.", "expected_status": 200},

    # Invalid JSON payload
    {"name": "Invalid JSON Payload", "input": None, "expected_status": 400},

    # Missing "message" field in payload
    {"name": "Missing 'message' Field", "input": {}, "expected_status": 400, "expected_error": "No message provided"},

    # High confidence scam
    {"name": "High Confidence Scam", "input": "Your account will be suspended unless you verify your info.", "expected_status": 200},

    # Low confidence input
    {"name": "Low Confidence Input", "input": "Hi, can you send me your phone number?", "expected_status": 200},
]

def run_test_case(test_case):
    """Run a single test case and print the results."""
    print(f"Running test: {test_case['name']}")

    # Prepare the payload
    payload = {"message": test_case["input"]} if test_case["input"] is not None else None

    # Make the API request
    try:
        response = requests.post(BASE_URL, json=payload)
    except Exception as e:
        print(f"  [ERROR] Failed to connect to the API: {e}")
        return

    # Check the status code
    if response.status_code != test_case["expected_status"]:
        print(f"  [FAIL] Expected status {test_case['expected_status']}, got {response.status_code}")
        return

    # Check the response content
    if response.status_code == 400 and "expected_error" in test_case:
        error_message = response.json().get("error", "")
        if error_message != test_case["expected_error"]:
            print(f"  [FAIL] Expected error '{test_case['expected_error']}', got '{error_message}'")
            return

    if response.status_code == 200:
        result = response.json()
        print(f"  [PASS] Result: {json.dumps(result, indent=2)}")
    else:
        print(f"  [PASS] Status: {response.status_code}")

def main():
    """Run all test cases."""
    print("\n========== Starting Edge Case Analysis ==========\n")
    for test_case in TEST_CASES:
        run_test_case(test_case)
        print("\n")
    print("========== Edge Case Analysis Complete ==========\n")

if __name__ == "__main__":
    main()