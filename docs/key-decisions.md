# Key Decisions (may change)

- **Deployment**: Use Google Cloud Run for the API; push long-running Playwright work to background (Cloud Run jobs/Cloud Tasks/Pub/Sub). Keep HTTP handlers fast.

- **Storage**: Don't rely on container FS. Upload PDFs immediately to Google Cloud Storage with a predictable path (e.g., `gs://report-cards/{run_id}/{branch}/{employee}.pdf`). Persist metadata for lookup.

- ~~**Gmail Dependency Injection**: Register `GmailService` via `FastAPI` dependency with `@lru_cache` to avoid per-request auth and enable test overrides.~~

- **Send-email API**: Accept recipients/subject/body in `JSON` with env fallbacks. Validate at least one recipient. Log errors and return clean HTTP errors.

- **Branch batching**: Group SC employees by branch, assemble per-branch recipients and attachments, send one email per branch. Ignore GRMs for now (Issue opened in Jira).

- **Looker Studio Limits**: Cannot create new parameters and calculated fields for the GRM & SC Productivity RC data source (BQ).

- **Playwright**: Use a custom image with Chromium/fonts; handle auth and UI changes. Only use local disk as a temp buffer before GCS upload.

- **Secrets/config**: Store OAuth/creds in Secret Manager. Add API auth/rate limiting. Use env locally; mount secrets in cloud.

- **Future**: Add orchestration (Workflows/Tasks), implement GCS `->` email attachments (stream bytes), and audit logging of sends (message IDs, recipients, branch, run ID).