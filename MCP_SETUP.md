# MCP Server Configuration Guide

## What are MCP Servers?

Model Context Protocol (MCP) servers extend Claude Code with specialized tools. This SEO AI OS includes three MCP servers:

1. **pagespeed-mcp** — PageSpeed Insights integration [OK] Working
2. **mcp-gsc** — Google Search Console integration [WARNING] Needs configuration
3. **fastmcp_server.py** — Custom FastMCP server [WARNING] Experimental

---

## Setup Instructions

### 1. PageSpeed Insights MCP (Recommended)

This adds a `pagespeed_analyze` tool directly to Claude Code.

**Location:** `tools/pagespeed-mcp/`

**Status:** [OK] Tests passing (6/6)

**Configuration:**

Add to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pagespeed": {
      "command": "node",
      "args": [
        "C:\\Users\\HP\\OneDrive\\Desktop\\SEO ai agency skills\\tools\\pagespeed-mcp\\dist\\index.js"
      ],
      "env": {
        "GOOGLE_API_KEY": "YOUR_GOOGLE_API_KEY_HERE"
      }
    }
  }
}
```

**Restart Claude Code** after adding this configuration.

**Usage:**
```
Ask Claude: "Analyze https://thedarenetwork.com with PageSpeed"
```

---

### 2. Google Search Console MCP

This would provide direct GSC data (impressions, clicks, queries) inside Claude Code.

**Location:** `tools/mcp-gsc/`

**Status:** [WARNING] Needs OAuth setup

**Setup Steps:**

1. **Enable GSC API** in Google Cloud Console:
   - Go to https://console.cloud.google.com/apis/library
   - Search for "Google Search Console API"
   - Click "Enable"

2. **Create OAuth 2.0 Credentials:**
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: Desktop app
   - Download credentials as `gsc_credentials.json`
   - Move to `tools/mcp-gsc/gsc_credentials.json`

3. **Run authentication:**
   ```bash
   cd tools/mcp-gsc
   python auth.py
   ```
   This will open a browser for you to authenticate.

4. **Add to Claude config:**
   ```json
   {
     "mcpServers": {
       "gsc": {
         "command": "python",
         "args": [
           "C:\\Users\\HP\\OneDrive\\Desktop\\SEO ai agency skills\\tools\\mcp-gsc\\gsc_server.py"
         ]
       }
     }
   }
   ```

**Usage:**
```
Ask Claude: "Get top 10 queries from GSC for thedarenetwork.com"
```

---

### 3. FastMCP Server (Experimental)

**Location:** `tools/fastmcp_server.py`

**Status:** [WARNING] Experimental, hangs on execution

**Note:** This is currently not functional. It appears to start a server and wait for connections. Consider removing or fixing if needed.

---

## Verifying MCP Setup

After configuration, restart Claude Code and run:

```
/mcp list
```

You should see your configured MCP servers listed.

---

## Troubleshooting

**MCP servers not showing up:**
- Check that the config file path is correct
- Verify JSON syntax (no trailing commas)
- Check absolute paths use double backslashes on Windows
- Restart Claude Code completely

**PageSpeed MCP not working:**
- Verify `GOOGLE_API_KEY` is set in the env section
- Run `npm test` in `tools/pagespeed-mcp/` to verify installation
- Check Node.js is installed: `node --version`

**GSC MCP authentication failing:**
- Ensure OAuth 2.0 credentials are type "Desktop app" (not Web app)
- Check `gsc_credentials.json` is in the correct location
- Run `python tools/mcp-gsc/auth.py` manually first

---

## Benefits of Using MCP

**Without MCP:**
```
You: "Check PageSpeed for thedarenetwork.com"
Claude: "I'll run the lighthouse_audit.py tool..."
*Runs Python script, waits 30s, reads JSON output*
```

**With MCP:**
```
You: "Check PageSpeed for thedarenetwork.com"
Claude: *Calls MCP tool directly, gets results in 5s*
```

**Advantages:**
- Faster execution (native tools vs. Python subprocess)
- Real-time data streaming
- Better error handling
- Reduced token usage (structured data vs. JSON parsing)

---

## Recommendation

**Priority 1:** Set up PageSpeed MCP (5 minutes, high value)
**Priority 2:** Set up GSC MCP (15 minutes, requires OAuth)
**Priority 3:** Remove or fix FastMCP server (low priority)

---

## Next Steps

After setup, update `CLAUDE.md` to reference these MCP tools in the workflow instructions. For example:

```markdown
### Step 4: Core Web Vitals Audit

**Preferred method:** Use PageSpeed MCP
- Ask: "Analyze [url] with PageSpeed for mobile and desktop"

**Fallback method:** Use lighthouse_audit.py
- Run: `python tools/lighthouse_audit.py --url [url] --strategy both`
```
