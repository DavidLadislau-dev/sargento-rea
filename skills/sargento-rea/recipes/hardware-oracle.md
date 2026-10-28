---
id: hardware-oracle
title: Hardware oracle
summary: Rank your sources of truth by how directly they observe the real thing, and settle the questions that documentation leaves open by running small probes on real hardware, with every setting recorded.
mission: build
needs: [a question about exact behaviour that your other sources leave open, access to hardware of the same family as the target, a way to run small probes on it]
tools: [a probe runner for your hardware, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: boykopovar/AnyPS5
    url: https://github.com/boykopovar/AnyPS5
status: draft
---

# Hardware oracle

Documentation, other implementations and the callers of a function all tell you something about how a system behaves, and they sometimes disagree. This recipe ranks them, and when the top-ranked written sources run out, it settles the question by running a small probe on real hardware and reading what the hardware does. The measured rows then become expected values in your tests.

## When to use

- You are reimplementing behaviour (an instruction, a system call, a library function) and the ISA manual, the compiler source, other projects and the callers do not settle a detail, or they disagree.
- You can run code on the real device or on hardware of the same family.
- You want to say, for each detail, which source it came from and how strong that source is. For the weakest source see `call-site-contract`.

## What you need

- Hardware that runs the probes. In AnyPS5's case that is an AMD GPU. On Linux the tool needs the `amdgpu` driver, read and write access to `/dev/kfd`, the ROCm HSA runtime with its headers, and a C compiler plus `clang` and `ld.lld` with the AMDGPU target [S]. On Windows it needs AMD's driver, which installs the HIP runtime, and no ROCm, C compiler, `clang` or `ld.lld` [S].
- A probe runner: something that takes a few lines of code and a table of inputs, runs them on the device and returns the raw results.
- A place to record the hardware, its settings and every measured row.
- Optional: the `rea` tools, for reading other implementations.

## Steps

1. **Rank the sources, strongest first.** The AnyPS5 order is [S]:
   1. a measurement on the real console: a payload that calls the function and records what it returns, together with the firmware version;
   2. the library's own code: a firmware module, or a copy of an SDK module that a program ships. It gives behaviour, error codes, layouts and validation order;
   3. other implementations and SDK bindings. A PS4 source may differ from the PS5 ABI;
   4. a program's call sites, which show what the caller expects, not what the library does (see `call-site-contract`).

   The ranking is the source's. Sort other implementations by licence before you read them (see `licence-firewall`) [I].
2. **Say when sources disagree.** The source asks for a note in the pull request and in the debt entry [S].
3. **Pick a detail the written sources leave open.** For instruction semantics the oracle exists to settle what the ISA documentation, LLVM or Mesa leave open [S].
4. **Measure on the closest hardware you have, and say which.** The PS5 GPU is gfx1013. Other RDNA2 GPUs share the main instruction encodings, except the operations that exist only on gfx10.1. RDNA3 runs the tool but differs from gfx1013 in more places [S]. The source asks authors to say in the PR which GPU they measured on [S]. Its examples do so: one measurement ran on RDNA1, the same family as gfx1013 [S], and another says it measures gfx1100 and not the console's gfx1013 [S].
5. **Write a probe.** The tool runs a few lines of RDNA assembly on a local AMD GPU, one input row per lane, and returns what the hardware computed [S]. Choose rows that separate your candidate models: edge values, NaN payloads, rounding ties [S].
6. **Set every control, and record it.** Every run explicitly sets all floating-point controls, even for integer instructions [S]. Record those settings alongside the GPU and the results [S].
7. **Run a control row that you know the answer to.** In one AnyPS5 measurement a first attempt answered zero for the control case as well, which would have been read as a measurement [S]. Once the descriptor was built in registers, the control answered the declared values, so the zeros for the other cases were the device's answer and not a dead kernel [S]. A control row is what lets you read a zero as an answer [I].
8. **Fit a model to every row.** Write a model that matches every measured row, implement it, and put the measured rows in the execution test as expected values [S].
9. **Respect the limits.** The tool runs compute kernels only. Behaviour that depends on the graphics pipeline (parameter cache, exports, rasterization, `SPI_*` state) cannot be measured with it [S]. Anything it cannot settle stays open: cases the sources do not settle throw, and behaviour not verified on hardware is recorded as technical debt [S].
10. **Record what you measured and what you did not.** For each detail, write the hardware, the settings, the rows and the cases that were not covered.

## How the Sargento splits the work

- **Probe recruit (1 per question).** Order: write the probe body, the input rows that separate the candidate models, and the control row; run it on the machine the user names and save every raw row with the settings. Hands back `reports/<question>.md` with the hardware, the settings, the raw rows and the control result.
- **Model recruit (1 per question).** Order: from the raw rows only, write a model that matches every row, and list the rows it does not match. Hands back the model, the count of rows matched ("N of M"), and the test file that pins the rows.
- **The Sargento** needs the user's hardware, so it asks the user to run or approve each run. It records each result in `ledger/facts.md` with the hardware, the settings and the row count (see `evidence-ledger`), marks "measured on X, not on the target" when the hardware differs, sends rejected or unmeasurable details to `ledger/unknowns.md`, and does not accept a probe report without a passed control [I].

## How to prove it worked

What to count, all [I] unless the source states them: details settled by measurement; rows measured per detail; rows the final model matches ("N of N" is the target); control rows that passed; details left open and why; how many tests pin measured rows; how many times a measurement contradicted a written source.

The method works when every row matches the model, the control passed, the tests pin the rows, and the PR or report says which hardware was used.

The recipe is `draft`. The source publishes measurements made with the tool, for example a sweep of all 63 GFX11 color codes on one descriptor type that showed comparison reads on only two formats [S]. It states no count of how often the ranking or the measurements improved the result, and it does not say how often a measurement contradicted a written source. A measurement is output of the method, and does not show the method works.

## Sources and credits

The method is documented in the public AnyPS5 project, a compatibility layer for PS5 executables. All links are permalinks to a fixed commit, or to a pull request with its merge commit.

- The source ranking, disagreements, the console-measurement example. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L9-L10, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L11-L12, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L15, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L15-L16, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L17-L18 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L20
- What the tool does, what it settles, pinning rows. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L3-L4 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L4-L5
- GPU families. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L7, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L7-L8 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L8-L9
- Requirements. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L15, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L16, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L19, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L27-L28 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L28-L29
- Row layout, floating-point controls, the workflow. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L40, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L49, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L50, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L88-L89 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L89
- Limits. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L93 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/HW_ORACLE.md#L94-L95
- Contribution rules about semantics. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/CONTRIBUTING.md#L8 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L7
- Pull request 7910, a measurement with a control, a sweep, and a stated GPU. https://github.com/boykopovar/AnyPS5/pull/7910 (merge commit https://github.com/boykopovar/AnyPS5/commit/5b5d24cb223ede690fe5eab1fe2f7a1736b801a5)
- Pull request 5375, measuring on the same GPU family and leaving the unmeasured case refused. https://github.com/boykopovar/AnyPS5/pull/5375 (merge commit https://github.com/boykopovar/AnyPS5/commit/31d951edea131b5e735e7d0b64f2148c00da8d05)

## Notes

What AnyPS5 sets for itself, as information about the source and not as rules of this skill:

- Pull requests that add or change shader instruction semantics must say where the semantics come from: measured on hardware (which GPU and what was checked) or the exact source (an ISA section, or a file from LLVM, ACO or Mesa) [S]. Reviewers check the semantics on hardware [S].
- Cases the source does not settle throw, and behaviour not verified on hardware is recorded in the technical-debt files [S]. The agent rules say the same for a general behaviour that is unknown: throw and record it [S].
- The oracle is a tool in the AnyPS5 repository, and its hardware must be an AMD GPU. Other projects need a probe runner of their own [I].
- The source's measurements name the GPU they ran on, and one says outright that it is not the console's GPU [S].

## Example

An illustrative case with made-up numbers. You need to know what a 16-bit add does when one input is a NaN with a non-default payload, and the manual does not say. You write a probe of three lines and 40 input rows covering signs, zeros, subnormals and NaN payloads, and add one control row with plain numbers whose sum you know. You set every floating-point control explicitly and record them. The control row returns the expected sum, so the device ran the kernel. Two candidate models predict different payloads for the NaN rows. One model matches 40 of 40 rows and the other 31 of 40. You implement the first, pin the 40 rows as expected values in the test, and write in the report which GPU you used and that you did not measure the other rounding modes.
