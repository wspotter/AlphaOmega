# MCP Server Verification Guide

## Quick Verification Commands

### 1. Check if MCP Server is Running
```bash
ps aux | grep -E "mcpo.*8002" | grep -v grep
```
**Expected**: Should show the mcpo process on port 8002

### 2. Check Server Health
```bash
curl -s http://localhost:8002/openapi.json | python3 -m json.tool | head -20
```
**Expected**: Should return OpenAPI JSON schema

### 3. List All Available Tools
```bash
curl -s http://localhost:8002/openapi.json | python3 -c "import json, sys; data=json.load(sys.stdin); [print(f'{i+1}. {path}') for i, path in enumerate(sorted(data['paths'].keys()))]"
```
**Expected**: Should list 76 tools

### 4. Test a Tool
```bash
# Check inventory
curl -X POST http://localhost:8002/get_low_stock_items \
  -H "Content-Type: application/json" \
  -d '{}'

# List allowed directories
curl -X POST http://localhost:8002/list_allowed_directories \
  -H "Content-Type: application/json" \
  -d '{}'

# Check file system
curl -X POST http://localhost:8002/list_directory \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/stacy/AlphaOmega"}'
```

### 5. Check Server Logs
```bash
tail -30 /home/stacy/AlphaOmega/logs/mcp-server.log
```

### 6. Restart MCP Server (if needed)
```bash
# Stop
pkill -f "mcpo.*8002"

# Start
cd /home/stacy/AlphaOmega
$HOME/.local/bin/uvx mcpo --port 8002 -- node agent_s/mcp/mcpart/build/index.js > logs/mcp-server.log 2>&1 &

# Verify
sleep 3 && curl -s http://localhost:8002/openapi.json | python3 -c "import json, sys; print('✅ MCP Server OK -', len(json.load(sys.stdin)['paths']), 'tools')"
```

## MCP Server Information

**Status**: ✅ Running  
**Port**: 8002  
**Process**: mcpo (Model Context Protocol Over HTTP)  
**Tools Available**: 76  
**Log File**: `/home/stacy/AlphaOmega/logs/mcp-server.log`

## Available Tool Categories

### Inventory & Products (12 tools)
- `check_inventory` - Check stock levels
- `get_low_stock_items` - Find items needing reorder
- `update_stock` - Update inventory levels
- `search_products` - Find products
- `get_best_sellers` - Top selling items
- `get_inventory_value` - Calculate total inventory value
- `forecast_demand` - Predict future demand
- `suggest_bundle` - Product bundling suggestions
- `compare_supplier_prices` - Price comparison
- `get_supplier_info` - Supplier details
- `create_purchase_order` - Generate PO
- `create_alert` - Set inventory alerts

### Sales & Customers (8 tools)
- `get_sales_report` - Sales analytics
- `get_daily_sales` - Today's sales
- `calculate_discount` - Price calculations
- `calculate_profit_margin` - Margin analysis
- `lookup_customer` - Customer details
- `get_top_customers` - VIP customers
- `get_customer_recommendations` - Personalized suggestions
- `update_loyalty_points` - Loyalty program

### Social Media & Marketing (12 tools)
- `post_to_social_media` - Publish posts
- `generate_post_ideas` - Content suggestions
- `generate_hashtags` - Hashtag recommendations
- `get_instagram_story_ideas` - Story concepts
- `schedule_weekly_posts` - Auto-scheduling
- `create_product_campaign` - Campaign creation
- `analyze_post_performance` - Analytics
- `get_social_analytics` - Platform metrics
- `get_new_comments` - Comment monitoring
- `suggest_comment_reply` - Reply suggestions
- `auto_respond_common_questions` - Auto-responses
- `track_competitor_activity` - Competitive analysis

### Scheduling & Tasks (10 tools)
- `book_appointment` - Schedule appointments
- `check_appointments` - View bookings
- `schedule_event` - Calendar events
- `get_daily_agenda` - Today's schedule
- `get_today_schedule` - Staff schedule
- `get_employee_schedule` - Team calendar
- `list_upcoming_events` - Event list
- `create_task` - Add tasks
- `update_task` - Modify tasks
- `complete_task` - Mark complete

### File Operations (13 tools)
- `read_file` - Read any file
- `write_file` - Create/overwrite file
- `edit_file` - Modify file
- `read_text_file` - Text files only
- `read_media_file` - Images/media
- `read_multiple_files` - Batch read
- `list_directory` - Directory contents
- `list_directory_with_sizes` - With file sizes
- `directory_tree` - Recursive tree view
- `create_directory` - Make directories
- `move_file` - Relocate files
- `search_files` - Find files
- `get_file_info` - File metadata

### Business Operations (11 tools)
- `generate_eod_report` - End of day summary
- `generate_daily_summary` - Daily overview
- `export_data` - Data export
- `log_expense` - Track expenses
- `get_expense_summary` - Expense reports
- `categorize_expenses` - Expense categorization
- `calculate_labor_cost` - Labor calculations
- `set_reminder` - Reminders
- `list_alerts` - View alerts
- `create_note` - Note taking
- `search_notes` - Find notes

### VIP Tools (6 tools)
- `vip_health_check` - System health
- `vip_check_status` - Status check
- `vip_generate_dataset` - Data generation
- `vip_list_datasets` - Available datasets
- `vip_get_dataset_info` - Dataset metadata
- `vip_validate_config` - Config validation

## Testing MCP Tools

### Inventory Test
```bash
curl -X POST http://localhost:8002/check_inventory \
  -H "Content-Type: application/json" \
  -d '{"product_id": "SKU001"}'
```

### File Operation Test
```bash
# Create a test file
curl -X POST http://localhost:8002/write_file \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/stacy/AlphaOmega/artifacts/test.txt", "content": "Hello from MCP!"}'

# Read it back
curl -X POST http://localhost:8002/read_file \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/stacy/AlphaOmega/artifacts/test.txt"}'
```

### Task Management Test
```bash
# Create task
curl -X POST http://localhost:8002/create_task \
  -H "Content-Type: application/json" \
  -d '{"title": "Test MCP", "description": "Verify MCP tools work"}'

# List tasks
curl -X POST http://localhost:8002/list_tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Integration with OpenWebUI

The MCP server is integrated into the AlphaOmega pipeline router at:
`/home/stacy/AlphaOmega/pipelines/alphaomega_router.py`

**MCP Keywords** that trigger routing:
- "create artifact"
- "save artifact"
- "save to memory"
- "remember this"
- "store this"
- "read file"
- "write file"
- "list files"
- "file operation"

**Example Prompts**:
- "Check inventory for SKU001"
- "Show me low stock items"
- "Create a task to order supplies"
- "List files in the artifacts directory"
- "Generate today's sales report"
- "Schedule a meeting for tomorrow"

## Troubleshooting

### Server Not Responding
1. Check if process is running: `ps aux | grep mcpo`
2. Check logs: `tail -50 /home/stacy/AlphaOmega/logs/mcp-server.log`
3. Restart server (see restart commands above)

### Tools Not Working
1. Verify API connectivity: `curl http://localhost:8002/openapi.json`
2. Check tool syntax in OpenAPI spec
3. Ensure required parameters are provided

### Permission Errors
- File operations are restricted to allowed directories:
  - `/home/stacy/AlphaOmega/artifacts`
  - `/home/stacy/AlphaOmega/logs`
  - `/home/stacy/AlphaOmega/docs`

## Performance Monitoring

```bash
# Watch server activity in real-time
tail -f /home/stacy/AlphaOmega/logs/mcp-server.log

# Count requests per minute
tail -100 /home/stacy/AlphaOmega/logs/mcp-server.log | grep "POST" | wc -l

# Check server resource usage
ps aux | grep mcpo | awk '{print "CPU: "$3"% | MEM: "$4"%"}'
```

## Quick Status Check Script

Create `/home/stacy/AlphaOmega/scripts/check-mcp.sh`:
```bash
#!/bin/bash
echo "🔍 MCP Server Status:"
if pgrep -f "mcpo.*8002" > /dev/null; then
    TOOLS=$(curl -s http://localhost:8002/openapi.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)['paths']))" 2>&1)
    echo "✅ Running with $TOOLS tools on port 8002"
else
    echo "❌ Not running"
fi
```

Make it executable: `chmod +x /home/stacy/AlphaOmega/scripts/check-mcp.sh`  
Run it: `./scripts/check-mcp.sh`
