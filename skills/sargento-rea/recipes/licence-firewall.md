---
id: licence-firewall
title: Licence firewall
summary: Sort every outside source by licence before work starts, so copyleft code is never copied or linked, permissive references are re-described with attribution, and copyleft tools only run as separate processes.
mission: build
needs: [the licence you want your own project to carry, a list of the outside code, files and tools you will study or use]
tools: [a licence checker for your package manager, git, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/cadcraft
    url: https://github.com/storytold/cadcraft
  - name: storytold/pdfcraft
    url: https://github.com/storytold/pdfcraft
  - name: storytold/photocraft
    url: https://github.com/storytold/photocraft
  - name: storytold/wordcraft
    url: https://github.com/storytold/wordcraft
  - name: storytold/soundcraft
    url: https://github.com/storytold/soundcraft
status: draft
---

# Licence firewall

A firewall here is a list. For each kind of outside material it says what you may do with it: depend on it, read it, re-describe it, or only run it. You write the list once, before the first recruit starts, and a tool in CI checks the part of it that a tool can check. That way a project can say where each idea came from and keep its own licence clean.

## When to use

- You are writing new software that reproduces the behaviour of other software or of a file format, and you want your code to be able to carry a permissive licence.
- Several recruits will read outside code and you need one rule for what each may read, copy, link or run.
- You need to be able to show, for each component, what it was learned from.

This recipe does not choose your licence or your tiers. Section "Notes" lists what the source projects chose for themselves.

## What you need

- The licence your own project will carry. The pdfcraft project's own licence is `MIT OR Apache-2.0` [S].
- The list of outside things you plan to use: libraries, reference implementations, tools, sample files, fonts, images.
- A licence checker for your package manager. The source uses cargo-deny, which is Rust-only; use the equivalent for your ecosystem.

## Steps

1. **Write your allowlist.** List the licences you accept in dependencies. The pdfcraft project's allowlist has eleven entries, starting with MIT, MIT-0 and Apache-2.0 and including BSD-2-Clause, BSD-3-Clause and ISC [S]. It states that code dependencies follow the same rule as assets: permissive licences only [S].
2. **Sort every outside thing into one of three tiers.**

   | Tier | What it is | What the source projects do with it |
   |---|---|---|
   | Permissive | Its licence is on your allowlist | Depend on it. Read it as a reference and re-describe it (step 5) [S] |
   | Copyleft | GPL, AGPL or LGPL | Never copy it and never link it. Run it only as a separate program that your tests call (step 6) [S] |
   | Unknown | No licence stated, or you cannot prove it | Do not use it. If an asset's origin or licence is unclear, do not add it [S] |

   Whether you may also read copyleft source is your choice. The source projects differ on it (see "Notes").
3. **Write the decision down once.** Keep a decision record that lists what you may depend on and what you rejected for licence reasons. The cadcraft project keeps one for its geometry libraries [S].
4. **Make a tool enforce the allowlist.** Configure the licence checker with your allowlist. The source's configuration also denies unknown registries and unknown git sources [S], and each exception is listed for one crate [S]. Each ignored advisory carries a written reason [S].
5. **Use permissive references by re-describing them.** For each reference you read, record its URL, its licence and the exact commit. Write what you learned in your own words before any code is written, and translate no code. The photocraft Affinity reader did this with an MIT-licensed reference, and records the licence and commit [S]. Then check every structure against public files, so nothing rests on the reference alone [S].
6. **Wrap each copyleft tool as an external process.** Write a small probe that runs the program and reads its output, in test code only. The source's oracle crate is a dev-dependency, never compiled into the product [S], and its probes run external programs such as qpdf [S]. CI installs qpdf and poppler-utils for them [S]. Make a missing program a failure in CI (see `rising-floors`).
7. **Apply the same rule to files that are not code.** Fonts, images, sounds and sample files. The source keeps one attribution file as the single source of truth [S], with author, source and licence for each asset [S], and a gate fails when an asset file has no entry [S]. Anything whose licence you cannot prove is not used [S].
8. **Write a provenance note for each component.** What you read, with licence and commit. What you deliberately did not read or run. Which samples were opened locally only. The Affinity reader's README does this [S]: it lists that no Affinity software was used, that nothing from an installation was read, and that no GPL or AGPL code was read [S].
9. **Check before merging a recruit's work.** The licence checker passes, the attribution gate passes, nothing in the diff came from copyleft code, and each new reference has its provenance note [I].

## How the Sargento splits the work

- **Licence audit recruit (1).** Order: list every dependency, reference, tool and asset with its licence into `reports/licence-audit.md`, using the licence checker where there is one, and place each in a tier. Write `unknown` where the licence is not stated. Hands back the count per tier and the list of unknowns.
- **Reference recruits (one per reference).** Order: read the permissive reference named in the order and write a description of its behaviour in your own words into `reports/<reference>.md`, with its URL, licence and commit. Include no code from it. Hands back the description and the questions it leaves open.
- **Oracle recruit (1).** Order: wrap each copyleft tool in a probe that runs it as a separate process, and make the probe fail when the tool is missing in CI. Hands back the probes and one passing and one failing run.
- **The Sargento** settles the tiers with the user, writes the allowlist and the decision record, puts each recruit's reading limits in its mission order, and rejects any report that contains code from a copyleft tier.

## How to prove it worked

What to count: dependencies by licence, and how many are outside the allowlist (the target is 0); assets without an attribution entry (0); copyleft programs linked into the product (0); copyleft tools reached only through probes; references with a provenance note (all of them).

The method works when the licence checker and the attribution gate pass in CI, and every reference used has its note.

The source publishes no count that shows the method working. It is a policy, and its success is the absence of copied code, which no number shows. This recipe is therefore `draft`.

## Sources and credits

Method learned from the open-source work of the storytold team. All links are permalinks to a fixed commit.

- The cadcraft rule: never copy or link copyleft code, not even read its sources. https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L25
- The wordcraft, soundcraft and pdfcraft rules for copyleft code. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L29, https://github.com/storytold/soundcraft/blob/e82c1689b31ae4941472068ebcd37b12bd4cecf0/AGENTS.md#L22 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L93
- The pdfcraft licence checker configuration: header, allowlist, unknown sources denied, an exception per crate, ignored advisories with reasons. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L3, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L2, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L10-L13, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L15-L17, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L20-L21, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L10-L22, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L33-L34, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L68-L69 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/deny.toml#L52
- The decision record for libraries. https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L9
- Formats come from public specifications. https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L25
- The Affinity reader: a permissive reference re-described, not relied on alone, with licence and commit recorded. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L84-L85, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L88, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L83-L84 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L74-L75
- The Affinity reader's provenance statements: what was and was not read or used. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L85-L86, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L72-L73, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L79-L80 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L78-L79
- Samples outside permissive terms opened locally only; pinned files permissive only. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L97-L98 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L98-L99
- Assets: unprovable licences, unclear origin, attribution file and gate. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L42, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L83, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L53, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L63 and https://github.com/storytold/cadcraft/blob/56542407292b911ad30523cfcfa987923fe2f8e2/AGENTS.md#L26
- The project licence and the allowlist for assets. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L38 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/AGENTS.md#L35
- The oracle crate: test support only, external programs, installed in CI. https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L6-L7, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/crates/oracle/README.md#L39, https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/.github/workflows/ci.yml#L80 and https://github.com/storytold/pdfcraft/blob/20eebc1c33ff7e6f42ac1c56bf95192f628a9d97/.github/workflows/ci.yml#L83
- The source stresses its asset rule. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/AGENTS.md#L19

## Notes

What the source projects set for themselves, as information about the source and not as rules of this skill:

- The cadcraft project never copies or links GPL, LGPL or AGPL code, and does not even read the sources of the copyleft projects it lists [S]. In the lines cited here, the wordcraft, soundcraft and pdfcraft projects say "never copy" and do not mention reading [S]. The Affinity reader's README says no GPL or AGPL code was read for that reader [S].
- The pdfcraft project says copyleft tools run only as external oracle processes [S]. Its configuration says copyleft is never linked [S].
- The pdfcraft project's own code carries `MIT OR Apache-2.0` [S], and its tiers follow from that. If you aim at another licence, your tiers change.
- The wordcraft project calls its rule against vendor assets non-negotiable [S].
- The rules cover only what the source projects chose for their own code. The recipe is a working method and not legal advice. Which licences you accept, and what you let your recruits read, are your decisions. Write them in your own rules for the study.

## Example

An illustrative audit, with made-up numbers. The audit recruit lists 40 dependencies: 39 permissive and 1 unknown (no licence file). A command-line tool that one test calls is copyleft; it is not a dependency, so it stays outside the build, behind a probe. The checker fails the build on the unknown dependency, and the question stays open in `ledger/unknowns.md` until the licence is proved or the dependency is removed. After the dependency is removed the ledger line reads: F-007 [S] 39 of 39 dependencies are on the allowlist. Source: reports/licence-audit.md (illustrative).
