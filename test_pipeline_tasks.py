#!/usr/bin/env python3
"""Test the AlphaOmega pipeline with task queries"""
import asyncio
import sys
sys.path.insert(0, '/home/stacy/AlphaOmega/pipelines')

from alphaomega_router import Pipeline

async def test_task_query():
    """Test if 'what tasks do i have today' routes to MCP"""
    pipeline = Pipeline()
    
    test_queries = [
        "what tasks do i have today",
        "show my tasks",
        "list all tasks",
        "what do I need to do today"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        # Detect intent
        intent = pipeline._detect_intent(query)
        print(f"Intent: {intent}")
        
        if intent == "mcp":
            tool_name, params = pipeline._detect_mcp_tool(query)
            print(f"MCP Tool: {tool_name}")
            print(f"Params: {params}")
            
            # Try to call it
            body = {
                "messages": [{"role": "user", "content": query}]
            }
            
            print("\nResponse:")
            async for chunk in pipeline.pipe(body):
                print(chunk, end="", flush=True)
            print()
        else:
            print(f"⚠️ Wrong intent! Expected 'mcp', got '{intent}'")

if __name__ == "__main__":
    asyncio.run(test_task_query())
