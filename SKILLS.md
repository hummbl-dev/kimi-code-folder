# Skills Catalog

> Complete reference for all 33+ specialized skills available to Kimi Code CLI.

---

## What Are Skills?

Skills are modular capabilities stored at `~/.codex/skills/*/SKILL.md` that extend Kimi Code's functionality for specific domains. Each skill contains:

- **Documentation** on how to use the capability
- **Workflow guidance** for complex tasks
- **Bundled scripts** or tools when needed
- **Configuration requirements** (e.g., API keys)

---

## Quick Reference

| Category | Skills | Common Trigger |
|----------|--------|----------------|
| **Deployment** | 4 skills | "Deploy to [platform]" |
| **Media** | 6 skills | "Generate image/video/audio" |
| **GitHub** | 3 skills | "Fix CI", "Address PR comments" |
| **Notion** | 4 skills | "Document in Notion" |
| **Security** | 3 skills | "Security review", "Threat model" |
| **DevTools** | 4 skills | "Browser test", "Notebook" |
| **Integrations** | 6 skills | "Linear", "Figma", "Sentry" |
| **Other** | 3 skills | "Web game", "Git workflow" |

---

## Deployment Skills

### `vercel-deploy`

Deploy applications to Vercel.

**When to Use:**
- Deploying Next.js, React, or other frontend apps
- Setting up preview deployments
- Configuring custom domains
- Managing Vercel projects

**Trigger:**
```
"Deploy this to Vercel"
"Set up Vercel preview deployments"
"Configure Vercel for this project"
```

**Requirements:**
- Vercel CLI installed or accessible
- Vercel account

---

### `netlify-deploy`

Deploy web projects to Netlify.

**When to Use:**
- Deploying static sites
- Setting up Netlify Functions
- Managing Netlify deployments

**Trigger:**
```
"Deploy to Netlify"
"Set up Netlify for this static site"
```

---

### `cloudflare-deploy`

Deploy to Cloudflare Workers and Pages.

**When to Use:**
- Deploying serverless Workers
- Setting up Cloudflare Pages
- Configuring edge functions

**Trigger:**
```
"Deploy to Cloudflare Workers"
"Set up Cloudflare Pages"
```

---

### `render-deploy`

Deploy applications to Render.

**When to Use:**
- Deploying web services
- Setting up databases on Render
- Configuring Blueprints

**Trigger:**
```
"Deploy to Render"
"Create a render.yaml for this project"
```

---

## Media Skills

### `imagegen`

Generate images via OpenAI's Image API (DALL-E).

**When to Use:**
- Creating logos, illustrations
- Generating concept art
- Product shots with transparent backgrounds
- Batch image generation

**Trigger:**
```
"Generate an image of..."
"Create a logo for..."
"Make a product shot with transparent background"
```

**Requirements:**
- `OPENAI_API_KEY` environment variable
- Valid OpenAI API access

**Features:**
- Multiple image sizes (1024x1024, 1792x1024, 1024x1792)
- Style variations
- Background removal/replacement
- Batch generation support

---

### `speech`

Text-to-speech conversion via OpenAI Audio API.

**When to Use:**
- Generating voiceovers
- Accessibility narration
- Audio prompts
- Batch speech generation

**Trigger:**
```
"Generate audio narration for..."
"Convert this text to speech"
"Create a voiceover"
```

**Requirements:**
- `OPENAI_API_KEY` environment variable

**Features:**
- Multiple built-in voices
- Various output formats
- Batch processing

**Note:** Custom voice creation is not supported.

---

### `sora`

AI video generation via OpenAI's video API.

**When to Use:**
- Creating AI-generated videos
- Video remixing
- Batch video generation

**Trigger:**
```
"Generate a video of..."
"Create an AI video"
"Remix this video with..."
```

**Requirements:**
- `OPENAI_API_KEY` environment variable
- Sora API access

**Features:**
- Text-to-video generation
- Video remixing
- Download videos/thumbnails/spritesheets
- Batch generation

---

### `transcribe`

Audio transcription with optional diarization.

**When to Use:**
- Transcribing interviews
- Converting meetings to text
- Extracting speech from recordings
- Speaker identification

**Trigger:**
```
"Transcribe this audio file"
"Convert this recording to text"
"Extract the transcript from..."
```

**Features:**
- Speaker diarization (who spoke when)
- Known-speaker hints
- Multiple audio formats
- Timestamps

---

### `pdf`

PDF generation and processing.

**When to Use:**
- Creating PDFs from documents
- Extracting text from PDFs
- PDF manipulation
- Layout-sensitive document generation

**Trigger:**
```
"Generate a PDF from..."
"Extract text from this PDF"
"Create a formatted PDF document"
```

**Tools:**
- `reportlab` for generation
- `pdfplumber` and `pypdf` for extraction
- Visual verification via rendering

---

### `screenshot`

System-level screenshot capture.

**When to Use:**
- Capturing full screen
- Specific window captures
- Region captures
- When tool-specific capture is unavailable

**Trigger:**
```
"Take a screenshot"
"Capture this window"
"Screenshot the current screen"
```

**Note:** This is OS-level capture, different from browser screenshots via Playwright.

---

## GitHub Skills

### `gh-fix-ci`

Debug and fix failing GitHub Actions PR checks.

**When to Use:**
- PR checks are failing in GitHub Actions
- Need to analyze CI logs
- Debug test failures in CI

**Trigger:**
```
"Fix the failing CI checks"
"Debug why the GitHub Actions are failing"
"The PR checks are red, help fix them"
```

**Workflow:**
1. Uses `gh` CLI to inspect checks
2. Fetches and analyzes logs
3. Summarizes failures
4. Drafts fix plan
5. Implements with user approval

**Note:** External CI providers (Buildkite, etc.) are out of scope.

---

### `gh-address-comments`

Address review comments on open GitHub PRs.

**When to Use:**
- Responding to PR review feedback
- Implementing requested changes
- Managing review threads

**Trigger:**
```
"Address the review comments on my PR"
"Help me respond to these code review comments"
"Implement the changes requested in the review"
```

**Requirements:**
- `gh` CLI authenticated
- Open PR on current branch

---

### `yeet`

One-flow git operations: stage, commit, push, and open PR.

**When to Use:**
- Quick PR creation
- Standard git workflow
- Single-command git operations

**Trigger:**
```
"Yeet these changes"
"Stage, commit, push, and open a PR"
```

**Workflow:**
1. `git add`
2. `git commit`
3. `git push`
4. `gh pr create`

---

## Notion Skills

### `notion-knowledge-capture`

Capture conversations and decisions into structured Notion pages.

**When to Use:**
- Turning chats into wiki entries
- Documenting how-tos
- Recording decisions
- Creating FAQs

**Trigger:**
```
"Document this in Notion"
"Capture this conversation to our wiki"
"Create a Notion page for this decision"
```

---

### `notion-meeting-intelligence`

Prepare meeting materials with Notion context.

**When to Use:**
- Preparing meeting agendas
- Gathering context for attendees
- Drafting pre-reads
- Tailoring materials to participants

**Trigger:**
```
"Prepare meeting materials for..."
"Draft an agenda for the team meeting"
"Gather context for this meeting"
```

---

### `notion-research-documentation`

Research across Notion and synthesize documentation.

**When to Use:**
- Gathering info from multiple Notion sources
- Creating briefs
- Building comparisons
- Writing reports with citations

**Trigger:**
```
"Research our Notion docs and create a brief"
"Synthesize information from our wiki"
```

---

### `notion-spec-to-implementation`

Turn Notion specs into implementation plans.

**When to Use:**
- Implementing PRDs/feature specs
- Creating implementation plans
- Tracking progress from specs

**Trigger:**
```
"Turn this Notion spec into an implementation plan"
"Create tasks from this product spec"
```

---

## Security Skills

### `security-best-practices`

Language/framework-specific security reviews.

**When to Use:**
- Security review requests
- Secure-by-default coding
- Security report generation

**Trigger:**
```
"Do a security review of this code"
"Check for security best practices"
```

**Supported Languages:**
- Python
- JavaScript/TypeScript
- Go

---

### `security-ownership-map`

Analyze git repos for security ownership topology.

**When to Use:**
- Bus factor analysis
- Security maintainer identification
- CODEOWNERS reality checks
- Orphaned sensitive code detection

**Trigger:**
```
"Analyze security ownership for this repo"
"Who owns the sensitive code?"
"Check bus factor for security-critical files"
```

**Outputs:**
- CSV/JSON for graph databases
- Visualization data
- Ownership clusters

---

### `security-threat-model`

Repository-grounded threat modeling.

**When to Use:**
- Threat modeling a codebase
- Enumerating threats/abuse paths
- AppSec threat modeling

**Trigger:**
```
"Create a threat model for this application"
"What are the security threats to this system?"
"Enumerate abuse paths"
```

**Outputs:**
- Markdown threat model document
- Trust boundaries
- Assets and attacker capabilities
- Mitigations

---

## DevTools Skills

### `playwright`

Browser automation via Playwright.

**When to Use:**
- Automating browser from terminal
- UI flow debugging
- Form filling and navigation
- Screenshots and snapshots
- Data extraction

**Trigger:**
```
"Test this login flow"
"Take a screenshot of the webpage"
"Automate this browser interaction"
```

**Features:**
- Navigation
- Form filling
- Screenshots
- Console error inspection
- Data extraction

---

### `jupyter-notebook`

Create, scaffold, and edit Jupyter notebooks.

**When to Use:**
- Creating experiment notebooks
- Building tutorials
- Data exploration
- Educational content

**Trigger:**
```
"Create a Jupyter notebook for..."
"Scaffold a new notebook"
```

---

### `spreadsheet`

Create, edit, analyze, and format spreadsheets.

**When to Use:**
- Creating Excel/CSV files
- Data analysis with pandas
- Preserving formulas and formatting
- Complex spreadsheet operations

**Trigger:**
```
"Create a spreadsheet with..."
"Analyze this CSV data"
"Format this Excel file"
```

**Formats:**
- `.xlsx` (Excel)
- `.csv`
- `.tsv`

---

### `doc`

Read, create, and edit Word documents.

**When to Use:**
- Creating .docx files
- Format-sensitive document editing
- Layout fidelity matters

**Trigger:**
```
"Create a Word document for..."
"Edit this .docx file"
```

---

## Integration Skills

### `linear`

Manage issues, projects, and team workflows in Linear.

**When to Use:**
- Reading/creating Linear tickets
- Updating issues
- Project management

**Trigger:**
```
"Create a Linear ticket for..."
"Check my Linear issues"
"Update ticket LIN-123"
```

---

### `figma`

Fetch design context, screenshots, and assets from Figma.

**When to Use:**
- Getting design specs
- Fetching Figma assets
- Design-to-code workflow
- Accessing Figma variables

**Trigger:**
```
"Get the design from Figma"
"Fetch assets from this Figma file"
```

---

### `figma-implement-design`

Translate Figma designs to production code.

**When to Use:**
- Implementing Figma designs
- Design-to-code with 1:1 fidelity
- Building components from Figma specs

**Trigger:**
```
"Implement this Figma design"
"Convert this Figma file to code"
"Build this component from Figma"
```

**Requirements:**
- Figma MCP server connection
- Valid Figma URLs/node IDs

---

### `sentry`

Inspect Sentry issues and events.

**When to Use:**
- Checking production errors
- Summarizing recent issues
- Pulling Sentry health data

**Trigger:**
```
"Check Sentry for recent errors"
"What's failing in production?"
"Summarize Sentry issues"
```

**Requirements:**
- `SENTRY_AUTH_TOKEN` environment variable

**Limitations:**
- Read-only queries only

---

### `openai-docs`

Access up-to-date OpenAI documentation.

**When to Use:**
- Building with OpenAI APIs
- Latest API documentation
- Model capabilities and limits

**Trigger:**
```
"How do I use the Responses API?"
"What's the latest on Codex?"
"Chat Completions documentation"
```

**Features:**
- Official documentation with citations
- API references
- Prioritizes OpenAI docs MCP tools

---

## Specialized Skills

### `develop-web-game`

Web game development with HTML/JS.

**When to Use:**
- Building browser-based games
- Game testing with Playwright
- Implementing game mechanics

**Trigger:**
```
"Create a web game"
"Build a simple browser game"
```

**Features:**
- Playwright-based testing
- Short input bursts with pauses
- Console error inspection
- Text rendering for game state

---

### `kimi-cli-help`

Kimi Code CLI usage and troubleshooting.

**When to Use:**
- Kimi CLI questions
- Configuration help
- Provider setup
- MCP integration issues

**Trigger:**
```
"How do I configure Kimi Code?"
"Kimi CLI troubleshooting"
```

---

### `skill-creator`

Guide for creating effective skills.

**When to Use:**
- Creating new skills
- Updating existing skills
- Extending Kimi Code capabilities

**Trigger:**
```
"Help me create a new skill"
"How do I extend Kimi Code?"
```

---

## Skill Selection Guide

| If User Wants To... | Suggest Skill |
|---------------------|---------------|
| Deploy a web app | `vercel-deploy`, `netlify-deploy`, `cloudflare-deploy`, `render-deploy` |
| Create media (image/video/audio) | `imagegen`, `sora`, `speech`, `transcribe` |
| Fix GitHub issues | `gh-fix-ci`, `gh-address-comments`, `yeet` |
| Document in Notion | `notion-*` skills |
| Security review | `security-best-practices`, `security-threat-model` |
| Automate browser | `playwright` |
| Process documents | `pdf`, `doc`, `spreadsheet` |
| Work with Figma | `figma`, `figma-implement-design` |
| Track issues | `linear` |
| Monitor errors | `sentry` |
| Build a game | `develop-web-game` |

---

## Authentication Requirements Summary

| Skill | Required Environment Variable |
|-------|-------------------------------|
| imagegen | `OPENAI_API_KEY` |
| speech | `OPENAI_API_KEY` |
| sora | `OPENAI_API_KEY` |
| sentry | `SENTRY_AUTH_TOKEN` |
| Most others | None (uses CLI tools or MCP) |

When authentication is missing, Kimi Code will report:
```
The [skill] requires [ENV_VAR]. Please set it and try again.
```
