#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced Gmail MCP Server
Tests all 14 features to ensure they work correctly
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import functions from enhanced_server
from enhanced_server import (
    search_emails,
    read_email,
    send_email,
    mark_as_read,
    mark_as_unread,
    delete_email,
    archive_email,
    star_email,
    list_labels,
    add_label,
    remove_label,
    create_draft,
    reply_to_email,
    get_thread
)

def print_test(test_name, result):
    """Print test results in a formatted way"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        print(f"✅ {test_name} - PASSED")
    else:
        print(f"❌ {test_name} - FAILED")
        print(f"   Error: {result.get('message', 'Unknown error')}")

    return result.get("status") == "success"

def main():
    """Run all tests"""
    print("🧪 Enhanced Gmail MCP Server - Comprehensive Feature Test")
    print("=" * 60)

    passed = 0
    failed = 0
    test_results = {}

    # Test 1: List Labels (Read-only, safe)
    print("\n📁 Testing Label Management...")
    result = list_labels()
    if print_test("1. list_labels", result):
        passed += 1
        test_results["list_labels"] = "✅ PASSED"
        # Store labels for later use
        labels = result.get("labels", [])
        print(f"   Found {len(labels)} labels")
    else:
        failed += 1
        test_results["list_labels"] = "❌ FAILED"

    # Test 2: Search Emails (Read-only, safe)
    print("\n📧 Testing Email Search...")
    result = search_emails(query="is:inbox", max_results=3)
    if print_test("2. search_emails", result):
        passed += 1
        test_results["search_emails"] = "✅ PASSED"
        messages = result.get("messages", [])
        print(f"   Found {len(messages)} messages")

        # Store first message ID for later tests
        if messages:
            test_message_id = messages[0]["id"]
            test_message_subject = messages[0]["subject"]
            print(f"   Using message: {test_message_subject}")
        else:
            test_message_id = None
            print("   ⚠️  No messages found for further testing")
    else:
        failed += 1
        test_results["search_emails"] = "❌ FAILED"
        test_message_id = None

    # Test 3: Read Email (Read-only, safe)
    if test_message_id:
        print("\n📖 Testing Email Reading...")
        result = read_email(test_message_id)
        if print_test("3. read_email", result):
            passed += 1
            test_results["read_email"] = "✅ PASSED"
            thread_id = result.get("labels", [])
            # Try to find thread ID
            print(f"   Subject: {result.get('subject', 'N/A')}")
            print(f"   From: {result.get('from', 'N/A')}")
        else:
            failed += 1
            test_results["read_email"] = "❌ FAILED"
    else:
        print("\n⏭️  Skipping read_email (no test message)")
        test_results["read_email"] = "⏭️  SKIPPED"

    # Test 4: Get Thread (Read-only, requires thread ID)
    # We'll skip this for now as we need a thread ID
    print("\n⏭️  Skipping get_thread (requires specific thread ID)")
    test_results["get_thread"] = "⏭️  SKIPPED (needs thread ID)"

    # Test 5: Mark as Unread (Safe, reversible)
    if test_message_id:
        print("\n✏️  Testing Email Status Management...")
        result = mark_as_unread(test_message_id)
        if print_test("4. mark_as_unread", result):
            passed += 1
            test_results["mark_as_unread"] = "✅ PASSED"
        else:
            failed += 1
            test_results["mark_as_unread"] = "❌ FAILED"

        # Test 6: Mark as Read (Safe, reversible)
        result = mark_as_read(test_message_id)
        if print_test("5. mark_as_read", result):
            passed += 1
            test_results["mark_as_read"] = "✅ PASSED"
        else:
            failed += 1
            test_results["mark_as_read"] = "❌ FAILED"
    else:
        print("\n⏭️  Skipping mark_as_read/unread (no test message)")
        test_results["mark_as_read"] = "⏭️  SKIPPED"
        test_results["mark_as_unread"] = "⏭️  SKIPPED"

    # Test 7: Star Email (Safe, reversible)
    if test_message_id:
        print("\n⭐ Testing Star Management...")
        result = star_email(test_message_id, star=True)
        if print_test("6. star_email (star)", result):
            passed += 1
            test_results["star_email"] = "✅ PASSED"

            # Unstar it back
            result = star_email(test_message_id, star=False)
            if result.get("status") == "success":
                print("   ✅ Unstar also works")
            else:
                print("   ⚠️  Unstar failed")
        else:
            failed += 1
            test_results["star_email"] = "❌ FAILED"
    else:
        print("\n⏭️  Skipping star_email (no test message)")
        test_results["star_email"] = "⏭️  SKIPPED"

    # Test 8: Label Management (Safe if we add/remove same label)
    if test_message_id and labels:
        print("\n🏷️  Testing Label Addition/Removal...")
        # Find a suitable label (preferably user-created, not system)
        test_label = None
        for label in labels:
            if label.get("type") == "user":
                test_label = label
                break

        if not test_label and labels:
            # Use any label if no user labels exist
            test_label = labels[0]

        if test_label:
            label_id = test_label["id"]
            label_name = test_label["name"]
            print(f"   Using label: {label_name}")

            result = add_label(test_message_id, label_id)
            if print_test("7. add_label", result):
                passed += 1
                test_results["add_label"] = "✅ PASSED"

                # Remove it back
                result = remove_label(test_message_id, label_id)
                if print_test("8. remove_label", result):
                    passed += 1
                    test_results["remove_label"] = "✅ PASSED"
                else:
                    failed += 1
                    test_results["remove_label"] = "❌ FAILED"
            else:
                failed += 1
                test_results["add_label"] = "❌ FAILED"
                test_results["remove_label"] = "⏭️  SKIPPED (add_label failed)"
        else:
            print("   ⚠️  No suitable labels found")
            test_results["add_label"] = "⏭️  SKIPPED (no labels)"
            test_results["remove_label"] = "⏭️  SKIPPED (no labels)"
    else:
        print("\n⏭️  Skipping label management (no test message or labels)")
        test_results["add_label"] = "⏭️  SKIPPED"
        test_results["remove_label"] = "⏭️  SKIPPED"

    # Test 9: Create Draft (Safe, creates draft in Drafts folder)
    print("\n✉️  Testing Draft Creation...")
    result = create_draft(
        to="test@example.com",
        subject="[TEST] Draft from Enhanced Gmail MCP",
        body="This is a test draft created by the automated test script."
    )
    if print_test("9. create_draft", result):
        passed += 1
        test_results["create_draft"] = "✅ PASSED"
        draft_id = result.get("draft_id")
        print(f"   Created draft ID: {draft_id}")
    else:
        failed += 1
        test_results["create_draft"] = "❌ FAILED"

    # Test 10: Reply to Email (SKIPPED - requires real email)
    print("\n⏭️  Skipping reply_to_email (requires real conversation)")
    test_results["reply_to_email"] = "⏭️  SKIPPED (manual test recommended)"

    # Test 11: Send Email (SKIPPED - avoid sending real emails in auto-test)
    print("\n⏭️  Skipping send_email (manual test recommended)")
    test_results["send_email"] = "⏭️  SKIPPED (manual test recommended)"

    # Test 12: Archive Email (Safe, reversible)
    if test_message_id:
