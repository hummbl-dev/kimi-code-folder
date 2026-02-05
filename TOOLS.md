# Tools Reference

> Complete reference for all built-in tools available to Kimi Code CLI.

---

## Overview

Kimi Code has access to 10 core tools organized into categories:

| Category | Tools |
|----------|-------|
| **File Operations** | `ReadFile`, `WriteFile`, `StrReplaceFile` |
| **Code Search** | `Grep`, `Glob` |
| **Shell** | `Shell` |
| **Web** | `SearchWeb`, `FetchURL` |
| **Media** | `ReadMediaFile` |
| **Subagents** | `Task` |

---

## File Operations

### `ReadFile`

Read text content from a file.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Path to the file |
| `line_offset` | number | ❌ | Line number to start reading from (1-indexed) |
| `n_lines` | number | ❌ | Number of lines to read (max 1000) |

**Usage Examples:**

```python
# Read entire file
ReadFile(path="src/index.ts")

# Read specific section (lines 45-60)
ReadFile(path="src/index.ts", line_offset=45, n_lines=15)

# Read first 50 lines
ReadFile(path="src/large-file.ts", n_lines=50)
```

**Best Practices:**
- Use `line_offset` + `n_lines` for large files to avoid loading unnecessary content
- Default limit is 1000 lines — use pagination for files exceeding this
- Always verify file exists before reading (use `Glob` first if unsure)

---

### `WriteFile`

Create a new file with specified content.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Path for the new file |
| `content` | string | ✅ | Content to write |
| `mode` | string | ❌ | `"overwrite"` (default) or `"append"` |

**Usage Examples:**

```python
# Create new file
WriteFile(
    path="src/utils.ts",
    content="export function formatDate(date: Date): string {\n  return date.toISOString();\n}"
)

# Append to existing file
WriteFile(
    path="log.txt",
    content="\nNew log entry",
    mode="append"
)
```

**Important:**
- Overwrites existing files without warning
- Creates parent directories if they don't exist
- Use `StrReplaceFile` for modifying existing files instead

---

### `StrReplaceFile`

Replace specific strings within a file using exact matching.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Path to the file |
| `edit` | object/array | ✅ | Replacement specification(s) |

**Edit Object Structure:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `old` | string | ✅ | Exact string to replace |
| `new` | string | ✅ | Replacement string |
| `replace_all` | boolean | ❌ | Replace all occurrences (default: false) |

**Usage Examples:**

```python
# Single replacement
StrReplaceFile(
    path="src/config.ts",
    edit={
        "old": "const API_URL = 'http://localhost:3000';",
        "new": "const API_URL = 'https://api.example.com';"
    }
)

# Multiple replacements in one call
StrReplaceFile(
    path="src/app.ts",
    edit=[
        {
            "old": "import { oldUtil } from './utils';",
            "new": "import { newUtil } from './utils';"
        },
        {
            "old": "console.log('Starting');",
            "new": "logger.info('Starting application');"
        }
    ]
)

# Replace all occurrences
StrReplaceFile(
    path="src/constants.ts",
    edit={
        "old": "OLD_VERSION",
        "new": "NEW_VERSION",
        "replace_all": True
    }
)
```

**⚠️ Critical: Exact Matching Required**

The `old` string must match **exactly**, including:
- Whitespace (spaces, tabs)
- Newlines
- Quote types (single vs double)

**Good Pattern:**
```python
# Always read first to get exact content
content = ReadFile(path="file.ts")
# Then use exact string from content
StrReplaceFile(path="file.ts", edit={"old": content, "new": newContent})
```

**Common Mistakes:**
```python
# ❌ Wrong - extra spaces
edit={"old": "function test()", "new": "..."}  # But file has "function test() "

# ❌ Wrong - wrong quotes
edit={"old": "import {x} from 'y'", "new": "..."}  # But file has "import {x} from \"y\""

# ✅ Correct - read first, match exactly
```

---

## Code Search

### `Grep`

Powerful search tool based on ripgrep for finding patterns in code.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | ✅ | Regex pattern to search |
| `path` | string | ❌ | Directory or file to search (default: current) |
| `glob` | string | ❌ | File pattern filter (e.g., `*.ts`, `*.{js,ts}`) |
| `type` | string | ❌ | File type (e.g., `py`, `js`, `ts`) |
| `-i` | boolean | ❌ | Case-insensitive search |
| `-n` | boolean | ❌ | Show line numbers |
| `-B` | number | ❌ | Lines to show before match |
| `-A` | number | ❌ | Lines to show after match |
| `-C` | number | ❌ | Lines to show before and after |
| `multiline` | boolean | ❌ | Enable multiline mode (dot matches newlines) |
| `output_mode` | string | ❌ | `"files_with_matches"`, `"content"`, or `"count_matches"` |
| `head_limit` | number | ❌ | Limit output to first N results |

**Usage Examples:**

```python
# Find all TODO comments
Grep(pattern="TODO|FIXME|XXX", output_mode="content", -n=True)

# Find function definitions in TypeScript
Grep(pattern="^function |^const .* = .*\(", type="ts", -n=True)

# Search for specific function
Grep(pattern="async function getUser", path="src", -n=True)

# Case-insensitive search
Grep(pattern="apikey|api_key", -i=True, output_mode="files_with_matches")

# Search with context (3 lines before/after)
Grep(pattern="class AuthService", -C=3, output_mode="content")

# Find files containing pattern (just filenames)
Grep(pattern="React\.lazy", output_mode="files_with_matches")

# Limit results
Grep(pattern="console\.log", head_limit=20, output_mode="content")

# Multiline search (find async functions with their bodies)
Grep(pattern="async function \w+\([^)]*\)\s*\{[^}]+\}", multiline=True)
```

**Output Modes:**
- `files_with_matches`: List of files containing matches (default)
- `content`: Show matching lines with context
- `count_matches`: Show count per file

---

### `Glob`

Find files and directories using glob patterns.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | ✅ | Glob pattern (e.g., `*.ts`, `src/**/*.js`) |
| `directory` | string | ❌ | Base directory (default: working directory) |
| `include_dirs` | boolean | ❌ | Include directories in results (default: true) |

**Usage Examples:**

```python
# Find all TypeScript files
Glob(pattern="*.ts")

# Find all test files recursively
Glob(pattern="**/*.test.ts")

# Find config files
Glob(pattern="*.config.{js,ts}")

# Find in specific directory
Glob(pattern="*.py", directory="/path/to/project")

# Find source files excluding tests
Glob(pattern="src/**/*.ts")

# List directory structure
Glob(pattern="*")
```

**Important Patterns:**
- `*` — Match any characters except `/`
- `**` — Match any characters including `/` (recursive)
- `?` — Match single character
- `{a,b}` — Match either `a` or `b`

**⚠️ Avoid:**
- Patterns starting with `**` (too broad)
- Patterns like `node_modules/**/*` (too many results)

---

## Shell

### `Shell`

Execute bash commands.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | ✅ | Bash command to execute |
| `timeout` | number | ❌ | Timeout in seconds (default: 60, max: 300) |

**Usage Examples:**

```python
# Run tests
Shell(command="npm test")

# Install dependencies
Shell(command="npm install")

# Check git status
Shell(command="git status")

# Run with timeout
Shell(command="npm run build", timeout=120)

# Multiple commands (chained)
Shell(command="cd src && npm run build")

# Check file existence
Shell(command="test -f config.json && echo 'exists' || echo 'not found'")

# Get disk space
Shell(command="df -h")
```

**Safety & Constraints:**
- Each call runs in a fresh shell environment
- No state persists between calls (use `&&` to chain)
- Current directory changes don't persist
- No superuser privileges
- 300-second maximum timeout

**Best Practices:**
```bash
# ✅ Chain related commands
Shell(command="cd /path && npm install && npm build")

# ✅ Conditional execution
Shell(command="command || echo 'Command failed'")

# ❌ Don't rely on cd persisting
Shell(command="cd /path")  # Next Shell call starts fresh
```

---

## Web Tools

### `SearchWeb`

Search the internet for information.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Search query |
| `limit` | number | ❌ | Number of results (default: 5, max: 20) |
| `include_content` | boolean | ❌ | Include page content (default: false) |

**Usage Examples:**

```python
# Quick search
SearchWeb(query="React 19 new features")

# More results
SearchWeb(query="TypeScript best practices 2024", limit=10)

# With content
SearchWeb(
    query="Next.js 14 app router migration guide",
    include_content=True,
    limit=3
)

# API documentation
SearchWeb(query="OpenAI API function calling documentation")

# Error research
SearchWeb(query="Node.js ECONNREFUSED error fix")
```

**Best Practices:**
- Use specific queries for better results
- Enable `include_content` when you need details
- Use `FetchURL` if you already know the URL

---

### `FetchURL`

Fetch content from a specific URL.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ | URL to fetch |

**Usage Examples:**

```python
# Fetch documentation
FetchURL(url="https://api.example.com/docs")

# Get latest release notes
FetchURL(url="https://github.com/facebook/react/releases/tag/v18.3.0")

# Check API status
FetchURL(url="https://status.example.com")

# Fetch raw file
FetchURL(url="https://raw.githubusercontent.com/user/repo/main/README.md")
```

---

## Media

### `ReadMediaFile`

Read image or video files.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Path to image or video file |

**Usage Examples:**

```python
# Read image
ReadMediaFile(path="assets/logo.png")

# Read screenshot
ReadMediaFile(path="screenshots/error.png")

# Read video
ReadMediaFile(path="recordings/demo.mp4")

# Read from URL (if supported)
ReadMediaFile(path="/Users/others/kimi-code-folder/assets/design.png")
```

**Limitations:**
- Maximum file size: 100MB
- Supported: Common image formats (PNG, JPG, GIF, WebP) and video formats

---

## Subagents

### `Task`

Spawn a subagent to perform a specific task with context isolation.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subagent_name` | string | ✅ | Type of subagent (usually `"coder"`) |
| `description` | string | ✅ | Brief task description (3-5 words) |
| `prompt` | string | ✅ | Detailed task with all context |

**Usage Examples:**

```python
# Analyze a specific module
Task(
    subagent_name="coder",
    description="Analyze auth module",
    prompt="""
    Analyze the authentication module at src/auth/.
    
    Focus on:
    1. How JWT tokens are handled
    2. Session management approach
    3. Security considerations
    
    Return a summary of findings.
    """
)

# Fix a specific bug
Task(
    subagent_name="coder",
    description="Fix login bug",
    prompt="""
    The login at src/routes/login.ts is failing with 'Invalid credentials'
    even for valid users. 
    
    Check:
    1. Password comparison logic
    2. Database query
    3. Error handling
    
    Fix the bug and return what was changed.
    """
)

# Research task
Task(
    subagent_name="coder",
    description="Research React patterns",
    prompt="""
    Search for the latest React Server Components best practices
    and patterns. Focus on:
    1. When to use Server vs Client components
    2. Data fetching patterns
    3. Common pitfalls
    
    Return a concise summary with code examples.
    """
)
```

**Key Characteristics:**
- Subagents have **no memory** of parent context
- Must provide **complete context** in the prompt
- Can run **in parallel** with other tools/subagents
- Return results to **parent only**

---

## Tool Combinations

### Common Patterns

**Exploring a Codebase:**
```python
# 1. Find structure
Glob(pattern="**/*.ts")

# 2. Check key config
ReadFile(path="package.json")

# 3. Search for patterns
Grep(pattern="export class|export function", type="ts")
```

**Fixing a Bug:**
```python
# 1. Find relevant code
Grep(pattern="function login|async function login", -n=True)

# 2. Read the function
ReadFile(path="src/auth.ts", line_offset=45, n_lines=30)

# 3. Read related tests
ReadFile(path="src/auth.test.ts")

# 4. Apply fix
StrReplaceFile(path="src/auth.ts", edit={...})

# 5. Verify
Shell(command="npm test -- auth.test.ts")
```

**Adding a Feature:**
```python
# 1. Research best practices
SearchWeb(query="React custom hooks best practices 2024")

# 2. Check existing patterns
Grep(pattern="^function use|^export function use", type="ts")

# 3. Create new file
WriteFile(path="src/hooks/useFeature.ts", content=...)

# 4. Update exports
StrReplaceFile(path="src/hooks/index.ts", edit={...})
```

**Multi-file Refactoring:**
```python
# Parallel subagents for independent parts
Task(subagent_name="coder", description="Refactor auth service", prompt=...)
Task(subagent_name="coder", description="Refactor user service", prompt=...)
Task(subagent_name="coder", description="Refactor API routes", prompt=...)
```

---

## Tool Selection Guide

| Goal | Primary Tool | Secondary Tools |
|------|--------------|-----------------|
| Read file contents | `ReadFile` | — |
| Create new file | `WriteFile` | — |
| Modify existing file | `StrReplaceFile` | `ReadFile` (first) |
| Find files by pattern | `Glob` | — |
| Search code content | `Grep` | `ReadFile` |
| Run command | `Shell` | — |
| Search web | `SearchWeb` | `FetchURL` |
| Get page content | `FetchURL` | — |
| View image/video | `ReadMediaFile` | — |
| Delegate complex task | `Task` | — |
