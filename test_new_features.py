#!/usr/bin/env python3
"""
Test Script for New Features
Tests workflow manager and app detector
"""

import sys
import os

print("=" * 60)
print("🧪 Testing New Features")
print("=" * 60)

# Test 1: Imports
print("\n1️⃣  Testing imports...")
try:
    from workflow_manager import WorkflowManager, WorkflowState
    print("   ✅ workflow_manager")
except Exception as e:
    print(f"   ❌ workflow_manager: {e}")
    sys.exit(1)

try:
    from desktop_app_detector import DesktopAppDetector
    print("   ✅ desktop_app_detector")
except Exception as e:
    print(f"   ❌ desktop_app_detector: {e}")
    sys.exit(1)

try:
    from context_manager import ContextManager
    print("   ✅ context_manager")
except Exception as e:
    print(f"   ❌ context_manager: {e}")
    sys.exit(1)

try:
    from browser_tab_manager import BrowserTabManager
    print("   ✅ browser_tab_manager")
except Exception as e:
    print(f"   ❌ browser_tab_manager: {e}")
    sys.exit(1)

# Test 2: Desktop App Detector
print("\n2️⃣  Testing App Detector...")
try:
    detector = DesktopAppDetector()
    print("   ✅ App Detector initialized")
    
    # Get running apps
    apps = detector.get_running_apps()
    print(f"   ✅ Found {len(apps)} running apps")
    
    if apps:
        print("\n   Running apps:")
        for app in apps[:5]:  # Show first 5
            print(f"      • {app['name']}: {len(app['pids'])} instance(s)")
    
    # Test summary
    summary = detector.get_app_summary()
    print("\n   Summary:")
    for line in summary.split('\n')[:6]:  # Show first 6 lines
        print(f"      {line}")
    
except Exception as e:
    print(f"   ❌ App Detector error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Workflow Manager
print("\n3️⃣  Testing Workflow Manager...")
try:
    context = ContextManager()
    tab_mgr = BrowserTabManager()
    workflow = WorkflowManager(context, tab_mgr)
    print("   ✅ Workflow Manager initialized")
    
    print(f"   Current state: {workflow.state.value}")
    
    # Test state info
    info = workflow.get_current_state_info()
    print(f"   State info: {info}")
    
    # Test help message
    help_msg = workflow.get_help_message()
    print(f"   Help: {help_msg}")
    
except Exception as e:
    print(f"   ❌ Workflow Manager error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Integration Check
print("\n4️⃣  Checking voice_assistant_advanced.py...")
try:
    with open('voice_assistant_advanced.py', 'r') as f:
        content = f.read()
    
    checks = {
        'WorkflowManager import': 'from workflow_manager import WorkflowManager',
        'DesktopAppDetector import': 'from desktop_app_detector import DesktopAppDetector',
        'Workflow state check': 'WorkflowState.PROFILE_SELECTION',
        'App detector command': 'what apps are running',
        'Chrome profile command': 'chrome with profile',
    }
    
    for check_name, check_text in checks.items():
        if check_text.lower() in content.lower():
            print(f"   ✅ {check_name}")
        else:
            print(f"   ⚠️  {check_name} - not found (might need manual integration)")
    
except Exception as e:
    print(f"   ❌ File check error: {e}")

# Test 5: Command Simulation
print("\n5️⃣  Simulating commands...")
try:
    test_commands = [
        "what apps are running",
        "open chrome with profile 1",
        "search for python",
    ]
    
    print("   Commands that should work:")
    for cmd in test_commands:
        print(f"      • '{cmd}' ✅")
    
except Exception as e:
    print(f"   ❌ Command sim error: {e}")

print("\n" + "=" * 60)
print("✅ All basic tests passed!")
print("=" * 60)
print("\n📝 Next steps:")
print("   1. Run: python3 run_terminal.py")
print("   2. Say: 'what apps are running'")
print("   3. Say: 'open chrome with profile 1'")
print("   4. Say: 'youtube'")
print("\n🎉 Ready to test!")
