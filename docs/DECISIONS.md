# Architecture decision log

Use this log for decisions affecting more than one module. Format: status, context, decision and consequences.

## ADR-001 — modular monolith
**Status:** Accepted. Vue frontend + FastAPI backend with internal modules. No microservices initially. Easier for small tasks and local testing; split only when measured need appears.

## ADR-002 — browser never calls upstream catalog directly
**Status:** Accepted. Production search/imagery/download use the app backend. Centralizes auth, availability, caching and avoids exposing secrets.

## ADR-003 — provider adapters
**Status:** Accepted. Each STAC/raster provider maps to common Scene model. UI is provider-independent.

## ADR-004 — Russian hosting and network gate
**Status:** Accepted. App/API/cache in Russia. Upstream reachability and end-user access are separate test gates. No no-VPN claim before evidence.

## ADR-005 — four baseline bands
**Status:** Accepted. MVP B02/B03/B04/B08 and free assignment to RGB. Extra bands require explicit decision. NBR needs SWIR.

## ADR-006 — COG and GDAL/Rasterio
**Status:** Accepted with validation. COG/GeoTIFF primary read path; test real Range/COG on selected source.

## ADR-007 — PostGIS and object storage
**Status:** Accepted. Metadata/geometries/jobs in PostGIS; large rasters/exports in file or S3-compatible storage behind interface.

## ADR-008 — background export
**Status:** Accepted. Long exports are jobs with worker, checksum and file delivery, not long blocking HTTP calls.

## ADR-009 — browser offline scope
**Status:** Accepted with limits. Cache shell and bounded offline packages; local data works offline; no promise of unlimited browser storage.

## ADR-010 — G1 foundation may proceed before G0 completion
**Status:** Accepted by explicit user authorization (2026-11-17).  
**Context:** The user will perform Russian-network acceptance checks after the first development build. Completing the frontend/backend development foundation does not require implementing satellite-data access.  
**Decision:** Continue G1 foundation tasks through the first local development build while G0 remains open. Do not implement provider adapters, real STAC search, raster access, imagery rendering, downloads, or claim no-VPN availability before the applicable G0 checks pass. Russian-network tests are deferred until the user receives the dev-build.  
**Consequences:** G1 work is temporarily authorized as a sequencing exception. G0 remains an independent hard gate for all real data/provider functionality and release claims.


## ADR-011 — единая мягкая нейтральная палитра интерфейса
**Status:** Accepted by explicit user direction (2026-11-17).
**Context:** Пользователь отклонил зелёную тему и попросил более мягкие цвета во всём проекте.
**Decision:** Использовать единую холодную графитово-сине-серую палитру с приглушённым голубым основным акцентом и лавандовым дополнительным акцентом для публичного лендинга и браузерного приложения. Не использовать зелёный в UI.
**Consequences:** Цвета реальных спутниковых изображений и тематических геоданных не перекрашиваются. Состояния warning/error сохраняют семантически различимые оттенки; контраст проверяется по WCAG для текста и интерактивных состояний.

## ADR-012 — потоковый просмотр спутниковых снимков без постоянного хранения полных сцен
**Status:** Accepted by explicit user direction (2026-11-18).
**Context:** Полное скачивание спутниковых сцен на сервер ради отображения создаёт ненужную нагрузку на диск и сеть. На VPS ограниченный объём диска; просмотр должен подгружать данные по мере перемещения и масштабирования карты.
**Decision:**
- Основной путь отображения — потоковое чтение только необходимых частей исходных растров и формирование картографических тайлов по запросу, без постоянного скачивания и хранения полных сцен на сервере.
- Предпочтительный технический путь — COG/GeoTIFF с HTTP Range и оконным чтением через backend, если конкретный источник действительно поддерживает этот режим. Совместимость каждого источника должна быть подтверждена испытаниями.
- Все обращения к каталогам и raster assets выполняются через backend; браузер не обращается к upstream-поставщикам напрямую.
- Временный кэш готовых тайлов и промежуточных данных допустим только с ограничениями по объёму и сроку хранения, безопасной очисткой и запретом удалять данные, используемые активными операциями.
- Полное скачивание исходных данных допускается для явно запрошенного экспорта или отдельно согласованного offline-пакета, но не как скрытый этап обычного просмотра.
**Consequences:**
- При проектировании raster reader и tile endpoint учитывать частичное чтение, повторное использование тайлов, ограниченный кэш и его автоматическую очистку.
- Проверить HTTP Range/COG, доступность каналов B02/B03/B04/B08, производительность, лицензии и российскую сетевую доступность до выбора production-поставщика.
- Это архитектурное решение не означает, что потоковый просмотр уже реализован, что любой кандидат поддерживает Range/COG или что доступ без VPN подтверждён.
- Текущая задача WEB-00.03 не расширяется: испытания raster assets и Range/COG выполняются отдельными последующими задачами фазы 00.


## ADR-013 — временное принятие одного риска npm audit для devDependency
**Status:** Accepted temporarily by explicit user authorization (2026-11-18); implemented in PR #27, merged as `f65060be3a9f862a20e2473cc2e4ea3ed26471aa`; exact-head CI run `44328382848` SUCCESS.
**Context:** GitHub-reviewed advisory GHSA-fc5q-39xc-vjpf affects `picomatch@4.0.7`, which is present only in the frontend development toolchain. The advisory did not list a patched release at the time of review; forcing a Vite downgrade or unverified override would create additional compatibility risk.
**Decision:** Temporarily allow only the exact high-severity dependency graph propagated from advisory GHSA-fc5q-39xc-vjpf on `picomatch@4.0.7`: `picomatch`, `@vue/language-core`, `fdir`, `tinyglobby`, `vite`, `vitest`, and `vue-tsc`, each at its reviewed exact lockfile version and exact `npm audit` dependency edges. Every other high/critical advisory, package, version, dependency scope or path remains a CI failure. Dependency scope is verified from `package-lock.json`; the npm audit severity report remains visible. This is risk acceptance, not a security fix.
**Review/expiry:** Recheck upstream advisory/release status within 14 days (by 2026-12-02) and remove the exception as soon as a patched compatible version is available. Revert the exception if the package moves into production dependencies or the dependency path changes.
**Consequences:** This does not authorize downgrading Vite, force-updating packages, weakening production controls, or claiming the vulnerability is fixed. The exception is tested by five Node policy tests and full frontend CI. Review/remove by 2026-12-02, or earlier as soon as an upstream patched release is available.

## ADR-014 — maximum catalog search page size
**Status:** Accepted by explicit user direction (2026-11-19).
**Context:** `API_CONTRACTS.md` required a server-bounded catalog search limit but did not specify its maximum.
**Decision:** `SearchRequest.limit` is a required integer in the inclusive range 1–100. A single catalog search response may contain at most 100 scenes. The value 100 is the hard maximum, not an implicit default; pagination uses the opaque cursor defined by the API contract.
**Consequences:** The backend DTO rejects limits below 1, above 100 and non-integer values. Any future change to this maximum requires an explicit contract and decision-log update.


## ADR-015 — тесты VPS без обновления диагностического агента
**Status:** Accepted by explicit user direction (2026-11-20).
**Context:** Routine G0 tests were repeatedly blocked or delayed by unnecessary requests to update/redeploy the VPS diagnostic agent, although the existing deployed agent can already run supported one-shot diagnostics.
**Decision:** For testing, always use the currently deployed `sentinel-explorer-agent` and its existing supported job types without asking the user to update, reinstall, redeploy or repair it. If a desired diagnostic is unsupported, use another available execution path or document the precise limitation and continue useful work. Agent maintenance is a separate task and may be raised only when the user explicitly requests it. A diagnostic response cap or handler limitation must not be reported as proof that an upstream provider is unavailable.
**Consequences:** G0 test execution must not be made conditional on agent updates. Preserve clear distinctions between transport reachability, catalog Search, asset access and raster reads.

## ADR-016 — Microsoft Planetary Computer remains a G0 candidate
**Status:** Accepted by explicit user direction (2026-11-20).
**Context:** The user confirms Microsoft Planetary Computer is accessible from Russia and requires it to remain in the provider shortlist. The 2026-11-20 VPS checker reached its STAC root (HTTP 200), but its collections response exceeded the diagnostic size cap; this is an inconclusive checker result, not proof of provider unavailability. Earlier user-side testing was recorded as Planetary Computer PASS for root/collections.
**Decision:** Keep Microsoft Planetary Computer in the G0 provider shortlist and continue testing it alongside Earth Search and CDSE. Do not remove or reject it because of `ResponseTooLarge`; improve or bypass the diagnostic limitation when needed. Continue to track Search, real Items, asset URLs, B02/B03/B04/B08 reads, Range/COG and legal terms as separate unverified criteria until independently evidenced.
**Consequences:** Provider candidacy is retained. This decision does not by itself mark every G0 test or legal criterion as passed, nor select Planetary Computer as the primary provider.


## ADR-017 — зашифрованный stateless cursor каталога
**Status:** Accepted for WEB-03.09 (2026-11-23).
**Context:** Multi-provider STAC pagination requires retaining provider-supplied continuation links and aggregate overflow state. A signed-but-readable token would expose temporary upstream URLs/tokens to the browser.
**Decision:** Use versioned AES-256-GCM encrypted opaque cursors with a server-only 32-byte key from `SENTINEL_CURSOR_ENCRYPTION_KEY` (base64), 15-minute TTL, canonical request binding, and a 64 KiB encoded-state ceiling. Cursor payload may contain provider continuation hrefs, normalized buffered scenes and emitted stable scene identities. Revalidate each href through the configured provider host allowlist before fetch. Missing/invalid key fails closed; no insecure fallback. Cursors are replayable until expiry; one-time-use semantics are explicitly out of scope.
**Consequences:** Key rotation invalidates existing cursors. The secret is never sent to frontend, DTOs, logs or health output. If state exceeds the cap, do not truncate it or issue a cursor; report a safe partial status. This ADR does not select/enable any provider or prove source availability.

## ADR-018 — публичный hash-only relay для approval команд Sentinel

**Status:** Accepted by explicit user direction (2026-11-25). Public ForAll implementation merged in PR #72 as `2b8127669f3b368e8b801b1d6cb225f65c12272b`; private Sentinel verifier integration and live command acceptance remain pending. The public relay is not an executable authorization by itself.

**Context:** The private `Helmslay/sentinel-explorer-agent` approval workflow was routed to a dedicated Windows runner, but that runner could not register because Kaspersky HTTPS inspection is administratively locked and Schannel could not complete certificate-revocation validation for the GitHub Actions token endpoint. The existing Pocket Forester runner is a separate repository runner; its successful GitHub checkout does not make it reusable by the private Sentinel repository. The public ForAll repository already hosts a constrained approval relay for Sentinel website publication.

**Decision:**
- Add a dedicated, isolated `tools/sentinel_control_relay/` module and separate `workflow_dispatch` workflow in the public `Helmslay/ForAll` repository for hash-only approval attestations of typed private Sentinel commands.
- The public workflow runs only on ForAll `main`, only under the configured owner identity and exact workflow path, with a first-attempt guard.
- Its only request-specific inputs are SHA-256 of the exact raw private Issue body, SHA-256 of the exact approved Issue title, an opaque `issue_binding_sha256`, and a fresh opaque release tag. The binding hash commits to private repository ID, Issue ID/number, both hashes, release tag and a per-request random nonce; ForAll never receives the nonce or Issue identifiers. The raw Issue, title, command/arguments, private repository credentials and Ed25519 keys must never be sent to ForAll.
- The workflow emits a short-lived, one-time public prerelease containing exactly one `approval-attestation.json` asset. The attestation identifies the hashes, operator, repository, workflow commit/run/attempt, timestamp and random approval ID.
- The private Sentinel VPS remains the trust decision point: it re-fetches the private Issue using its GitHub App, validates the typed request and requester, verifies exact hash bindings and the exact trusted public workflow run, rejects stale/reused attestations, then signs locally with the VPS-held Ed25519 key. The public relay never signs commands or executes them.
- Keep the existing public site-publication relay as a separate workflow and preserve its artifact verification path.
- Do not require changes to Kaspersky policy or use the Pocket Forester runner for cross-repository execution.

**Consequences and rollout:**
- Public relay code and documentation live under `tools/sentinel_control_relay/`; the GitHub workflow must remain under `.github/workflows/`.
- The exact merged ForAll workflow commit becomes a trust anchor in the private Sentinel verifier. That private integration is a separate reviewed task. Until it is complete and deployed, a generated public attestation must not be treated as an executable command approval.
- Public release assets disclose only hashes and workflow metadata. Hashes are not credentials, but operators must not use this relay to attest to low-entropy secrets or confidential values.
- The existing issue-triggered private Windows approval workflow is retired only after the private verifier integration and end-to-end read-only test are complete.
