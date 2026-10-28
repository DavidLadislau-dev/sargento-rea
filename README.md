# Sargento REA

## Recipes

| Recipe | What it gets you | Learned from |
|---|---|---|
| [Rosetta stone pairs](skills/sargento-rea/recipes/rosetta-stone.md) | Learn an undocumented file format by pairing each sample with the vendor's own interpretation of the same document, then counting field matches across every pair. | storytold (indd-utils, photocraft, photocraft-corpus, wordcraft) |
| [Evidence ledger](skills/sargento-rea/recipes/evidence-ledger.md) | Keep every fact about a target with a match count and every open question with a status, so your code relies only on facts you can re-check. | storytold (indd-utils) |
| [Pinned corpus](skills/sargento-rea/recipes/pinned-corpus.md) | Keep samples out of git, pin each batch by commit and SHA-256, record where each batch came from, and leave private samples out of published numbers. | storytold (photocraft, indd-utils, photocraft-corpus) |
| [Black-box app observation](skills/sargento-rea/recipes/black-box-app.md) | Learn how an installed app behaves by feeding it synthetic inputs and recording what it shows and writes, using only its screen, its exports and its scripting interface. | storytold (photocraft-corpus, wordcraft, cadcraft, soundcraft, pdfcraft) |
| [Licence firewall](skills/sargento-rea/recipes/licence-firewall.md) | Sort every outside source by licence before work starts, so copyleft code is never copied or linked, permissive references are re-described with attribution, and copyleft tools only run as separate processes. | storytold (cadcraft, pdfcraft, photocraft, wordcraft, soundcraft) |
| [Rising floors](skills/sargento-rea/recipes/rising-floors.md) | Make every measurement print its scores, enforce a pass floor that only goes up, fail instead of skip when a reference tool is missing, and accept a parity claim only when a real test backs it. | storytold (pdfcraft, photocraft, photocraft-corpus, wordcraft) |
| [Call-site contract](skills/sargento-rea/recipes/call-site-contract.md) | Infer what a library function takes and returns from how real programs call it, record what the callers cannot settle, and write the code from that contract instead of translating the disassembly. | AnyPS5 |
| [Hardware oracle](skills/sargento-rea/recipes/hardware-oracle.md) | Rank your sources of truth by how directly they observe the real thing, and settle the questions that documentation leaves open by running small probes on real hardware, with every setting recorded. | AnyPS5 |
| [Call-site contract](skills/sargento-rea/recipes/call-site-contract.md) | Infer what a library function takes and returns from how real programs call it, record what the callers cannot settle, and write the code from that contract instead of translating the disassembly. | AnyPS5 |
