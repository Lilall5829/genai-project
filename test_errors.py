import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("ERROR HANDLING TESTS")
print("=" * 70)
print()

def test_error(test_name, url, data=None, json_data=None, headers=None):
    """Test an endpoint and display the error response"""
    print(f"Test: {test_name}")
    print("-" * 70)
    
    try:
        if json_data is not None:
            response = requests.post(url, json=json_data, headers=headers or {})
        elif data is not None:
            response = requests.post(url, data=data, headers=headers or {})
        else:
            response = requests.post(url, headers=headers or {})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")
    
    print()

# Test 1: Invalid JSON format
print("1. INVALID JSON FORMAT")
test_error(
    "Sending malformed JSON",
    f"{BASE_URL}/generate",
    data="invalid json{{{",
    headers={"Content-Type": "application/json"}
)

# Test 2: Missing required field
print("2. MISSING REQUIRED FIELD (prompt)")
test_error(
    "Request without 'prompt' field",
    f"{BASE_URL}/generate",
    json_data={
        "temperature": 0.7,
        "max_tokens": 100
    }
)

# Test 3: Prompt too long (validation error)
print("3. PROMPT TOO LONG (>1000 characters)")
test_error(
    "Prompt exceeds 1000 character limit",
    f"{BASE_URL}/generate",
    json_data={
        "prompt": "A" * 1100,  # 1100 characters
        "max_tokens": 50
    }
)

# Test 4: Invalid parameter type
print("4. INVALID PARAMETER TYPE")
test_error(
    "temperature should be float, not string",
    f"{BASE_URL}/generate",
    json_data={
        "prompt": "Hello",
        "temperature": "not a number",
        "max_tokens": 50
    }
)

# Test 5: Negative max_tokens
print("5. INVALID VALUE (negative max_tokens)")
test_error(
    "Negative max_tokens value",
    f"{BASE_URL}/generate",
    json_data={
        "prompt": "Hello",
        "max_tokens": -100
    }
)

# Test 6: Non-existent endpoint
print("6. NON-EXISTENT ENDPOINT")
test_error(
    "Calling endpoint that doesn't exist",
    f"{BASE_URL}/nonexistent",
    json_data={"prompt": "Hello"}
)

print("=" * 70)
print("TESTS COMPLETED")
print("=" * 70)
print()
print("Observations:")
print("- Check the error response format for each test")
print("- Are the error messages clear and helpful?")
print("- Is the format consistent across different error types?")

