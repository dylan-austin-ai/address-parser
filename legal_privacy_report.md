# Legal & Privacy Report

### 1. Checks Summary

| Check | Result | Classification |
|---|---|---|
| Dependency license scan | 25 copyleft packages found | Flag |
| Copyleft detection | 25 copyleft found | Flag |
| PII handling scan | PASS / 0 candidates | Pass |

### 2. Dependency Licenses

The scan identified several copyleft licenses. These require careful legal review to ensure that the distribution of your project does not trigger unintended source code disclosure requirements.

**Copyleft Licenses Found:**
*   **GPL-2.0 / GPL-3.0 / GPLv2+ / GPLv3:** Strong copyleft — any project that includes GPL code must also be released under GPL; **incompatible with proprietary distribution**
    *   *Affected packages:* cloud-init (dual), defer, pycups, python-apt, python-debian, ubuntu-pro-client, ufw, xkit
*   **LGPL-2.1 / LGPL-v2+ / LGPL:** Weak copyleft — can link without infecting your code, but modifications to the library itself must be released
    *   *Affected packages:* Brlapi, PyGObject, chardet, launchpadlib, lazr.restfulclient, lazr.uri, louis, pycairo, pyxdg, systemd-python, wadllib
*   **MPL-2.0 / MPL-1.1:** File-level copyleft — modified MPL files must be released, but you may combine with proprietary code in separate files
    *   *Affected packages:* certifi, orjson, pathspec, pycairo, tqdm

**Other Licenses Found:**
*   **MIT:** Permissive — use freely, keep copyright notice
*   **Apache-2.0:** Permissive — use freely, patent grant included, keep NOTICE file
*   **BSD-2-Clause / BSD-3-Clause:** Permissive — use freely, keep copyright notice
*   **CC0 1.0:** Public domain — no restrictions

### 3. PII Handling

No PII handling candidates detected.

### 4. Data Governance Assessment

| Sub-point | Assessment |
|---|---|
| Is data logged or persisted? If so, is retention policy addressed? | Not Applicable |
| Are there consent or notice mechanisms where required? | Not Applicable |
| Is sensitive data encrypted at rest or in transit? | Not Applicable |

### 5. Recommendations

1.  **Review GPL Dependencies:** The presence of `pycups`, `python-apt`, `ubuntu-pro-client`, `ufw`, and `xkit` (GPL) and `defer` (GPL) poses a significant risk if this project is intended to be distributed as proprietary software. You must ensure these are not being bundled or linked in a way that mandates the release of your own source code.
2.  **Verify Dual-License Compliance:** For `cloud-init`, confirm which license branch (GPLv3 or Apache-2.0) is being utilized to ensure compliance with your distribution model.
3.  **Audit LGPL Linking:** For all `LGPL` dependencies (e.g., `PyGObject`, `systemd-python`), verify that they are being dynamically linked rather than statically compiled to maintain the ability to satisfy LGPL requirements without disclosing your project's code.