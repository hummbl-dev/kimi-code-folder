# Best Practices

> Patterns and anti-patterns for effective collaboration with Kimi Code CLI.

---

## Table of Contents

1. [Request Framing](#request-framing)
2. [Parallel Execution](#parallel-execution)
3. [Context Management](#context-management)
4. [Error Handling](#error-handling)
5. [File Operations](#file-operations)
6. [Subagent Usage](#subagent-usage)
7. [Testing and Verification](#testing-and-verification)

---

## Request Framing

### ✅ DO: Describe Outcomes

Focus on **what** you want to achieve, not **how** to implement it.

```
✅ "Add user authentication with email/password and session management"
✅ "Fix the bug where users get logged out after 5 minutes"
✅ "Make the API return proper error messages for validation failures"
```

### ❌ DON'T: Micromanage Implementation

Avoid prescribing exact implementation details.

```
❌ "Add `import passport from 'passport'` at line 1, then create a middleware 
    function at line 15 that checks req.session.userId..."
❌ "Use axios instead of fetch and add a try-catch block with console.error"
```

**Why:** Kimi Code chooses optimal tools and approaches based on the codebase context.

---

### ✅ DO: Provide Context

Give relevant background to help Kimi Code understand the problem.

```
✅ "The login is failing in production but works locally. The error message 
    is 'Invalid session token'. Check the auth middleware in src/middleware/auth.ts"
✅ "We need to support both light and dark themes. The current CSS is in 
    src/styles/theme.css using CSS variables"
```

### ❌ DON'T: Be Vague

Avoid requests that lack necessary context.

```
❌ "Fix the bug"
❌ "Make it better"
❌ "Update the code"
```

---

### ✅ DO: Specify Constraints

Clearly state what should or shouldn't be changed.

```
✅ "Refactor the auth logic but don't modify the public API interface"
✅ "Add tests for the new feature, but don't change existing tests"
✅ "Keep changes minimal — only fix the specific bug"
```

### ❌ DON'T: Assume Implicit Constraints

Don't assume Kimi Code knows unstated requirements.

```
❌ "Update the component" (without mentioning: "but keep the props interface unchanged")
❌ "Fix the build" (without mentioning: "we use pnpm not npm")
```

---

## Parallel Execution

### ✅ DO: Structure for Parallelism

Frame requests so independent operations can run simultaneously.

```
✅ "Fix the login bug in auth.ts, update the tests in auth.test.ts, 
    and add documentation to the README"
    
✅ "Check the API routes in src/routes/, analyze the database models 
    in src/models/, and review the middleware in src/middleware/"
    
✅ "Research the latest React patterns online and also check our 
    current implementation in the frontend folder"
```

**Result:** Multiple subagents or parallel tool calls execute simultaneously.

---

### ❌ DON'T: Force Sequential Dependencies

Avoid phrasing that creates artificial dependencies.

```
❌ "First read the config file, then based on what you find, read the 
    appropriate module file, then make changes"
    
❌ "Check file A, and if it contains X, then check file B, otherwise 
    check file C, then..."
```

**Better Approach:**
```
✅ "The config is in config.json. Read it along with src/modules/core.ts 
    and src/modules/optional.ts. Update all relevant files to match the new format."
```

---

### ✅ DO: Batch Independent Reads

When you need to examine multiple files, request them together.

```
✅ "Read src/auth.ts, src/user.ts, and src/session.ts to understand 
    the current authentication flow"
```

Kimi Code reads all three files in parallel.

---

## Context Management

### ✅ DO: Use Partial File Reads

For large files, read only the relevant sections.

```
✅ "Read lines 45-80 of src/server.ts where the middleware is defined"
✅ "Show me the first 50 lines of the config file"
```

**Tools:** `ReadFile` with `line_offset` and `n_lines`

---

### ❌ DON'T: Load Unnecessary Content

Avoid loading entire files when only a section is needed.

```
❌ "Read the entire 2000-line file" (when you only need one function)
```

---

### ✅ DO: Re-read Modified Files

After making changes, re-read to verify.

```
✅ "Update the function in utils.ts, then read the file to confirm the changes"
```

---

### ✅ DO: Use Grep for Discovery

Use `Grep` to find relevant code before reading files.

```
✅ "Search for all uses of the deprecated `getUser` function"
✅ "Find where the API_BASE_URL is defined"
```

---

## Error Handling

### ✅ DO: Provide Error Context

When reporting issues, include relevant details.

```
✅ "The build failed with this error: 'Module not found: ./utils'. 
    The import is in src/components/Header.tsx at line 12"
    
✅ "Tests are failing with timeout errors in auth.test.ts. 
    The tests were passing yesterday."
```

---

### ❌ DON'T: Report Vague Failures

Avoid unhelpful error reports.

```
❌ "It didn't work"
❌ "Something went wrong"
❌ "There's an error"
```

---

### ✅ DO: Set Expectations

Clarify what "success" looks like.

```
✅ "After fixing, the login should work with valid credentials 
    and reject invalid ones with a 401 status"
    
✅ "The component should display the user name and show a loading 
    state while fetching"
```

---

## File Operations

### ✅ DO: Read Before Replacing

Always read the file first to get exact content.

```python
# Good pattern
content = ReadFile(path="src/config.ts")
# Use exact string from content in replacement
StrReplaceFile(
    path="src/config.ts",
    edit={"old": exact_string_from_file, "new": new_content}
)
```

---

### ❌ DON'T: Guess Content

Never assume file content without reading.

```python
# ❌ Bad - might not match exactly
StrReplaceFile(
    path="src/config.ts",
    edit={"old": "const API_URL = 'http://localhost'", "new": "..."}
)
# Might fail if actual content has different spacing or quotes
```

---

### ✅ DO: Match Exactly

`StrReplaceFile` requires exact string matching.

```python
# ✅ Correct - exact match including whitespace
StrReplaceFile(
    path="file.ts",
    edit={
        "old": "function test() {\n  return true;\n}",
        "new": "function test() {\n  return false;\n}"
    }
)
```

---

### ❌ DON'T: Ignore Whitespace

Whitespace matters for exact matching.

```python
# ❌ Wrong - extra space
edit={"old": "function test()", "new": "..."}
# But file has: "function test() " (with trailing space)
```

---

### ✅ DO: Verify File Existence

Use `Glob` to check files before operations.

```python
# Check first
Glob(pattern="src/**/*.test.ts")
# Then operate on confirmed files
```

---

## Subagent Usage

### ✅ DO: Use Subagents for Isolation

Spawn subagents when you need fresh context.

```
✅ "Debug why my previous attempt at fixing the auth bug failed"
✅ "Research React Server Components while I check the current implementation"
```

---

### ✅ DO: Provide Complete Context

Subagents have no parent memory — include all necessary context.

```python
# ✅ Good - complete context
Task(
    subagent_name="coder",
    description="Fix auth bug",
    prompt="""
    Fix the authentication bug in src/auth.ts.
    
    Current behavior: Users with valid credentials get "Invalid token" error.
    Expected behavior: Valid credentials should allow login.
    
    The JWT verification happens in the verifyToken function.
    Check line 45-60 where the token is decoded.
    
    Return: What was fixed and the corrected code.
    """
)
```

---

### ❌ DON'T: Assume Shared Context

Subagents can't see parent conversation.

```python
# ❌ Bad - references undefined context
Task(
    prompt="Fix the bug I mentioned earlier"  # Subagent doesn't know!
)
```

---

### ✅ DO: Parallelize Independent Tasks

Use subagents for tasks that can run simultaneously.

```
✅ "Refactor the auth service, user service, and API gateway in parallel"
```

Spawns 3 subagents working independently.

---

### ❌ DON'T: Use Subagents for Simple Tasks

Don't add overhead for trivial operations.

```
❌ "Spawn a subagent to read this file and tell me its contents"
# Just use ReadFile directly
```

---

## Testing and Verification

### ✅ DO: Request Verification

Ask Kimi Code to verify changes.

```
✅ "Fix the bug and run the tests to verify"
✅ "Update the component and check that it renders correctly"
✅ "Refactor the code and ensure the build passes"
```

---

### ✅ DO: Specify Test Commands

Provide the correct test command if non-standard.

```
✅ "Run tests with `pnpm test:unit`"
✅ "Check the build with `npm run build:prod`"
```

---

### ✅ DO: Check Multiple Aspects

Verify related functionality.

```
✅ "Fix the API endpoint, then verify:
    1. The endpoint returns correct data
    2. Error handling works for invalid inputs
    3. Existing tests pass"
```

---

## Security Best Practices

### ✅ DO: Protect Sensitive Data

Don't expose credentials in requests.

```
✅ "Use the existing .env file for API keys"
✅ "The database URL is in the environment variable"
```

---

### ❌ DON'T: Share Secrets

Never include actual credentials in prompts.

```
❌ "Connect to the database at postgres://user:password123@host/db"
```

---

## Communication Patterns

### ✅ DO: Ask for Explanations

Request rationale when helpful.

```
✅ "Fix the bug and explain why it was happening"
✅ "Refactor this and tell me the benefits of the new approach"
```

---

### ✅ DO: Iterate

Break complex tasks into steps.

```
✅ "First, explore the codebase structure. Then we'll plan the refactoring."
✅ "Let's start with the authentication module, then move to authorization."
```

---

### ✅ DO: Correct Misunderstandings

Clarify if Kimi Code misinterprets.

```
✅ "Actually, I meant the frontend auth, not the backend"
✅ "The error happens on line 45, not line 54"
```

---

## Summary Checklist

When making a request, consider:

- [ ] Is the desired outcome clear?
- [ ] Is relevant context provided?
- [ ] Are constraints specified?
- [ ] Can independent parts run in parallel?
- [ ] Are file paths provided (or discoverable)?
- [ ] Is verification requested?
- [ ] Are secrets protected?

Following these practices leads to faster, more accurate results.
