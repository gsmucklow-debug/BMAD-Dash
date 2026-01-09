# BMAD Dash

AI Agent Orchestration Auditor for BMAD Method projects.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install NPM dependencies:
   ```bash
   npm install
   ```

3. Build Tailwind CSS:
   ```bash
   npm run build:css
   ```

4. Copy environment template:
   ```bash
   cp .env.template .env
   ```

5. Add your Gemini API key to `.env`

6. Run the application:
   ```bash
   python backend/app.py
   ```

7. Open browser to `http://localhost:5000`

## Development

Watch Tailwind for changes:
```bash
npm run watch:css
```

## Architecture

- Backend: Flask (Python 3.10+)
- Frontend: Vanilla JavaScript + Tailwind CSS
- No database - file-based parsing only
- Localhost-only deployment
