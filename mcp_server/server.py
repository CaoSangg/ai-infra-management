# mcp_server/server.py
import asyncio
from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# Import các hàm từ Module 1 và Module 3
from tool_registry import get_available_tools
from dispatcher import execute_ansible_playbook

app = Server("infra-mcp-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    # Phục vụ cho Dynamic Broadcasting
    return get_available_tools()

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Route yêu cầu tới đúng hàm thực thi ở Layer bên dưới
    if name == "run_ansible_playbook":
        playbook_name = arguments.get("playbook_name")
        extra_vars = arguments.get("extra_vars", {})
        
        # Gọi xuống Execution Dispatcher
        result_text = execute_ansible_playbook(playbook_name, extra_vars)
        return [types.TextContent(type="text", text=result_text)]
    
    raise ValueError(f"Tool {name} không tồn tại hoặc chưa được đăng ký")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
