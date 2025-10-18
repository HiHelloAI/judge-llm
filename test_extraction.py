"""Test if text extraction is causing issues"""

from judge_llm.core.models import Content, Part

def extract_text_old(parts: list) -> str:
    """Old version"""
    texts = [part.text for part in parts if part.text]
    return " ".join(texts).strip()

def extract_text_new(parts: list) -> str:
    """New version"""
    if not parts:
        return ""
    texts = [part.text.strip() for part in parts if part.text and part.text.strip()]
    return " ".join(texts)

# Test cases
test_cases = [
    ("Single part", [Part(text="Hello world")]),
    ("Multiple parts", [Part(text="Hello"), Part(text="world")]),
    ("Parts with whitespace", [Part(text="  Hello  "), Part(text="  world  ")]),
    ("Parts with trailing spaces", [Part(text="Hello "), Part(text="world ")]),
    ("Part with None", [Part(text="Hello"), Part(text=None), Part(text="world")]),
    ("Part with empty string", [Part(text="Hello"), Part(text=""), Part(text="world")]),
    ("Part with just spaces", [Part(text="Hello"), Part(text="   "), Part(text="world")]),
]

print("="*80)
print("TEXT EXTRACTION COMPARISON")
print("="*80)

for name, parts in test_cases:
    old_result = extract_text_old(parts)
    new_result = extract_text_new(parts)

    print(f"\n{name}:")
    print(f"  Old: '{old_result}' (len: {len(old_result)})")
    print(f"  New: '{new_result}' (len: {len(new_result)})")
    print(f"  Match: {old_result == new_result}")

    if old_result != new_result:
        print(f"  DIFFERENCE DETECTED!")
        print(f"    Old repr: {repr(old_result)}")
        print(f"    New repr: {repr(new_result)}")
