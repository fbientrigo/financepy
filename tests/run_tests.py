import sys
import types
from tests import test_hurst_dfa
from tests import test_market_mode
from tests import test_risk_off

def run_tests_in_module(module):
    print(f"Running tests in {module.__name__}...")
    passed = 0
    failed = 0
    for name, func in vars(module).items():
        if name.startswith('test_') and isinstance(func, types.FunctionType):
            try:
                func()
                print(f"  [PASS] {name}")
                passed += 1
            except AssertionError as e:
                print(f"  [FAIL] {name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
                failed += 1
    return passed, failed

if __name__ == "__main__":
    total_passed = 0
    total_failed = 0
    
    modules = [test_hurst_dfa, test_market_mode, test_risk_off]
    
    for m in modules:
        p, f = run_tests_in_module(m)
        total_passed += p
        total_failed += f
        
    print(f"\nTotal Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    
    if total_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
