"""
OpenAI Agents SDK - Todo Agent Configuration

This module configures an AI agent that uses the MCP Todo Server tools
to manage tasks through natural language conversations.

Agent Behavior Rules:
- Add task when user says "create", "add", "new task"
- List tasks when user says "show", "list", "my tasks"
- Complete task when user says "done", "complete", "finish"
- Update task when user says "change", "update", "modify"
- Delete task when user says "remove", "delete"

Features:
- Friendly confirmations before destructive actions
- Error handling with helpful messages
- Context-aware task management
"""

import asyncio
import os
import json
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.mcp import MCPServerStdio

from src.mcp.server import init_db, Task, User


# ============================================================================
# Configuration
# ============================================================================

# Disable tracing for local development
set_tracing_disabled(True)

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")


# ============================================================================
# MCP Server Connection
# ============================================================================

@asynccontextmanager
async def get_mcp_server():
    """Create and manage MCP server connection."""
    server = MCPServerStdio(
        name="todo-app",
        # Run the MCP server as a subprocess
        command="python",
        args=["-m", "src.mcp.run"],
    )
    await server.connect()
    try:
        yield server
    finally:
        await server.disconnect()


# ============================================================================
# Agent Instructions
# ============================================================================

AGENT_INSTRUCTIONS = """
You are a friendly and helpful Todo Assistant. You help users manage their tasks
through natural conversation.

## Your Capabilities

You can help users:
1. **Create tasks** - When users want to add, create, or make a new task
2. **List tasks** - When users want to see, show, or list their tasks
3. **Complete tasks** - When users mark tasks as done, complete, or finished
4. **Update tasks** - When users want to change, update, or modify tasks
5. **Delete tasks** - When users want to remove or delete tasks

## Behavior Rules

### Creating Tasks
- When user says: "create", "add", "new task", "make a task"
- Ask for the task title if not provided
- Optionally ask for description, priority (low/medium/high), or due date
- Always confirm before creating: "I'll create a task called '[title]'. Should I proceed?"

### Listing Tasks
- When user says: "show", "list", "my tasks", "what do I have"
- Show tasks in a friendly, organized format
- Group by status if there are many tasks
- Offer to filter by status or priority

### Completing Tasks
- When user says: "done", "complete", "finish", "mark as done"
- Identify which task they're referring to
- If ambiguous, ask for clarification
- Confirm: "Great job! I'll mark '[task title]' as complete. OK?"

### Updating Tasks
- When user says: "change", "update", "modify", "edit"
- Ask what they want to change (title, description, priority, etc.)
- Confirm the changes before applying

### Deleting Tasks
- When user says: "remove", "delete", "get rid of"
- **ALWAYS confirm before deleting** - this is destructive!
- Say: "Just to confirm, you want to delete '[task title]'. This cannot be undone. Proceed?"
- Wait for explicit confirmation

## Communication Style

- Be warm and friendly
- Use encouraging language for completing tasks ("Great job!", "Well done!")
- Be cautious with destructive actions (delete)
- Keep responses concise but helpful
- Use emojis sparingly to add personality ✓

## Error Handling

- If a task isn't found, say so politely and offer to list their tasks
- If the user isn't found, explain they need to have an account
- If an operation fails, explain what went wrong and suggest alternatives
- Never expose technical error messages to the user

## User ID Handling

- You will be given a user_id for the current user
- Always use this user_id when calling tools
- Never ask the user for their user_id
- If operations fail due to user not found, guide them to create an account
"""


# ============================================================================
# Helper Functions
# ============================================================================

def format_task_list(tasks: list) -> str:
    """Format task list for display."""
    if not tasks:
        return "You don't have any tasks yet! Would you like to create one?"
    
    lines = ["Here are your tasks:\n"]
    
    # Group by status
    by_status = {"pending": [], "in_progress": [], "completed": []}
    for task in tasks:
        status = task.get("status", "pending")
        by_status[status].append(task)
    
    # Display pending first
    if by_status["pending"]:
        lines.append("📋 **Pending:**")
        for task in by_status["pending"]:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "⚪")
            lines.append(f"  {priority_icon} [{task['id'][:8]}] {task['title']}")
        lines.append("")
    
    # Display in progress
    if by_status["in_progress"]:
        lines.append("🔄 **In Progress:**")
        for task in by_status["in_progress"]:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "⚪")
            lines.append(f"  {priority_icon} [{task['id'][:8]}] {task['title']}")
        lines.append("")
    
    # Display completed
    if by_status["completed"]:
        lines.append("✅ **Completed:**")
        for task in by_status["completed"]:
            lines.append(f"  ✓ [{task['id'][:8]}] {task['title']}")
    
    return "\n".join(lines)


def extract_task_id_from_message(message: str) -> Optional[str]:
    """Extract task ID (UUID) from user message."""
    import re
    # Look for UUID pattern
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    matches = re.findall(uuid_pattern, message.lower())
    return matches[0] if matches else None


# ============================================================================
# Create Agent
# ============================================================================

async def create_todo_agent(user_id: str) -> Agent:
    """
    Create a Todo Agent with MCP tools connected.
    
    Args:
        user_id: The UUID of the current user
        
    Returns:
        Configured Agent instance
    """
    
    # Create MCP server connection
    mcp_server = MCPServerStdio(
        name="todo-app",
        command="python",
        args=["-m", "src.mcp.run"],
    )
    
    # Connect to MCP server
    await mcp_server.connect()
    
    # Get tools from MCP server
    mcp_tools = await mcp_server.list_tools()
    
    # Create agent with MCP tools
    agent = Agent(
        name="Todo Assistant",
        instructions=AGENT_INSTRUCTIONS,
        tools=mcp_tools,
        model="gpt-4o-mini",
    )
    
    return agent


# ============================================================================
# Run Conversation
# ============================================================================

async def run_conversation(user_id: str, user_message: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
    """
    Run a single turn of conversation with the Todo Agent.
    
    Args:
        user_id: The UUID of the current user
        user_message: The user's message
        conversation_history: Optional list of previous messages
        
    Returns:
        Dictionary with response and any tool results
    """
    
    # Create agent
    agent = await create_todo_agent(user_id)
    
    # Prepare input
    input_text = user_message
    
    # Run the agent
    result = await Runner.run(agent, input_text)
    
    return {
        "response": result.final_output,
        "conversation_id": None,  # Could be tracked if needed
    }


# ============================================================================
# Interactive CLI
# ============================================================================

async def interactive_cli(user_id: str):
    """Run interactive CLI conversation."""
    
    print("\n" + "=" * 60)
    print("📝 Todo Assistant - Powered by OpenAI Agents")
    print("=" * 60)
    print("\nI can help you manage your tasks!")
    print("Try saying things like:")
    print('  • "Add a task to buy groceries"')
    print('  • "Show me my tasks"')
    print('  • "Mark task [id] as done"')
    print('  • "Delete task [id]"')
    print('\nType "quit" or "exit" to end the conversation.\n')
    print("-" * 60)
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Goodbye! Have a productive day!")
                break
            
            # Run conversation
            result = await run_conversation(user_id, user_input, conversation_history)
            
            print(f"\n🤖 Assistant: {result['response']}")
            
            # Update history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": result["response"]})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point."""
    # Initialize database
    init_db()
    
    # For demo, create a test user
    import uuid
    from sqlalchemy import create_engine, Column, String
    from sqlalchemy.orm import declarative_base, Session
    
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = "users"
        id = Column(String(36), primary_key=True)
        email = Column(String(255), nullable=False)
        username = Column(String(50), nullable=False)
    
    engine = create_engine("sqlite:///todoapp.db")
    Base.metadata.create_all(engine)
    
    # Create or get test user
    test_user_id = str(uuid.uuid4())
    with Session(engine) as session:
        user = User(id=test_user_id, email="demo@example.com", username="demo")
        session.add(user)
        session.commit()
    
    print(f"\nDemo user created: {test_user_id}")
    
    # Run interactive CLI
    await interactive_cli(test_user_id)


if __name__ == "__main__":
    asyncio.run(main())
