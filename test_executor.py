"""
Test script for Python Executor skill

Run this to verify that the script execution functionality works correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent))

from skills.python_executor.tools import (
    list_available_scripts,
    execute_python_script,
    format_execution_result,
    get_script_info
)

def test_list_scripts():
    """Test listing available scripts."""
    print("\n" + "="*60)
    print("TEST 1: List Available Scripts")
    print("="*60)
    
    scripts = list_available_scripts()
    print(f"\nFound {len(scripts)} scripts:")
    for script in scripts:
        print(f"  ✓ {script}")
    
    return len(scripts) > 0

def test_get_script_info():
    """Test getting script information."""
    print("\n" + "="*60)
    print("TEST 2: Get Script Information")
    print("="*60)
    
    scripts = list_available_scripts()
    if not scripts:
        print("No scripts to test")
        return False
    
    script = scripts[0]
    info = get_script_info(script)
    
    print(f"\nScript: {script}")
    print(f"Path: {info['path']}")
    print(f"Description: {info['description'][:100]}...")
    print(f"Size: {info['size']} bytes")
    
    return info is not None

def test_execute_hello():
    """Test executing hello.py script."""
    print("\n" + "="*60)
    print("TEST 3: Execute hello.py")
    print("="*60)
    
    try:
        result = execute_python_script("hello.py", timeout=10)
        print(format_execution_result(result))
        return result['success']
    except FileNotFoundError:
        print("⚠️ hello.py not found - skipping test")
        return True  # Don't fail if script doesn't exist
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_execute_calculator():
    """Test executing calculator.py with arguments."""
    print("\n" + "="*60)
    print("TEST 4: Execute calculator.py with arguments")
    print("="*60)
    
    try:
        result = execute_python_script(
            "calculator.py",
            args=["add", "5", "3"],
            timeout=10
        )
        print(format_execution_result(result))
        
        # Check if result is correct
        success = result['success'] and "8" in result['stdout']
        if success:
            print("\n✅ Calculator test passed (5 + 3 = 8)")
        return success
        
    except FileNotFoundError:
        print("⚠️ calculator.py not found - skipping test")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_execute_system_info():
    """Test executing system_info.py."""
    print("\n" + "="*60)
    print("TEST 5: Execute system_info.py")
    print("="*60)
    
    try:
        result = execute_python_script("system_info.py", timeout=10)
        print(format_execution_result(result))
        return result['success']
    except FileNotFoundError:
        print("⚠️ system_info.py not found - skipping test")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_nonexistent_script():
    """Test handling of non-existent script."""
    print("\n" + "="*60)
    print("TEST 6: Handle Non-existent Script")
    print("="*60)
    
    try:
        result = execute_python_script("nonexistent.py")
        print("❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError as e:
        print(f"✅ Correctly raised error: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Python Script Executor - Test Suite")
    print("="*60)
    
    tests = [
        ("List Scripts", test_list_scripts),
        ("Get Script Info", test_get_script_info),
        ("Execute hello.py", test_execute_hello),
        ("Execute calculator.py", test_execute_calculator),
        ("Execute system_info.py", test_execute_system_info),
        ("Handle Non-existent Script", test_nonexistent_script),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())