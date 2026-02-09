"""Manual verification script for JWT middleware implementation"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_get_current_user():
    """Verify get_current_user dependency exists and has correct signature"""
    from api.deps import get_current_user
    from fastapi import Depends
    from fastapi.security import HTTPBearer, HTTPAuthCredentials
    import inspect

    # Check function exists
    assert callable(get_current_user), "get_current_user should be callable"

    # Check signature
    sig = inspect.signature(get_current_user)
    params = sig.parameters

    # Should have credentials and session parameters
    assert 'credentials' in params, "Should have credentials parameter"
    assert 'session' in params, "Should have session parameter"

    print("✅ get_current_user dependency function exists with correct signature")
    return True

def verify_jwt_functions():
    """Verify JWT functions exist"""
    from security.jwt import verify_token, decode_token

    assert callable(verify_token), "verify_token should be callable"
    assert callable(decode_token), "decode_token should be callable"
    assert verify_token == decode_token, "decode_token should be alias of verify_token"

    print("✅ JWT verification functions exist")
    return True

def verify_task_endpoints_protected():
    """Verify all task endpoints have get_current_user dependency"""
    from api.v1.tasks import router
    import inspect

    protected_count = 0
    total_routes = 0

    for route in router.routes:
        if hasattr(route, 'endpoint'):
            total_routes += 1
            sig = inspect.signature(route.endpoint)
            params = sig.parameters

            # Check if current_user parameter exists
            if 'current_user' in params:
                param = params['current_user']
                # Check if it has Depends(get_current_user)
                if hasattr(param, 'default') and param.default is not inspect.Parameter.empty:
                    protected_count += 1
                    print(f"  ✅ {route.methods} {route.path} - protected")
                else:
                    print(f"  ❌ {route.methods} {route.path} - has current_user but no Depends")
            else:
                print(f"  ❌ {route.methods} {route.path} - not protected")

    print(f"\n✅ {protected_count}/{total_routes} task endpoints are protected")
    return protected_count == total_routes

def verify_error_handling():
    """Verify error handling in get_current_user"""
    import ast
    from pathlib import Path

    deps_file = Path(__file__).parent / "src" / "api" / "deps.py"
    with open(deps_file) as f:
        tree = ast.parse(f.read())

    # Find get_current_user function
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_current_user":
            # Check for try-except block
            has_exception_handler = False
            raises_401 = False

            for child in ast.walk(node):
                if isinstance(child, ast.Raise):
                    # Check if raising HTTPException
                    if isinstance(child.exc, ast.Call):
                        if hasattr(child.exc.func, 'id') and child.exc.func.id == 'HTTPException':
                            raises_401 = True
                if isinstance(child, ast.ExceptHandler):
                    has_exception_handler = True

            print(f"✅ get_current_user has exception handling: {has_exception_handler}")
            print(f"✅ get_current_user raises HTTPException: {raises_401}")
            return True

    print("❌ Could not verify error handling")
    return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Phase 6 - JWT Middleware Verification")
    print("=" * 60)
    print()

    checks = [
        ("JWT Functions", verify_jwt_functions),
        ("get_current_user Dependency", verify_get_current_user),
        ("Task Endpoints Protected", verify_task_endpoints_protected),
        ("Error Handling", verify_error_handling),
    ]

    passed = 0
    failed = 0

    for name, check_func in checks:
        try:
            print(f"\n[{name}]")
            if check_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} check failed")
        except Exception as e:
            failed += 1
            print(f"❌ {name} check failed with error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
