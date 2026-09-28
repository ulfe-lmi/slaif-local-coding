# Testing ledger 001 — real Codex envelope crashes RC2 image policy

## Purpose

This append-only ledger entry records an independently observed compatibility
failure in `slaif-local-coding` 0.1.0-rc2. It is documentation and sanitized
reproduction evidence, not an accepted fix, release record, benchmark result,
or authorization to modify a deployed service.

## Tested identities

- Product OCI digest:
  `sha256:2349400a0dd5dbcec560f6c164283f24e5a55c5f474114416af21d6f3b2cb100`
- Product source: `0a2f34b6d6fc17b732a1e7570f751776dce1ae01`
- Subject client: Codex CLI 0.149.0
- Responses model name: `qwen3.8-27b`
- Observation date: 2026-09-28 UTC

## Observed failure

A direct Codex session reached the model and completed a genuine tool loop.
The same client request through the adapter failed before upstream inference in
VISION, CACHE, and BOTH configurations. A minimal real-Codex reproduction
reported:

```text
TypeError: unhashable type: 'dict'
slaif_local_coding/image_policy.py:35 in walk
node.get("type") in IMAGE_TYPES
```

Plain Responses requests through the same adapter passed from both the VM and
an isolated worker container. This isolates the failure to processing the real
Codex request envelope rather than adapter readiness, Docker networking, or the
model endpoint.

## Content-free trigger

Codex 0.149 emits a namespace tool with nested parameter JSON schemas. Two
ordinary schema properties named `type` have dictionary schema values. The
image-policy walker recursively traverses the entire request and attempts set
membership on those dictionaries before establishing that the candidate image
marker is a string.

[`codex-envelope-content-free.json`](codex-envelope-content-free.json) records
only paths, counts, and top-level tool type labels. It contains no prompt,
credential, request body, tool body, image, source code, or model output.

## Minimal offline reproduction

[`rc2-image-policy-minimal-reproducer.json`](rc2-image-policy-minimal-reproducer.json)
records a network-disabled execution inside the exact immutable RC2 image. The
input is equivalent to this ordinary nested JSON-schema fragment:

```python
payload = {
    "tools": [
        {
            "tools": [
                {
                    "parameters": {
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "ordinary JSON-schema property",
                            }
                        }
                    }
                }
            ]
        }
    ]
}
```

Calling `slaif_local_coding.image_policy.count_images(payload)` raises
`TypeError: unhashable type: 'dict'`. No server, credential, network, prompt, or
model call is required.

## Expected correction and regression coverage

The image policy must distinguish supported string image markers from arbitrary
dictionary-valued JSON-schema fields. Regression coverage should include:

1. the content-free namespace-tool shape recorded here;
2. ordinary nested JSON schemas containing properties named `type`;
3. zero, one, and multiple valid Responses `input_image` items;
4. valid Chat `image_url` items;
5. retention of all non-image request content and tool schemas;
6. a real Codex 0.149 request through each adapter policy.

A correction requires a new immutable product candidate and fresh qualification.
Do not rewrite or relabel RC2 or the independent failed attempts.

## Privacy and provenance

Only sanitized, closed-schema evidence is included. Private raw Codex events,
adapter logs, benchmark workspaces, backend credentials, and GitHub/Docker
authentication are intentionally excluded. File hashes are in
[`MANIFEST.sha256`](MANIFEST.sha256).
