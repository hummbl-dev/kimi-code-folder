# User Guide

> How to work effectively with Kimi Code CLI — from framing requests to leveraging advanced features.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Framing Effective Requests](#framing-effective-requests)
3. [Leveraging Parallel Execution](#leveraging-parallel-execution)
4. [When to Use Subagents](#when-to-use-subagents)
5. [Working with Skills](#working-with-skills)
6. [Error Handling](#error-handling)
7. [Common Patterns](#common-patterns)

---

## Getting Started

### What Kimi Code Can Do

- ✅ Read and modify code files
- ✅ Execute shell commands
- ✅ Search and analyze codebases
- ✅ Research on the web
- ✅ Deploy applications
- ✅ Process media (images, audio, video, PDFs)
- ✅ Spawn parallel subagents for complex tasks

### What to Expect

1. **Immediate execution** — No "yes/no" confirmation loops, Kimi Code acts directly
2. **Parallel work** — Multiple tasks run simultaneously when independent
3. **Transparent reasoning** — Explanations of what's being done and why
4. **Error reporting** — Clear diagnostics when things don't work

---

## Framing Effective Requests

### The Golden Rule: Outcome Over Implementation

Describe **what** you want to achieve, not **how** to do it.

| ❌ Avoid (Micromanaging) | ✅ Prefer (Outcome-focused) |
|--------------------------|----------------------------|
| "Add `import axios` at line 3, then use `axios.get()` in the `fetchData` function" | "Fetch data from the user API endpoint and handle errors" |
| "Create a file called `utils.ts` with a function `formatDate` that takes a Date and returns a string" | "Add date formatting utilities that support multiple locales" |
| "Use grep to find all TODO comments, then read each file" | "Find all TODO items in the codebase and summarize them" |

**Why this works:**
- Kimi Code chooses the best tools for the job
- More maintainable code (implementation details can be refined)
- Less back-and-forth for corrections

### Provide Context, Not Constraints

| ❌ Too Constrained | ✅ Context-Rich |
|-------------------|-----------------|
| "Fix the bug in `auth.ts`" | "Users are getting logged out after 5 minutes. The auth middleware is in `src/middleware/auth.ts`" |
| "Update the README" | "Add setup instructions for new developers. The project uses pnpm and requires Node 18+" |

### Be Specific About Scope

```
❌ "Make the app better"
✅ "Add form validation to the signup page and show inline error messages"

❌ "Fix all the issues"
✅ "Fix the TypeScript errors in the database connection module"
```

---

## Leveraging Parallel Execution

Kimi Code can execute multiple independent operations in parallel. Structure your requests to take advantage of this.

### Patterns That Enable Parallelism

**1. Multiple Independent Files**
```
✅ "Fix the auth bug in auth.ts, update the corresponding test in auth.test.ts, 
    and add a note to the CHANGELOG"
```
Result: Three parallel operations → Faster completion

**2. Exploration + Research**
```
✅ "Analyze the current routing structure in src/routes/ and also research 
    the latest React Router best practices"
```
Result: Local analysis and web research happen simultaneously

**3. Multi-Module Analysis**
```
✅ "Check how authentication works in the auth module, how sessions are 
    stored in the db module, and what the API routes expect in the routes module"
```
Result: Three code areas analyzed in parallel

### Patterns That Force Sequential Execution

```
❌ "Read the config file, and based on what you find, read the appropriate 
    module file, and then make changes"
```
This requires sequential execution because each step depends on the previous.

**Better approach:**
```
✅ "The config is in config.json. Read it, then also read src/modules/core.ts 
    and src/modules/optional.ts. Update both to match the new config format."
```
Now Kimi Code can read all files in parallel, then make changes.

---

## When to Use Subagents

Subagents are isolated workers spawned via the `Task` tool. They run in fresh contexts and return results to the parent.

### Use Subagents When:

| Scenario | Example |
|----------|---------|
| **Independent tasks** | "Fix these 3 unrelated bugs in different files" |
| **Context isolation** | "Debug why my previous approach failed" |
| **Large codebase exploration** | "Analyze the frontend, backend, and database layers separately" |
| **Research tasks** | "Search for the latest React patterns and also check our current implementation" |
| **Complex multi-file refactoring** | "Refactor auth in 5 different services" |

### Don't Use Subagents When:

| Scenario | Why Not |
|----------|---------|
| Simple single-file edits | Direct execution is faster |
| Sequential dependent tasks | Parent maintains context better |
| Quick questions | Overhead exceeds benefit |
| Tasks requiring continuous shared state | Subagents can't communicate |

### Example: Subagent Delegation

```
User: "I need to refactor the authentication across 3 services: 
       auth-service, user-service, and api-gateway. 
       Each has its own auth logic that needs to be consolidated."

Kimi Code spawns 3 subagents:
├─ Subagent 1: Analyze auth-service
├─ Subagent 2: Analyze user-service
└─ Subagent 3: Analyze api-gateway

Each returns findings → Parent synthesizes consolidation plan
```

---

## Working with Skills

Skills are specialized capabilities stored at `~/.codex/skills/*/SKILL.md`.

### How Skills Are Triggered

**Automatic Detection:**
```
User: "Deploy this to Vercel"
→ Kimi Code detects "deploy" + "Vercel" context
→ Reads vercel-deploy/SKILL.md
→ Follows documented workflow
```

**Explicit Request:**
```
User: "Use the imagegen skill to create a logo"
→ Kimi Code reads imagegen/SKILL.md
→ Uses the bundled scripts
```

### Common Skill Patterns

| If You Want... | Mention... | Skill Used |
|----------------|------------|------------|
| Deploy a website | "Deploy to Vercel" | vercel-deploy |
| Generate an image | "Create an image of..." | imagegen |
| Convert text to speech | "Generate audio narration" | speech |
| Process a PDF | "Extract text from this PDF" | pdf |
| Automate browser testing | "Test this login flow" | playwright |
| Generate a video | "Create a video of..." | sora |
| Transcribe audio | "Transcribe this recording" | transcribe |

### Skills Requiring Authentication

Some skills need API keys:

| Skill | Required Env Var |
|-------|------------------|
| imagegen | `OPENAI_API_KEY` |
| speech | `OPENAI_API_KEY` |
| sora | `OPENAI_API_KEY` |
| sentry | `SENTRY_AUTH_TOKEN` |

If a skill fails due to missing auth, Kimi Code will report what's needed.

---

## Error Handling

### How Kimi Code Handles Errors

1. **Transient Errors** (network, file locked)
   - Automatically retries
   - Reports if retry fails

2. **Logic Errors** (wrong file, incorrect replacement)
   - Analyzes what went wrong
   - Adapts approach
   - Retries with correction

3. **Fundamental Blockers** (missing dependencies, unclear requirements)
   - Reports clearly to user
   - Provides diagnostic information
   - Suggests next steps

### What You Should Do

**When errors occur, provide:**
- The error message
- What you expected to happen
- Any relevant context

**Example:**
```
❌ "It didn't work"
✅ "The deployment failed with 'Build command not found'. 
    The project uses pnpm and the build script should be 'pnpm build'"
```

---

## Common Patterns

### Pattern 1: Codebase Exploration

```
"Explore this codebase and tell me:
1. What frameworks/libraries are used
2. How the project is structured
3. Where the main business logic lives"
```

Kimi Code will:
1. `Glob` for key files (package.json, tsconfig.json, etc.)
2. `ReadFile` on configuration and entry points
3. `Grep` for common patterns
4. Synthesize findings

### Pattern 2: Bug Fix with Tests

```
"The login is failing with 'Invalid credentials' even with correct passwords.
Fix the bug and update the tests in auth.test.ts."
```

Kimi Code will:
1. Search for login-related code
2. Read the auth implementation
3. Read the test file
4. Identify and fix the bug
5. Update tests
6. Run tests to verify

### Pattern 3: Feature Addition

```
"Add pagination to the user list API. It should accept page and limit 
query parameters and return paginated results with metadata."
```

Kimi Code will:
1. Find the user list endpoint
2. Examine current implementation
3. Add pagination logic
4. Update or add tests
5. Verify the changes

### Pattern 4: Research + Implementation

```
"What's the current best practice for handling env vars in Next.js 14? 
Then update our project to follow it."
```

Kimi Code will:
1. `SearchWeb` for current best practices
2. `ReadFile` on current env handling
3. Implement changes based on research

### Pattern 5: Deployment

```
"Deploy this Next.js app to Vercel with preview deployments enabled."
```

Kimi Code will:
1. Read vercel-deploy skill
2. Check project structure
3. Create/verify vercel.json
4. Deploy to Vercel

---

## Quick Tips

| Tip | Why It Helps |
|-----|--------------|
| Start with high-level requests | Kimi Code can figure out the details |
| Mention file paths if you know them | Saves exploration time |
| Specify constraints explicitly | "Don't modify tests" or "Keep changes minimal" |
| Ask for explanations if curious | Kimi Code can explain its reasoning |
| Use todo lists for complex tasks | Kimi Code will track progress |
| Provide error context | Faster resolution |
