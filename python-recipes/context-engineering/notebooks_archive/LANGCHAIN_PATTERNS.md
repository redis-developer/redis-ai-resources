# LangChain Patterns Used Throughout the Course

This document outlines the consistent LangChain patterns used throughout the Context Engineering course to ensure compatibility with our LangGraph agent architecture.

## Core Imports

All notebooks now use these consistent imports:

```python
# LangChain imports (consistent with our LangGraph agent)
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool

# Initialize LangChain LLM (same as our agent)
if OPENAI_API_KEY:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
    print("✅ LangChain ChatOpenAI initialized")
else:
    llm = None
    print("⚠️  LangChain LLM not available (API key not set)")
```

## Message Patterns

### System Instructions Testing
```python
def test_prompt(system_prompt, user_message, label):
    """Helper function to test prompts using LangChain messages"""
    if llm:
        # Create LangChain messages (same pattern as our agent)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Invoke the LLM (same as our agent does)
        response = llm.invoke(messages)
        
        print(f"🤖 {label}:")
        print(response.content)
    else:
        print(f"⚠️  {label}: LangChain LLM not available - skipping test")
```

### Context-Aware Conversations
```python
def test_context_aware_prompt(system_prompt, user_message, student_context):
    """Test context-aware prompts with student information"""
    if llm:
        # Build context-aware system message
        context_prompt = build_context_aware_prompt(student_context)
        
        # Create LangChain messages with context
        messages = [
            SystemMessage(content=context_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Invoke with context (same pattern as our agent)
        response = llm.invoke(messages)
        
        print("🤖 Context-Aware Response:")
        print(response.content)
```

## Tool Definition Patterns

### LangChain Tool Decorator
```python
from langchain_core.tools import tool

@tool
def search_courses(query: str, format_filter: Optional[str] = None) -> str:
    """Search for courses in the Redis University catalog.
    
    Args:
        query: Search terms for course titles and descriptions
        format_filter: Optional filter for course format (online, in-person, hybrid)
    
    Returns:
        Formatted list of matching courses with details
    """
    # Tool implementation here
    pass
```

### Tool Schema Compatibility
```python
class ToolDefinition:
    def to_langchain_schema(self) -> Dict[str, Any]:
        """Convert to LangChain tool schema (compatible with OpenAI function calling)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required_params
                }
            }
        }
```

## Agent Integration Patterns

### Tool-Enabled Agent
```python
class ToolEnabledUniversityAgent:
    """Redis University Agent with comprehensive tool capabilities (LangChain-based)."""
    
    def __init__(self, student_id: str, llm=None):
        self.student_id = student_id
        self.llm = llm  # LangChain ChatOpenAI instance
        self.tool_registry = tool_registry
        self.conversation_history = []
    
    def chat(self, message: str) -> str:
        """Chat with the agent using LangChain patterns."""
        if not self.llm:
            return "LangChain LLM not available"
        
        # Build conversation with context
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            *self.get_conversation_history(),
            HumanMessage(content=message)
        ]
        
        # Invoke LLM with tools
        response = self.llm.invoke(messages)
        
        # Update conversation history
        self.conversation_history.extend([
            HumanMessage(content=message),
            AIMessage(content=response.content)
        ])
        
        return response.content
```

## Context-Aware Tool Integration

### Context Injection
```python
def inject_context_into_messages(base_messages, context):
    """Inject context into LangChain messages."""
    enhanced_messages = []
    
    for message in base_messages:
        if isinstance(message, SystemMessage):
            # Enhance system message with context
            enhanced_content = f"{message.content}\n\nStudent Context:\n{format_context(context)}"
            enhanced_messages.append(SystemMessage(content=enhanced_content))
        else:
            enhanced_messages.append(message)
    
    return enhanced_messages
```

### Context-Aware Tool Execution
```python
@tool
def context_aware_search(query: str, context: Optional[Dict] = None) -> str:
    """Context-aware course search using LangChain patterns."""
    
    # Use context to enhance search
    if context and context.get('preferences'):
        # Apply user preferences automatically
        format_filter = context['preferences'].get('format')
        if format_filter:
            print(f"💡 Applied preference: {format_filter} format")
    
    # Perform search with context awareness
    results = perform_search(query, format_filter)
    
    # Return formatted results
    return format_search_results(results, context)
```

## Benefits of LangChain Integration

### 1. **Consistency with LangGraph Agent**
- All notebooks use the same message patterns as the production agent
- Students learn patterns they'll use in the final LangGraph implementation
- Seamless transition from learning to building

### 2. **Modern AI Development Patterns**
- Industry-standard LangChain framework
- Compatible with OpenAI function calling
- Extensible to other LLM providers

### 3. **Educational Clarity**
- Clear separation between system and human messages
- Explicit message flow that students can understand
- Consistent patterns across all notebooks

### 4. **Production Readiness**
- Patterns scale from learning to production
- Compatible with LangGraph workflows
- Industry best practices throughout

## Migration Notes

### What Changed
- `openai.OpenAI()` → `ChatOpenAI()`
- `{"role": "system", "content": "..."}` → `SystemMessage(content="...")`
- `{"role": "user", "content": "..."}` → `HumanMessage(content="...")`
- `client.chat.completions.create()` → `llm.invoke(messages)`
- `response.choices[0].message.content` → `response.content`

### What Stayed the Same
- All educational content and learning objectives
- Tool functionality and Redis integration
- Context engineering concepts and patterns
- Hands-on exercises and challenges

This ensures students learn modern LangChain patterns while maintaining the educational effectiveness of the original course design.
