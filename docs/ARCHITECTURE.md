# Architecture and ownership boundaries

## Generative layer and delivered layer

```text
authorized context + selected capabilities
                  |
                  v
       private RepoKernel compiler
                  |
                  v
       generated Project Kernel
                  |
                  v
  MAIOS setup + host-native adapters
                  |
                  v
     project owned by the operator
```

RepoKernel is the private generative metakernel. It defines and compiles a
project-specific structure, but its source is not part of this distribution.
The Project Kernel is the generated result delivered to the project.

## Main layers in the package

| Layer | Role | Primary location |
|---|---|---|
| Project identity | Sources, intent, boundaries, and semantic continuity | `package/.repokernel/` |
| MAIOS start kernel | Startup interpretation and human-guided configuration | `package/kernel/` |
| Project state | Brief, current state, and re-entry point | `package/project/` |
| Setup state | Configuration lifecycle and interview contract | `package/setup/` |
| Local faculties | Interview, routing, and operation skills | `package/skills/` |
| Host adapters | Native discovery paths and activation receipts | `package/.agents/`, `.claude/`, `.opencode/`, `HOST_ADAPTERS.json` |

## Authority

The person owns the project direction and external-effect decisions. The
Project Kernel owns the project's explicit operational context. Host adapters
translate that shared state into each assistant's discovery conventions; they
do not create authority and they do not prove activation merely by existing.

## Evolution

`package/kernel/PROJECT_EVOLUTION_CONTRACT.json` classifies reusable change as
case memory, competence, skill, function, or meta-evolution. A candidate is not
silently promoted: the required review and ownership boundary still apply.
