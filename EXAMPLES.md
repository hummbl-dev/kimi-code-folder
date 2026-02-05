# Examples

> Good vs. bad request patterns with explanations and expected outcomes.

---

## Table of Contents

1. [Code Exploration](#code-exploration)
2. [Bug Fixes](#bug-fixes)
3. [Feature Addition](#feature-addition)
4. [Refactoring](#refactoring)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Research Tasks](#research-tasks)

---

## Code Exploration

### Scenario: Understanding a New Codebase

#### ❌ Bad Request
```
"Tell me about this codebase."
```

**Problems:**
- Too vague — what specifically to look for?
- No guidance on depth or focus areas
- Hard to provide useful response

---

#### ✅ Good Request
```
"Explore this codebase and tell me:
1. What tech stack is used (frameworks, main dependencies)
2. The overall project structure
3. Where the main business logic lives (API routes, services, etc.)
4. How authentication is handled

Focus on the src/ directory."
```

**What Kimi Code Does:**
1. `Glob` to find key config files (package.json, tsconfig.json, etc.)
2. `ReadFile` on configuration files
3. `Grep` for common patterns (exports, routes, auth)
4. Provides structured overview

**Result:** Actionable understanding of the codebase.

---

### Scenario: Finding Specific Code

#### ❌ Bad Request
```
"Find the login code."
```

**Problems:**
- "Login" could mean many things (UI, API, auth logic, etc.)
- No guidance on what aspect to focus on

---

#### ✅ Good Request
```
"Find where the JWT token validation happens in the backend. 
I'm looking for the middleware or function that verifies tokens 
and sets the user context."
```

**What Kimi Code Does:**
1. `Grep` for patterns like "verify", "jwt", "token", "middleware"
2. `ReadFile` on matching files
3. Identifies the validation logic

**Result:** Pinpoints the exact code responsible for token validation.

---

## Bug Fixes

### Scenario: Authentication Failure

#### ❌ Bad Request
```
"Fix the auth bug."
```

**Problems:**
- No information about symptoms
- Don't know which auth component
- No reproduction steps

---

#### ✅ Good Request
```
"Users are getting 'Invalid session' errors when trying to access 
protected routes, even though they just logged in successfully. 

The error seems to happen in the auth middleware. Check:
1. src/middleware/auth.ts - the token verification logic
2. How the session is being stored and retrieved
3. Token expiration handling

Fix the bug and add a test case to prevent regression."
```

**What Kimi Code Does:**
1. `ReadFile` on auth.ts
2. `Grep` for session/token related code
3. Identifies the issue (e.g., token expiration check wrong)
4. `StrReplaceFile` to fix
5. `ReadFile` on test file
6. `StrReplaceFile` to add test
7. `Shell` to run tests

**Result:** Bug fixed with regression test.

---

### Scenario: API Error Handling

#### ❌ Bad Request
```
"The API is broken. Fix it."
```

**Problems:**
- No error details
- "Broken" is not actionable
- No scope defined

---

#### ✅ Good Request
```
"The user creation API endpoint is returning 500 errors instead of 
validation errors. When I POST to /api/users with invalid data 
(missing email), it should return 400 with a clear error message, 
but it's crashing.

Check:
1. src/routes/users.ts - the route handler
2. src/validators/user.ts - the validation logic
3. Error handling in the route

Make sure validation errors are caught and returned as 400 responses 
with descriptive messages."
```

**What Kimi Code Does:**
1. `ReadFile` on the route and validator
2. Identifies missing try-catch or validation
3. Adds proper error handling
4. Tests the fix

**Result:** Proper error handling with appropriate status codes.

---

## Feature Addition

### Scenario: Adding Pagination

#### ❌ Bad Request
```
"Add pagination to the API."
```

**Problems:**
- Which endpoint(s)?
- What pagination style?
- What parameters?

---

#### ✅ Good Request
```
"Add pagination to the GET /api/users endpoint. 

Requirements:
- Accept `page` (default 1) and `limit` (default 20, max 100) query params
- Return paginated results with metadata: { data: [], pagination: { page, limit, total, totalPages } }
- Maintain backward compatibility

Files to modify:
- src/routes/users.ts - the route handler
- Update or add tests in src/routes/users.test.ts

Follow the existing code style in the project."
```

**What Kimi Code Does:**
1. `ReadFile` on current implementation
2. `Grep` for existing pagination patterns
3. Implements pagination with metadata
4. Updates tests
5. Verifies backward compatibility

**Result:** Properly paginated endpoint with tests.

---

### Scenario: New Component

#### ❌ Bad Request
```
"Create a user profile component."
```

**Problems:**
- What framework? (React, Vue, etc.)
- What data should it display?
- Where should it go?

---

#### ✅ Good Request
```
"Create a UserProfile component in React that displays user information.

Requirements:
- Props: user (User type), onEdit callback
- Display: name, email, avatar, join date
- Show loading state while user data is being fetched
- Handle error state if user fails to load
- Use the existing UI components from src/components/ui/
- Follow the project pattern (check src/components/Card.tsx for reference)

Create:
1. src/components/UserProfile.tsx - the component
2. src/components/UserProfile.test.tsx - tests
3. Update src/components/index.ts to export it"
```

**What Kimi Code Does:**
1. `ReadFile` on existing components for patterns
2. `ReadFile` on UI component library
3. Creates UserProfile.tsx with proper structure
4. Creates tests
5. Updates exports

**Result:** Complete, tested component following project conventions.

---

## Refactoring

### Scenario: Extracting Reusable Logic

#### ❌ Bad Request
```
"Clean up the code."
```

**Problems:**
- What "clean up" means is subjective
- No specific targets
- No success criteria

---

#### ✅ Good Request
```
"Extract the date formatting logic that's duplicated across the codebase 
into a reusable utility.

I noticed these patterns:
- src/components/Post.tsx has date formatting
- src/components/Comment.tsx has similar formatting  
- src/utils/report.ts also formats dates

Create:
1. src/utils/date.ts with formatDate, formatRelativeDate functions
2. Use date-fns library (already in package.json)
3. Update all existing places to use the new utility
4. Don't change the output format - keep it the same
5. Add tests for the utility functions"
```

**What Kimi Code Does:**
1. `Grep` to find all date formatting code
2. `ReadFile` on each occurrence
3. `WriteFile` for the new utility
4. `StrReplaceFile` to update all usages
5. Creates tests

**Result:** DRY code with reusable utility and tests.

---

### Scenario: Multi-File Refactoring

#### ❌ Bad Request
```
"Refactor all the API calls to use a new pattern."
```

**Problems:**
- What new pattern?
- Which API calls?
- No specific guidance

---

#### ✅ Good Request
```
"Refactor the API layer to use a centralized apiClient instead of 
direct fetch calls.

Current state:
- Direct fetch calls scattered in src/services/
- Each handles auth headers separately
- Error handling is inconsistent

Target state:
- Use src/lib/apiClient.ts (already exists) for all API calls
- Remove duplicate auth header logic
- Consistent error handling through the client

Files to refactor (parallelize where possible):
1. src/services/auth.ts
2. src/services/user.ts
3. src/services/posts.ts

Keep the public interface of each service the same - just change 
internal implementation."
```

**What Kimi Code Does:**
1. Spawns subagents for each service file (parallel)
2. Each subagent refactors one file
3. Parent synthesizes results
4. Verifies no breaking changes

**Result:** Refactored API layer with consistent patterns.

---

## Testing

### Scenario: Adding Test Coverage

#### ❌ Bad Request
```
"Add more tests."
```

**Problems:**
- Which areas?
- What type of tests?
- How much coverage?

---

#### ✅ Good Request
```
"Add unit tests for the authentication utilities in src/utils/auth.ts.

Functions to test:
- hashPassword(password): returns hashed string
- verifyPassword(password, hash): returns boolean
- generateToken(payload): returns JWT string
- verifyToken(token): returns decoded payload or throws

Test cases needed:
- Success cases for each function
- Error cases (wrong password, invalid token, expired token)
- Edge cases (empty input, special characters)

Use the existing test setup (Jest). Check src/utils/validation.test.ts 
for the testing pattern used in this project."
```

**What Kimi Code Does:**
1. `ReadFile` on auth.ts to understand functions
2. `ReadFile` on existing test for patterns
3. `WriteFile` for auth.test.ts with comprehensive cases
4. `Shell` to run tests

**Result:** Comprehensive test coverage for auth utilities.

---

### Scenario: Fixing Flaky Tests

#### ❌ Bad Request
```
"The tests are flaky. Make them stable."
```

**Problems:**
- Which tests?
- What flakiness patterns?
- No examples

---

#### ✅ Good Request
```
"The tests in src/components/UserList.test.tsx are flaky - they fail 
intermittently with timeout errors.

Observed patterns:
- Fails about 30% of the time in CI
- Error: 'Unable to find element with data-testid="user-list"'
- Seems to happen when the user list takes time to load

Check:
1. How the component fetches data
2. If async operations are properly awaited in tests
3. If there are proper loading state checks
4. Mock data setup

Make the tests reliable without increasing timeout values."
```

**What Kimi Code Does:**
1. `ReadFile` on the component
2. `ReadFile` on the test file
3. Identifies missing `waitFor` or `findBy` queries
4. Fixes async handling
5. Verifies stability

**Result:** Stable, properly async-aware tests.

---

## Deployment

### Scenario: First Deployment

#### ❌ Bad Request
```
"Deploy this."
```

**Problems:**
- To which platform?
- What configuration needed?
- What are the requirements?

---

#### ✅ Good Request
```
"Deploy this Next.js application to Vercel.

Project details:
- Framework: Next.js 14 with App Router
- Build command: next build (standard)
- Environment variables needed:
  - DATABASE_URL (production database)
  - NEXTAUTH_SECRET (for auth)
  - API_BASE_URL
- Output: static export not needed (using SSR)

Requirements:
1. Set up Vercel project
2. Configure environment variables
3. Enable preview deployments for PRs
4. Custom domain: myapp.example.com (add to Vercel config)

Use the vercel-deploy skill."
```

**What Kimi Code Does:**
1. Reads vercel-deploy skill
2. Checks project structure
3. Creates/verifies vercel.json
4. Deploys to Vercel
5. Configures environment variables

**Result:** Deployed application with proper configuration.

---

### Scenario: CI/CD Setup

#### ❌ Bad Request
```
"Set up CI/CD."
```

**Problems:**
- Which platform?
- What workflows?
- What triggers?

---

#### ✅ Good Request
```
"Set up GitHub Actions for this project.

Required workflows:
1. CI (on every PR):
   - Install dependencies (pnpm)
   - Run linting
   - Run type checking
   - Run tests
   - Build the project

2. Deploy (on push to main):
   - Run all CI checks
   - Deploy to Vercel (production)

Project uses:
- pnpm (not npm/yarn)
- Node.js 18
- Next.js with TypeScript

Create:
- .github/workflows/ci.yml
- .github/workflows/deploy.yml"
```

**What Kimi Code Does:**
1. `WriteFile` for CI workflow
2. `WriteFile` for deploy workflow
3. Uses pnpm commands
4. Sets up proper triggers

**Result:** Complete CI/CD pipeline.

---

## Research Tasks

### Scenario: Technology Evaluation

#### ❌ Bad Request
```
"Should we use X or Y?"
```

**Problems:**
- No context on requirements
- No constraints
- What decision criteria?

---

#### ✅ Good Request
```
"Research state management solutions for our React project.

Current situation:
- Medium-sized app with ~50 components
- Current: Prop drilling getting unwieldy
- Team: 5 developers, varying experience levels
- Requirements:
  - Server state caching (API calls)
  - Client state (UI state, forms)
  - Good TypeScript support
  - Easy to learn

Compare:
1. Redux Toolkit + RTK Query
2. Zustand + TanStack Query
3. Context API only

For each, analyze:
- Learning curve
- Boilerplate amount
- Performance characteristics
- Ecosystem/tooling
- Migration effort from current state

Provide a recommendation with justification."
```

**What Kimi Code Does:**
1. `SearchWeb` for latest information on each option
2. `FetchURL` for official documentation
3. Analyzes tradeoffs
4. Provides structured comparison
5. Makes recommendation

**Result:** Informed decision with clear rationale.

---

### Scenario: API Integration Research

#### ❌ Bad Request
```
"How do I use the Stripe API?"
```

**Problems:**
- Too broad
- What specific integration?
- What language/framework?

---

#### ✅ Good Request
```
"Research integrating Stripe payments into our Next.js application.

Specific needs:
1. One-time payments for product purchases
2. Save payment methods for future use
3. Webhook handling for payment confirmation
4. Test mode setup for development

Focus on:
- Stripe Elements vs Checkout
- Required API endpoints
- Webhook security verification
- Environment variable management
- Testing approach

Our stack:
- Next.js 14 with App Router
- TypeScript
- Prisma for database
- Currently no payment system

Fetch current best practices from Stripe documentation."
```

**What Kimi Code Does:**
1. `FetchURL` on Stripe docs
2. `SearchWeb` for recent integration guides
3. Synthesizes implementation approach
4. Provides code examples
5. Highlights security considerations

**Result:** Complete integration guide with code samples.

---

## Summary: Request Quality Factors

| Factor | Poor Request | Good Request |
|--------|--------------|--------------|
| **Specificity** | "Fix it" | "Fix the timeout in auth middleware" |
| **Context** | "Update the code" | "Update user validation to support international phone numbers" |
| **Scope** | "Refactor everything" | "Refactor the auth module to use the new apiClient" |
| **Success Criteria** | "Make it better" | "Reduce bundle size by 20% while maintaining functionality" |
| **Constraints** | (none) | "Don't change the public API" |
| **Files/Location** | (not mentioned) | "In src/services/auth.ts" |

Apply these patterns to get the best results from Kimi Code.
