---
id: pinned-corpus
title: Pinned corpus
summary: Keep samples out of git, pin each batch by commit and SHA-256, record where each batch came from, and leave private samples out of published numbers.
mission: study
needs: [sample files, a folder outside every repository, a SHA-256 tool]
tools: [git, a SHA-256 tool such as shasum or sha256sum, a scripting language for the fetch script, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: storytold/photocraft
    url: https://github.com/storytold/photocraft
  - name: storytold/indd-utils
    url: https://github.com/storytold/indd-utils
  - name: storytold/photocraft-corpus
    url: https://github.com/storytold/photocraft-corpus
status: draft
---

# Pinned corpus

Counts like "171 of 171" only mean something if a second person can get the same samples. A pinned corpus makes that true: the samples are never committed, every batch is fixed by a commit and a checksum, and a fetch that does not match is rejected. It also settles two things people forget: where each batch came from, and which samples must stay out of anything you publish.

## When to use

- Your study counts things over many sample files (see `rosetta-stone` and `evidence-ledger`), and the counts must be repeatable by someone else.
- The samples come from several places: public repositories, archives, files you generated, and files that are private to you.
- You will publish numbers, notes or code, and you must be sure that no sample ends up in them.

## What you need

- The samples, or a list of where to get them.
- A folder outside every repository and outside every target, ignored by git.
- A SHA-256 tool, and a scripting language for the fetch script.
- The user's rules about which samples are private. Ask for them in the briefing.

## Steps

1. **Keep samples out of git, always.** Never commit a sample, whatever its licence, and do not commit test files derived from third-party samples. The source project keeps them in a git-ignored folder and compares against reference files at run time [S].
2. **Sort the samples into batches by origin.**
   - Public batch: files you can fetch again from an upstream, at a fixed commit.
   - Generated batch: files made from scratch by a script you keep. The source keeps these in a repository of their own, and only generator-made files go in it [S].
   - Private batch: files only you have. They stay local.
3. **Write a manifest.** One entry per file: path, size, SHA-256, licence, and the source URL fixed to a commit, never to a branch. For archives, one entry per archive with its size and checksum, and one per member you use [S]. Write a plain checksum file too, one line per file in the form `sha256  path`, so any tool can check it [S].
4. **Write the fetch script, and make it strict.** What the source script does [S]:
   - saves each file in a git-ignored folder and checks its size and SHA-256 against the manifest;
   - skips files that are already present and match;
   - downloads an archive once, checks its checksum, and extracts only the members the manifest lists;
   - refuses manifest paths that point outside the target folder;
   - accepts only https, and stops when more bytes arrive than the manifest says;
   - moves a file into place only after its digest matches;
   - waits between requests to the same host;
   - exits with an error if any file is missing or does not match.

   Run it with the isolated flag if it is Python, and keep it outside the sample folder (see "Untrusted files" in the Study mission).
5. **Pin each batch.** Put every batch's commit in one file, with the date of the upstream state. Changing a pin is then the only thing that makes anyone fetch again [S].
6. **Move a pin in one reviewed step.** Change the commit, regenerate the manifest, read the manifest diff, and re-run the measurements. Raise pass floors if more files pass, and never lower one silently [S].
7. **Record provenance for each batch.** Make one commit per batch, naming what changed and the version of the application that made it [S]. Write a short provenance note per corpus: source repository, commit, licence, and who made the files [S]. If a batch is not openly licensed, keep the names of its sources in a local file and out of committed files, as the source project asks for its corpus [S].
8. **Decide what a missing corpus does.** In photocraft's CI, with the corpus feature on, a missing corpus is a failure and every checksum is re-verified before the run [S]. The same README tells other apps that consume the corpus to let their tests skip when the files are absent [S]. We suggest failing in any run whose numbers you publish.
9. **Keep private samples out of every published number.** Give them a path prefix of their own, make your tools take an exclude option for it, and run every committed measurement with the option on [S]. Never describe a private sample's content in a committed file. If a fact rests on one, mark the fact as not re-checkable by others (see `evidence-ledger`).
10. **Count distinct files by hash.** Skip a file whose SHA-256 you have already seen, and say "distinct" in the number [S].
11. **Never rewrite the history of the corpus repository,** so old pins stay fetchable [S].
12. **State the corpus in every number.** Say the date, the batches in, and the batches out, for example "654 distinct pairs, without the privately held samples" [S].

## How the Sargento splits the work

- **Inventory recruit (1).** Order: list every sample by path, size and SHA-256 into `reports/corpus-inventory.md`, mark each file's origin (public with licence, generated, private), and list duplicates by hash. It reads file names and bytes only to hash them, and it runs nothing from the samples. Hands back: the counts per origin, the duplicate list and files with no known origin.
- **Fetch-script recruit (1).** Order: write the fetch and verify scripts to the list in step 4 in `tools/`, test them on a small batch in a fresh folder, then on the full manifest. Hands back: the scripts and the final line of the run, such as "N of M files ready", with the exit code.
- **Provenance recruit (optional).** Order: for each public batch, find the upstream commit and licence and write the provenance note. Hands back: one note per batch, with `unknown` where a licence is not stated.
- **The Sargento** settles with the user which batches are private, writes the inputs list with SHA-256 into the study's `README.md`, checks that every report names the corpus its numbers are over, and rejects any report that includes private samples in a published count.

## How to prove it worked

What to count: files in the manifest, files verified by the fetch script ("N of M ready"), distinct hashes, sample files tracked by git (the answer is 0), and whether a second machine reproduces every SHA-256.

The method works when the fetch script reports all files ready, `git ls-files` lists no sample, and a rerun on another machine gives the same checksums.

No upstream measurement shows that the method improves results, so this recipe is `draft`. Numbers the source publishes about its pinned sets, marked [S], show what the setup looks like at scale:

- [S] The corpus repository's checksum file has one line per file: 258 Photoshop files and 28 GIMP files, 286 lines in all (counted from the file at the cited commit).
- [S] One Affinity reader is tested against 21 pinned public documents, out of a collection of 189 distinct documents. The documents under other terms were only opened locally, never committed.
- [S] The indd-utils manifest lists the openly licensed part of its corpus, about 5.5 GB, each file with its licence, size and SHA-256.
- [S] Published counts name their corpus: 654 distinct pairs (489 trustworthy), measured without the privately held samples.

## Sources and credits

Method learned from the open-source work of the storytold team. All links are permalinks to a fixed commit.

- Pins in one file, never committed, verified against manifests, and how to move a pin. [S] "changing a pin is the only thing that refetches." https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L1-L10
- Pins for our own files and for third-party sets, with dates. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L14-L20 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L6-L7
- Counts of the pinned sets, and the provenance note generated per corpus. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L51-L51, https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L75-L76 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L67-L69
- An archive checked against a committed digest, and subsets chosen by a manifest. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L47-L48 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/xtask/src/corpus_pins.rs#L118-L119
- The corpus repository: pinned and verified, with a checksum manifest, a rejected mismatch, and a missing corpus that fails. [S] "A pinned commit plus a sha256 manifest gives the same reproducibility" (README). https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L22-L23, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L61-L63, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L96-L99, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L112-L113 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L159-L161
- The checksum file, and the count of its lines. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L127-L127 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/SHA256SUMS#L1-L286
- Only generator-made files, one commit per batch, the pinning workflow, and never rewriting history. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L165-L168, https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L177-L178 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L186-L190
- Third-party corpora fetched from their upstreams, and the advice to copy the pattern. https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L132-L134 and https://github.com/storytold/photocraft-corpus/blob/c3abfc1c794409a71ade6a22283caab4ba4d2aa8/README.md#L148-L149
- The manifest of the open part of the indd-utils corpus. [S] "Never commit the downloaded files." https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/corpus-manifest.json#L2-L3 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/corpus-manifest.json#L2022-L2026
- The fetch script. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/fetch_corpus.py#L5-L11, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/fetch_corpus.py#L43-L43, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/fetch_corpus.py#L67-L67, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/fetch_corpus.py#L93-L94 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/fetch_corpus.py#L106-L114
- Rules for samples: never commit, no derived golden files, sources named locally only, private samples left out, untrusted files. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L23-L36 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CONTRIBUTING.md#L40-L44
- Samples stay local and are not redistributed, and facts that rest on a non-public sample. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L20-L22, https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L35-L36 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/CLEANROOM.md#L66-L66
- The exclude option and the hash check for duplicates. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/audit_corpus.py#L98-L99 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/tools/audit_corpus.py#L111-L112
- Published numbers name their corpus. https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/measurement.md#L9-L12 and https://github.com/storytold/indd-utils/blob/136f973a9d5f1b3ef34e46e27f4a08af196efde7/docs/format/unknowns.md#L12-L13
- The Affinity reader: pinned permissive files only, the rest opened locally. https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L95-L101 and https://github.com/storytold/photocraft/blob/1f7fc0f53696e54da79b95015abb37d7c22cdd1a/crates/affinity/README.md#L112-L114
- Vendor-made PDFs kept local, not fixtures. https://github.com/storytold/wordcraft/blob/c4fafc215490a0186ee750454b1ce73a9823daed/docs/file-format-parity.md#L160-L160

## Notes

What the source projects set for themselves, as information about the source and not as rules of this skill:

- The indd-utils project never commits a sample, whatever its licence, and keeps tests free of output derived from third-party files. It keeps its privately held samples out of committed numbers and never describes their content [S].
- The photocraft-corpus repository accepts only files that a script it keeps generated from scratch, and no personal, found or copyrighted files [S].
- The wordcraft project keeps its Word-made PDFs and measurements local, and says they are not fixtures [S].
- The indd-utils project does commit a manifest that names the sources and licences of the openly licensed part of its corpus, and keeps the names of the other sources in a local file [S].
- Whether a sample is private is the user's decision. The recipe only says how to keep those samples out of published numbers once the user has decided.

## Example

The photocraft project keeps one file with a pinned commit per corpus set. One command fetches every set into a git-ignored folder and checks each file against that set's manifest; the CI job re-checks every checksum before testing and downloads again only when a pin changes. To move the pin of its own Photoshop-made set (258 files), a maintainer commits to the corpus repository first, then opens a pull request that changes the commit, regenerates the manifest and raises the test floors where more files pass [S].
