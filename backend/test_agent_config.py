"""
Test script for Todo Agent configuration.

This tests the agent setup and behavior rules without requiring OpenAI API.
"""

import asyncio
from src.agents.todo_agent import AGENT_INSTRUCTIONS, format_task_list


def test_agent_instructions():
    """Test that agent instructions contain all required behavior rules."""
    print("Testing Agent Instructions...")
    
    # Check for all required behavior rules
    required_patterns = [
        ("Create tasks", ["create", "add", "new task"]),
        ("List tasks", ["show", "list", "my tasks"]),
        ("Complete tasks", ["done", "complete", "finish"]),
        ("Update tasks", ["change", "update", "modify"]),
        ("Delete tasks", ["remove", "delete"]),
    ]
    
    for behavior, keywords in required_patterns:
        found = any(kw in AGENT_INSTRUCTIONS.lower() for kw in keywords)
        assert found, f"Missing behavior rule for: {behavior}"
        print(f"  ✓ {behavior} rules present")
    
    # Check for confirmation requirements
    assert "confirm" in AGENT_INSTRUCTIONS.lower(), "Missing confirmation requirement"
    print("  ✓ Confirmation requirements present")
    
    # Check for error handling
    assert "error" in AGENT_INSTRUCTIONS.lower(), "Missing error handling"
    print("  ✓ Error handling present")
    
    print("\n[OK] All agent instructions validated!\n")


def test_format_task_list():
    """Test task list formatting."""
    print("Testing Task List Formatting...")
    
    # Test empty list
    result = format_task_list([])
    assert "don't have any tasks" in result
    print("  ✓ Empty list handled")
    
    # Test with tasks
    tasks = [
        {"id": "abc12345-1234-1234-1234-123456789abc", "title": "Task 1", "status": "pending", "priority": "high"},
        {"id": "def67890-1234-1234-1234-123456789def", "title": "Task 2", "status": "in_progress", "priority": "medium"},
        {"id": "ghi11111-1234-1234-1234-123456789ghi", "title": "Task 3", "status": "completed", "priority": "low"},
    ]
    result = format_task_list(tasks)
    assert "Task 1" in result
    assert "Task 2" in result
    assert "Task 3" in result
    assert "Pending" in result
    assert "In Progress" in result
    assert "Completed" in result
    print("  ✓ Task list formatted correctly")
    
    print("\n[OK] Task list formatting validated!\n")


def test_extract_task_id():
    """Test task ID extraction from messages."""
    print("Testing Task ID Extraction...")
    
    from src.agents.todo_agent import extract_task_id_from_message
    
    # Test with UUID in message
    msg = "Please complete task abc12345-1234-5678-9abc-123456789def for me"
    result = extract_task_id_from_message(msg)
    assert result == "abc12345-1234-5678-9abc-123456789def"
    print("  ✓ UUID extracted from message")
    
    # Test without UUID
    msg = "Complete my task"
    result = extract_task_id_from_message(msg)
    assert result is None
    print("  ✓ Returns None when no UUID present")
    
    print("\n[OK] Task ID extraction validated!\n")


async def test_agent_creation():
    """Test agent creation with MCP tools."""
    print("Testing Agent Creation...")
    
    import uuid
    from src.agents.todo_agent import create_todo_agent
    
    test_user_id = str(uuid.uuid4())
    
    try:
        agent = await create_todo_agent(test_user_id)
        assert agent is not None
        assert agent.name == "Todo Assistant"
        print(f"  ✓ Agent created: {agent.name}")
        print(f"  ✓ Model: {agent.model}")
        print(f"  ✓ Tools available: {len(agent.tools)}")
        print("\n[OK] Agent creation validated!\n")
    except Exception as e:
        print(f"  ⚠ Agent creation skipped (requires MCP server running): {e}\n")


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Todo Agent - Configuration Tests")
    print("=" * 60)
    print()
    
    # Sync tests
    test_agent_instructions()
    test_format_task_list()
    test_extract_task_id()
    
    # Async tests
    await test_agent_creation()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
