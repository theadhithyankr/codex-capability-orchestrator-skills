# Manual Test Projects

Use these lightweight fixtures to test stack detection and skill resolution without touching a real application.

## Next.js Site

From the repository root:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\codex_skills.py" detect .\manual-test-projects\nextjs-site
```

Expected detected stack: `nextjs`.

Resolve matching skills:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\codex_skills.py" resolve-project .\manual-test-projects\nextjs-site
```

That command may return `Winner: none` if you do not already have a matching Next.js skill installed.

For a deterministic local demo using this repository's example skill fixtures:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\codex_skills.py" resolve-project .\manual-test-projects\nextjs-site --root .\examples
```

Expected winner: `nextjs-workflow`.

Optionally search GitHub for candidates:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\codex_skills.py" resolve-project .\manual-test-projects\nextjs-site --allow-github
```

Install the best validated candidate into the fixture project:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\codex_skills.py" resolve-project .\manual-test-projects\nextjs-site --allow-github --install --scope local --yes
```

This fixture is only for detector/resolver testing. Do not run `npm install` unless you intentionally want to turn it into a real Next.js app.
