---
id: call-site-contract
title: Call-site contract
summary: Infer what a library function takes and returns from how real programs call it, record what the callers cannot settle, and write the code from that contract instead of translating the disassembly.
mission: build
needs: [a program that calls the function and that you are allowed to read, a way to list its calls into the library, a place outside the repo for disassembly output]
tools: [readelf, objdump, optional rea]
authors: [DavidLadislau-dev]
learned_from:
  - name: boykopovar/AnyPS5
    url: https://github.com/boykopovar/AnyPS5
status: draft
---

# Call-site contract

You need to reimplement a library function that nothing documents. The programs that call it do exist, and each call shows what the caller passes in and what it does with the answer. This recipe turns those calls into a short written contract, says plainly which parts the calls cannot settle, and has the code written from the contract. The disassembly never becomes the code.

## When to use

- A function in a system library has no public signature or behaviour description, and you have a program that calls it.
- You are building a compatibility layer, a reimplementation or a test double, and need arguments, widths, buffer sizes, which pointers are outputs and what counts as failure.
- You want to know how much of a contract is established and how much is a guess. Use `hardware-oracle` to rank this source against the others and to settle what is left open.

## What you need

- A program (an executable or a module) that calls the function, in a form you may read. The method works on machine code of any kind, and the steps below show the System V AMD64 case that AnyPS5 targets.
- A list of the program's imports with the address of every call to each one. AnyPS5 produces it with its own converter (step 2). Without one, any disassembler that lists cross-references to an import slot will do [I].
- `readelf` and `objdump` from binutils, or a disassembler that loads program headers.
- A folder outside the repo for disassembly and notes. Keep it out of anything you publish [I].

## Steps

1. **Rank your sources first.** A call site is the weakest source: it shows what the caller expects, not what the library does [S]. Measurement on the real device and the library's own code rank above it. See `hardware-oracle`.
2. **List the call sites.** AnyPS5 unwraps the title's decrypted `eboot.bin` with a script [S], then relinks it with the registry option [S]. The registry file lists each import with its NID, relocation type, slot offset and `callSites` as virtual addresses [S]. Modules that ship with the tool have no `callSites` [S]. A helper maps a name to its NID and back [S].
3. **Resolve each site by relocation type.** For a `GLOB_DAT` import, each call site is the `call *slot(%rip)` itself. For a `JUMP_SLOT` import, the site is the PLT stub, and the callers are the `call <stub>` instructions [S].
4. **Disassemble around the site.** The unwrapped ELF has no section headers, so `objdump -d` prints nothing. Read the executable `LOAD` segment from `readelf -lW`, cut it out at its file offset and disassemble it at its virtual address with `objdump -D -b binary -m i386:x86-64` and `--adjust-vma` [S]. Ghidra or IDA do the same when they load the program headers [S]. For a module, the repo's annotate tool does this for every executable segment and names the imports [S]. The same steps work on the library's own module [S]. Keep the output outside the repo [I].
5. **Read the registers.** The PS5 uses the System V AMD64 convention: integer and pointer arguments in six registers, then the stack; floating-point arguments in `xmm0` to `xmm7`; the result in `rax` or `xmm0` [S]. The source's table of what a call site settles, paraphrased:
   - Registers written just before the call give the argument count. A register set long before the call, or for another use, is not an argument [S].
   - The width of the move that loads a register (32-bit or 64-bit, zero- or sign-extending) gives the argument's width and signedness [S].
   - An address computed from the stack frame is a pointer to a caller buffer, and the frame layout gives the buffer's size [S].
   - A value stored at the pointer before the call and read after it marks an in/out argument, capacity in and size out [S].
   - A test and a branch on the result give a 32-bit result and the values the caller treats as failure [S].
   - A first call with a null buffer, then a second with a buffer of the returned size, is a size query [S].
   - A log string that names the function tells you which import the call is [S]. Find it with `strings -t x`, then the instruction that loads that address [S].
   - A result that is never read settles nothing: the return type stays unknown [S].
6. **Read several call sites, not one.** A single site can mislead, and the source says to check several [S].
7. **Write what is settled and what is not.** A call site does not settle what the library writes, which error codes it returns, its side effects, or the values a caller happens to accept [S]. "The title continues if it gets 0" does not mean the library returns 0 [S]. Put each item of the contract in one of two lists: settled by the sites, or open.
8. **Leave the open part open.** In AnyPS5, whatever the sites and the other sources leave open throws, and a silent stub is allowed only for something that affects the UI [S]. The code never returns a made-up success [S]. We suggest the same for any project: fail loudly on the open part and record it as a known gap [I].
9. **Cite what you saw.** For each function, record where the sites came from (title ID and addresses, or module and firmware version), what each site showed, and what was not verified, for example "read from disassembly, not measured on a console" [S]. Quote only the instructions that show the claim, not whole functions [S].
10. **Write from the contract.** Hand the contract (arguments, sizes, values, order, errors) to whoever writes the code. The code is written from it, not by translating the disassembly instruction by instruction or copying its structure [S]. Rebuild data tables from a public source when one exists [S].
11. **Re-check against better evidence when you get it.** When a measurement or a library module settles an open item, update the contract and say that the new source disagrees or agrees [I]. The source asks for a note in the pull request and the debt entry whenever sources disagree [S].

## How the Sargento splits the work

- **Site-finder recruit (1).** Order: list every call site of the named imports in the program's registry, resolve each by relocation type, and write `reports/sites.md` with one line per site. Hands back the site list and the count of sites per import. Writes no code.
- **Reader recruits (1 per library, or per group of related functions).** Order: for each assigned function, read at least two call sites and fill the table of step 5. Hands back a contract note per function with two lists, settled and open, each item tied to the site that showed it. Pastes no disassembly into the note [I].
- **Writer recruit (1 per library).** Order: implement the functions from the contract notes only. This recruit does not receive the disassembly or the program [I]. If a note leaves something open, the code fails loudly there and the recruit lists the gap in its report.
- **The Sargento** merges the contract notes into `ledger/facts.md` (see `evidence-ledger`), keeps the open items in `ledger/unknowns.md`, sends open items that matter to a measurement (see `hardware-oracle`), and refuses a writer's report that cites the disassembly instead of the contract [I].

## How to prove it worked

What to count, all [I] unless the source states them: functions with a contract note; call sites read per function; items settled and items open per function; functions whose open list is empty; functions whose contract later matched or contradicted a measurement or the library's own code ("N of M").

The method works when every function has a contract note with at least two sites, every open item is either measured later or still failing loudly, and a later measurement contradicts few settled items. The first of these counts only shows that you did the work. The last one is the real test.

This recipe is `draft`. The source describes the method and its rules but publishes no count showing that call-site contracts come out right, so the recipe has no number to cite as [S]. One caution from the source: its progress counts describe declared functions, not verified ABI compatibility or playable games [S]. Read your own counts the same way.

## Sources and credits

The method is documented in the public AnyPS5 project, a compatibility layer for PS5 executables, by its maintainer and contributors. All links are permalinks to a fixed commit. The project's text does not describe a result for the method itself.

- Source ranking, why a call site is the weakest, and what to do when sources disagree. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L17-L18 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L20
- Finding the call sites: unwrap, registry, NID helper, bundled modules. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L47, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L49, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L49-L50, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L50-L51 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L51-L52
- Relocation types. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L53 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L54-L55
- Disassembling: no section headers, the cut, the invocation, Ghidra and IDA, the annotate tool, modules. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L56-L57, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L57-L58, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L62, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L72, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L66-L67 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L75
- Log strings. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L73 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L35
- The calling convention and the table of what a site settles. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L24, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L29, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L30, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L31, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L32, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L33, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L34 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L36
- What a site does not settle, the open part, silent stubs. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L38-L39, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L39-L40 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L42-L43
- Citing: where from, what each site showed, what was not verified, quoting. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L82, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L84-L85, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L86 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L88
- Writing from the contract and public tables. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L95-L96 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L96-L97
- Repository rules cited in Notes. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L88-L89, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L93, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L93-L95, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L98, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/REVERSE_ENGINEERING.md#L13-L14, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/CONTRIBUTING.md#L9, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/CONTRIBUTING.md#L12, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/CONTRIBUTING.md#L72, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L5, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L6, https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L7 and https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/AGENTS.md#L9
- Progress counts are not verified compatibility. https://github.com/boykopovar/AnyPS5/blob/2227f1366188cda5699dd20e2e756a18006a5d4b/docs/dev/PROGRESS.md#L7

## Notes

What AnyPS5 sets for itself, as information about the source and not as rules of this skill:

- The project asks contributors to work only from dumps of titles and firmware they own, and never to add, attach or link game files, firmware, decrypted binaries or keys to the repository, a pull request or an issue [S]. Its stated goal is interoperability: what a title needs from a system library to run [S].
- A module a title ships itself is not reimplemented. It can still be read to learn how a system library behaves [S].
- The code stays generic: a title ID belongs in the debt entry, never in code or test names [S]. The agent rules add that a value, ID or path seen in one title's trace must not be special-cased [S], and the general behaviour is implemented instead [S].
- Known gaps go in a per-library debt file [S].
- The project allows no comments in code, apart from end-of-block markers [S], and asks every pull request to say whether AI assistance was used [S].
- PS4 sources can differ from the PS5 ABI, which matters when a PS4 reference is used to fill an open item [S].
- Another project could do this on any ABI. The register names and the converter in steps 2 to 5 are AnyPS5's; the idea of reading widths, buffers, in/out use and result checks is not tied to them [I].

## Example

An illustrative case with made-up names and numbers. A library function `lib_get_info` is called from 3 places in the program. In two of them the register for the second argument holds the address of a stack buffer, the third argument holds a constant that equals the buffer size, and the caller reads the third argument's memory afterwards. That gives a pointer, a capacity and a size that comes back, so the contract says "second argument: output buffer; third argument: capacity in, size out". All three callers compare the 32-bit result to zero and take the error branch on a negative value, so the contract says "32-bit result; negative means failure for these callers". Nothing shows which negative values the library returns, what it writes into the buffer or whether it is thread-safe. Those three go on the open list, and the code written from the contract fails loudly for any input the contract does not cover.
