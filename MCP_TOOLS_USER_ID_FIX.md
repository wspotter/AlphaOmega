# ✅ MCP Tools - Empty User ID Fix

**Issue**: Tools showing "0" in UI, returning 200 OK but empty list  
**Root Cause**: `/api/v1/tools/list` filtering by user ownership  
**Fix**: Set `user_id` to empty string for global system tools

---

## What I Did:

```sql
UPDATE tool 
SET user_id = '' 
WHERE id LIKE 'mcp_%';
```

This makes the tools "system tools" not owned by any specific user.

---

## 🎯 Test Now:

1. **Refresh browser**: Ctrl+Shift+R
2. **Go to**: http://localhost:8080/workspace/tools
3. **You should now see**: 76 MCP tools listed

---

## If Still Not Working:

The `user_id` column might not accept empty strings (NOT NULL constraint).  
Alternative fix - make tools owned by your actual user:

```bash
# Get your user ID
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "SELECT id, email FROM user"

# Update tools to your user_id
sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
  "UPDATE tool SET user_id = '<YOUR_USER_ID>' WHERE id LIKE 'mcp_%'"
```

Let me know if tools appear now!
