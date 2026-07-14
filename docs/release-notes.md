# CreatorForge Release Notes

This release hardens the local production workflow: a single Studio generation
action can opt into the complete private pipeline, progress includes media and
upload stages, and individual artifacts remain independently regenerable.

It adds local settings, diagnostics, dashboard metrics, and project-management
operations. Existing API routes remain compatible; all external integrations
are locally configured and covered by mock-based tests.
