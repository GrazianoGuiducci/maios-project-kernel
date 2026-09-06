# MAIOS Project Kernel 3.1.1

This patch corrects the runtime and delivery findings from the two post-release
reviews of 3.1.0. The earlier installer fixes and immutable v3.1.0 tag remain.

- Resultant and configuration transitions capture recovery before mutation.
  Caught failures restore state, projections and previous receipts, even when
  a nested configuration call failed after writing but before returning.
- An incomplete rollback retains owner-local evidence. Status and fresh reentry
  identify pending or unlinked resultant state and refuse another apply.
- Identical configuration reapplication keeps the last material receipt and
  its backup link intact.
- CLI plan and receipt outputs stay outside source, distribution and target;
  documented commands use a temporary path and exercise preview/apply/uninstall
  without changing the distribution bytes.
- Unregistered matching bytecode remains project-owned evidence; uninstall
  preserves it even when the associated source was removed or evolved.
- Runtime source organs, competence/faculty readers and crosswalk entries
  reject symbolic links and linked ancestors.

The suite contains 66 tests, including eight new regression cases. The real
symlink case requires host permission; Windows environments without that
privilege skip it, while Linux executes it. Read the exact commit's CI for
observed results. The distribution remains 58 files, including 47 payload files.

The state journals support qualified recovery from caught failures. They do
not authorize automatic replay, arbitrary-file cleanup or multi-file crash-safe
transactions. Normal MAIOS execution suppresses Python bytecode generation.

The family remains 3.0.0. This patch does not introduce automatic migration;
native model use and later non-identical assimilation remain separate evidence
planes. The Form and site retain their own next movements. The installable
projection remains the tracked `package/` directory, with no separate asset.
