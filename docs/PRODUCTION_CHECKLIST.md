# Agri Nirvana Production Checklist

## Frontend

- [ ] Set `VITE_API_BASE_URL` in the Vercel project to the deployed FastAPI URL.
- [ ] Keep `ALLOWED_ORIGINS` restricted to the exact production frontend origin(s).
- [ ] Verify image upload works for JPG, PNG, and WebP.
- [ ] Verify oversized images are rejected with a readable message.
- [ ] Verify invalid/non-plant images are rejected.
- [ ] Verify low-confidence results never present themselves as definitive diagnoses.
- [ ] Verify diagnosis history loads after refresh.
- [ ] Verify camera permissions are handled gracefully when denied.
- [ ] Verify desktop, tablet, and mobile layouts.
- [ ] Verify dark/light theme and Marathi/Hindi/English text do not overflow.

## Backend

- [ ] Run `python -m compileall -q backend`.
- [ ] Run `pytest -q backend/tests` with `AI_MODEL_PROVIDER=mock`.
- [ ] Configure a persistent production MongoDB URI.
- [ ] Configure the Hugging Face token only as a server-side secret when required.
- [ ] Confirm the production model is actually loaded before enabling real diagnosis traffic.
- [ ] Keep confidence thresholds and model versions visible in `/api/v1/model/status`.
- [ ] Monitor 4xx/5xx rates and model latency.

## Safety / agronomy

- [ ] Treat model output as decision support, not a laboratory-confirmed diagnosis.
- [ ] Do not recommend disease-specific chemical treatment when confidence is below threshold.
- [ ] Keep pesticide labels, crop registrations, PHI, and local agricultural advisories authoritative over static application text.
- [ ] Review any dosage or drone-spray recommendation before field deployment.

## Deployment

- [ ] Confirm the Vercel build succeeds.
- [ ] Confirm API CORS allows the production frontend and rejects unknown origins.
- [ ] Confirm `/health` and `/api/v1/model/status` are reachable from the deployed frontend environment.
- [ ] Verify browser console has no uncaught errors.
- [ ] Verify no API keys or tokens are shipped in the frontend bundle.
