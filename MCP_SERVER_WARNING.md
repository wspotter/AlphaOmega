# ⚠️ MCP SERVER CONFIGURATION - IMPORTANT! ⚠️

## THE CORRECT WAY

**There is ONE unified MCP server on port 8002 with 76 tools.**

### Start Command:
```bash
./scripts/start-mcp-unified.sh
```

### Manual Start:
```bash
cd /home/stacy/AlphaOmega
$HOME/.local/bin/uvx mcpo --port 8002 -- node agent_s/mcp/mcpart/build/index.js > logs/mcp-unified.log 2>&1 &
```

### Verify:
```bash
curl -s http://localhost:8002/openapi.json | jq '.paths | keys | length'
# Should return: 76
```

## THE WRONG WAY (DON'T DO THIS!)

❌ **DO NOT** run `start-mcp-servers.sh` - This splits the server into TWO servers (8002 and 8003)  
❌ **DO NOT** start separate filesystem and mcpart servers  
❌ **DO NOT** use ports 8003, 8004, etc. for MCP

## Why This Matters

**Last night we unified everything into ONE server because:**
1. OpenWebUI works better with a single tool server
2. Reduces port conflicts and confusion
3. All 76 tools are accessible from one endpoint
4. Simpler to manage and monitor

## Tool Categories (All in ONE server on port 8002)

1. **Inventory Management** (12 tools) - add_item, update_stock, etc.
2. **Sales & Analytics** (8 tools) - record_sale, get_sales_report, etc.
3. **Social Media** (12 tools) - post_to_facebook, schedule_instagram, etc.
4. **Task & Calendar** (10 tools) - create_task, add_appointment, etc.
5. **File System** (13 tools) - read_file, write_file, search_files, etc.
6. **Business Operations** (11 tools) - add_customer, track_expense, etc.
7. **VIP Clients** (6 tools) - VIP management and automation
8. **Universal Tools** (4 tools) - Memory, artifacts, etc.

**Total: 76 tools in ONE unified server**

## If You Accidentally Start the Wrong Way

```bash
# Stop ALL MCP servers
pkill -f "mcpo.*800[0-9]"

# Start the CORRECT unified server
./scripts/start-mcp-unified.sh

# Verify
curl http://localhost:8002/openapi.json | jq '.paths | keys | length'
# Should show: 76
```

## Files to Use

✅ **CORRECT**: `scripts/start-mcp-unified.sh` - Starts ONE server with 76 tools  
❌ **WRONG**: `scripts/start-mcp-servers.sh.WRONG_DONT_USE` - Splits into multiple servers

## Integration with OpenWebUI

**Add to OpenWebUI:**
- Admin Panel → Settings → External Tools
- Click [+] under 'Manage Tool Servers'
- Name: **AlphaOmega MCP (76 Tools)**
- URL: **http://localhost:8002**

**That's it! ONE server, 76 tools, port 8002.**

---

**Last Updated**: October 11, 2025  
**Reason for This File**: Prevented accidental split of unified MCP server
