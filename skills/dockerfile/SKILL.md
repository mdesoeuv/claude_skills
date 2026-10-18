---
name: dockerfile
description: Write and review production-grade Dockerfiles and container builds — multi-stage, pinned bases, non-root, small images, cache-friendly layers, healthchecks, and ECR/ECS/EKS specifics. Use for any Dockerfile, docker-compose.yml, container build in CI, "containerise this app", image size or CVE questions, or buildx/multi-arch builds.
metadata:
  tier: recommended
---

# Dockerfile

An image is a deployable artifact and an attack surface. Small, pinned, non-root, reproducible.

## Template

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.13-slim@sha256:<digest> AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

FROM base AS deps
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

FROM base AS runtime
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --chown=app:app . .
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/healthz')"
ENTRYPOINT ["python", "-m", "app"]
```

Adapt per language: `node:22-slim` with `npm ci --omit=dev`, `golang:1.23` builder into `gcr.io/distroless/static` or `scratch`, `eclipse-temurin:21-jre` for Java. Prefer distroless or `-slim` over `alpine` when the app uses glibc-dependent wheels.

## Rules

- Pin base images by tag **and** digest; refresh digests on a schedule (Renovate/Dependabot), not by hand.
- Order layers from least to most volatile: base, system deps, dependency manifests, dependency install, source. Copying `package.json` before `npm ci` is what makes the cache work.
- Add a `.dockerignore` (`.git`, `node_modules`, `.env*`, `*.tfstate`, tests, docs). Secrets excluded here cannot leak into layers.
- Never `COPY .env` or pass secrets as `ARG`/`ENV`; use `--mount=type=secret` at build and the orchestrator's secret injection at runtime.
- One process per container. Use `ENTRYPOINT` exec-form so signals reach the process; add `tini` or `--init` if the app spawns children.
- Run as non-root with a read-only filesystem when possible (`readonlyRootFilesystem` in ECS task def, `securityContext` in K8s).
- Set resource expectations in the task/pod spec, not in the image.

## Verify

```bash
docker build -t app:dev .
docker run --rm -p 8080:8080 app:dev            # does it start and answer /healthz
docker image ls app:dev                          # size sanity
hadolint Dockerfile                              # lint
trivy image --severity HIGH,CRITICAL app:dev     # CVEs
docker run --rm app:dev id                       # not root
```

Report image size and the trivy summary.

## AWS specifics

- ECR login: `aws ecr get-login-password --region $R | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$R.amazonaws.com`. Enable scan-on-push and a lifecycle policy that keeps the last N tagged images.
- Tag with the git SHA plus a moving tag; deploy by SHA. Never deploy `latest`.
- For Lambda container images use the `public.ecr.aws/lambda/*` bases or add the Runtime Interface Client; keep the image under the cold-start budget.
- Build multi-arch (`--platform linux/amd64,linux/arm64`) when targeting Graviton; verify native deps compile for arm64.
