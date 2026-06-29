# Repository Agent Instructions

Before implementing work for a specialized platform, framework, vendor, SDK, or domain-specific language, first check whether a matching skill or capability exists.

Use `capability-orchestrator` before coding when a task mentions a named platform or DSL such as Shopify Liquid, Salesforce, Stripe, n8n, Convex, Expo, Terraform, Kubernetes, GitHub Actions, Supabase, or similar vendor/framework-specific stacks, unless a matching dedicated skill is already active.

For normal English build prompts with named technologies, run project preparation internally using the prompt as source context, then read `.codex/context/manifest.json` and relevant `.codex/context/docs/*.json` before editing files. Do not ask the user to type the helper command.
