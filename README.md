# opencode-acp-bridge

ACP server that proxies runs to a remote `opencode serve` instance.

Exposes an [ACP](https://agentcommunicationprotocol.com/)-compliant agent backed by an OpenCode HTTP server.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `ACP_HOST` | `127.0.0.1` | Bind host |
| `ACP_PORT` | `8000` | Bind port |
| `OPENCODE_URL` | `http://127.0.0.1:4096` | OpenCode server base URL |
| `OPENCODE_SERVER_USERNAME` | `opencode` | Basic auth username |
| `OPENCODE_SERVER_PASSWORD` | *(empty)* | Basic auth password |
| `OPENCODE_TIMEOUT_S` | `600.0` | Request timeout |
| `OPENCODE_WORKING_DIR` | *(empty)* | Optional working dir hint |
| `ACP_AGENT_NAME` | `opencode` | Exposed agent name |
| `ACP_AGENT_DESCRIPTION` | *(default)* | Exposed agent description |
| `ACP_REUSE_SESSIONS` | `true` | Reuse OpenCode sessions per ACP session |

## Run locally

```bash
uv run server.py
```
