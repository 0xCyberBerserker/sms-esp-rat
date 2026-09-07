---
name: sms-esp-rat
description: Compress concise Spanish technical responses after token-rat-esp using telegraphic phrasing and a measured semantic codebook while preserving code, commands, paths, identifiers, numbers, negations, and copy-paste text exactly.
metadata:
  short-description: Token-measured Spanish output compression
---

# sms-esp-rat

Apply after `token-rat-esp`: it compresses representation, not content.

`raw -> token-rat-esp -> sms-esp-rat -> final`

## Mode

- `safe`: compact Spanish; exact macros; minimal telegraphy.
- `normal` (default): exact macros + clear telegraphy.
- `max`: strongest lossless, reconstructable compression.

Use `safe` for high-stakes, conditional, pedagogical, or precision-heavy answers. Disable macros for third-party prose, translations, formal/legal/medical text, specifications, and literal copy-paste content.

## Transformation

1. Protect exactly: code, commands/flags, paths/URLs, IDs/hashes/CVEs, IPs/ports, versions/numbers/units, errors/regex, structured data, quoted literals, technical names, negations, conditions, and copy-paste text.
2. Compress surrounding prose: omit inferable grammar/ceremony; use measured short technical terms and minimal punctuation.
3. Emit a macro only when its entire canonical meaning is true. Otherwise use plain text.
4. Compose compatible macros with spaces. Keep parameter text literal.
5. Recheck meaning and protected regions; any mutation cancels compression.

Never append an expansion after a macro. The shared meaning lives in the codebook.

Read [references/codebook.md](references/codebook.md) before macros. Read [references/measurements.md](references/measurements.md) only to audit/change it.

Prefer one status line, then exact evidence. Examples: `lorem testok`; `partial runtime?`; `blocked:<cause>`; `check: systemctl status sshd`.

Precision wins over savings. If a macro is even slightly inaccurate or ambiguous, do not use it.
