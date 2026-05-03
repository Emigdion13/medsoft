# Qwen Code Assistant Instructions

## Mandatory Reading Before Any Task

**You MUST read and understand [PROJECT_README.md](../PROJECT_README.md) before responding to any user request.**

This file contains all critical information about:
- Project architecture and technology stack
- Spanish language requirement (all UI text)
- Python version requirements (3.12)
- Environment variable configurations
- Common pitfalls and troubleshooting steps

**When fixing bugs or making changes:**
- Read `PROJECT_README.md` first for architecture context
- Then read [HowItWasFixed.md](../HowItWasFixed.md) to avoid reintroducing old bugs

## Quick Reference

### File Locations
- Backend: `/Users/emi/Desktop/projects/medisoft/backend`
- Frontend: `/Users/emi/Desktop/projects/medisoft/frontend`
- E2E Tests: `/Users/emi/Desktop/projects/medisoft/test/e2e`

### Environment Files
- `.env.local` - Local development (DB_HOST=localhost, VITE_API_URL=/api)
- `.env.docker` - Docker deployment (DB_HOST=db, VITE_BACKEND_URL=http://backend:8000/api)

## Critical Rules

1. **READ PROJECT_README.md FIRST** - Understand the architecture before coding
2. **Project is in Spanish** - All UI text must be in Spanish
3. **Python version is 3.12** - Use `backend/.python-version` for consistency

