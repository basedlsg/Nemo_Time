# Model Context Protocol (MCP) - Development Guide

## 1. What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is a standardized communication layer that allows AI models, like me, to interact with external tools and resources. It operates on a client-server model:

*   **MCP Server:** An application that exposes a set of tools (e.g., `get_database_record`) or resources (e.g., `file://path/to/data.csv`).
*   **MCP Client:** The AI model, which can discover and execute tools provided by connected MCP servers.

This allows for extending the AI's capabilities beyond its built-in tools, enabling it to interact with local files, databases, or external APIs in a structured way. All communication is done via JSON objects, typically over standard input/output (stdio) for local servers.

## 2. How MCP Can Accelerate Nemo Development

For the Nemo project, MCP provides a powerful framework for development and testing, allowing us to decouple the AI logic from the live Google Cloud infrastructure.

*   **Local Testing & Iteration:** We can test Cloud Functions locally by simulating their dependencies. For example, an MCP server can provide a mock `vertex_ai_search` tool that returns predictable results, allowing us to test the `query_handler`'s logic without needing a deployed and populated Vertex AI index.
*   **Tool-Based Interaction:** Instead of running `curl` commands to test endpoints, we can create an MCP server that exposes tools like `test_query_endpoint`. This allows for more structured, repeatable, and automated testing directly from the AI model.
*   **Live Data Injection:** A developer can run a local MCP server to provide live data or alternative configurations to a function during a test run, enabling rapid debugging and what-if analysis.

## 3. Example MCP Usage for Nemo

### Scenario: Local Testing of the `query` Function

A developer needs to test the logic of the `query` function without deploying it or its dependencies.

1.  **Create an MCP Server:** The developer writes a small Python script that acts as an MCP server. This server exposes a tool named `mock_vertex_search`.
2.  **Define the Tool:** The `mock_vertex_search` tool accepts a query vector and filter parameters, and returns a hardcoded set of document chunks, simulating a response from Vertex AI.
3.  **Run the Test:** The developer instructs the AI model (in `Code` or `Debug` mode) to use the `mock_vertex_search` tool to test the `compose_response` logic from the `lib/composer.py` file.

This approach allows the developer to test the response composition logic in isolation, ensuring it works as expected before integrating it with the live Vertex AI service.

### Conceptual MCP Server in Python

```python
# conceptual_mcp_server.py
import json
import sys

def main():
    """
    A conceptual MCP server for testing the Nemo query function.
    """
    # This server would be started as a background process.
    # The AI model would communicate with it via stdio.

    while True:
        # Read a request from the AI model (stdin)
        line = sys.stdin.readline()
        if not line:
            break
        request = json.loads(line)

        # Route the request to the appropriate tool
        if request.get("tool_name") == "mock_vertex_search":
            response = {
                "status": "success",
                "result": {
                    "candidates": [
                        {
                            "text": "这是从模拟Vertex AI返回的示例文本。",
                            "metadata": {
                                "title": "模拟文档",
                                "url": "http://example.com/doc1",
                                "province": "gd",
                                "asset": "solar"
                            }
                        }
                    ]
                }
            }
        else:
            response = {"status": "error", "message": "Tool not found"}

        # Write the response back to the AI model (stdout)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
```

This guide provides a starting point for leveraging MCP in our development process. By adopting this tool-based approach, we can enhance our testing capabilities and accelerate the development lifecycle.