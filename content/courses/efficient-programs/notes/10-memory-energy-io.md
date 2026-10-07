# 10 Memory, energy and I/O efficiency

Slides 69 to 74 and 97 to 100 [S3]. The kinds of efficiency other than CPU
time from slide 2, treated briefly in the deck and briefly here: what the
lever is in each case and the one formula or number that goes with it.

## Memory efficiency [S3 p.69 to 70]

**Packing** [S3 p.69]: no unused bytes or bits (C bit-fields, Pascal
`packed`), data compression, code size, and the reason it matters for speed:
cache behaviour. A structure padded from 12 to 16 bytes puts 8 instead of
10.7 elements in a 128 B line; the miss rate of a stream is proportional to
the element size (note 04: $m = s/B$).

**Factoring** [S3 p.70]: turn similar code fragments into procedures and call
them; the opposite of inlining (note 07, #55), traded when instruction-cache
or code size is the constraint (embedded ROM). **Interpreters**: implement
schematic programs by an interpreter over a compact representation; slower
per operation, smaller (Gforth, an interpreter, appears on slides 37 and
66).

## Energy efficiency [S3 p.71 to 74] [S21]

Fewer cycles → less energy, with a caveat: what happens when the job is done
(**rebound effect**, Jevons paradox: efficiency gains get spent on more use).

**Dynamic voltage and frequency scaling.** Switching power of CMOS logic:

$$P = C\,U^2 f,$$

$C$ the switched capacitance, $U$ the supply voltage, $f$ the clock
[S3 p.71]. The rest is the standard derivation, not on the slide: where the
voltage needed for a frequency rises roughly linearly with $f$,
$P \propto f^3$ and the energy of a fixed task
$E = P \cdot t \propto f^3 \cdot f^{-1} = f^2$: half the clock, a quarter of
the dynamic energy, twice the time. Slide 72 [S21] shows where that holds:
the voltage of an AMD Zen 4 core is flat (about 0.7 V) below about 2 GHz and
rises, steeply near the top, above it. Below the knee $U$ is constant, so
$E \propto U^2$ per task does not fall with $f$ at all, while the static
(leakage, uncore, DRAM, platform) power accrues per second regardless: there
**race to idle** (finish fast, sleep) wins; near the top of the curve
slowing down pays. Slides 73 and 74 [S21] show measured libx264 runs on
Alder Lake and Zen 2 cores: performance grows ever more slowly with core
power, and the energy per task is flat or minimal somewhere in the low to
middle clock range and rises steeply over the top 1 to 1.5 GHz.

Tools (root): `turbostat` with the `PkgWatt`, `CorWatt`, `GFXWatt`,
`RAMWatt` columns, `powerstat` [S3 p.71]. What a user can set: a frequency
limit or a power limit [S3 p.71] (on Linux via cpufreq and Intel's RAPL
interface; general knowledge).

## I/O [S3 p.97 to 98]

Sources: user input, mass storage (SSD, HDD), network. **Synchronous**
(blocking) I/O waits for the result and makes no other progress; remedies:
do independent work in another thread, one thread per outstanding request,
and since spawning is expensive, reuse threads (pools). **Asynchronous
system calls**, POSIX AIO: `aio_read()` / `aio_write()` submit, `aio_suspend()`
waits (a zero timeout makes it a poll), `aio_error()` reports status. The
event loop [S3 p.98]:

```
loop:
    timeout = have work ? 0 : infinite
    if aio_suspend(requests, timeout) == 0:
        for req in requests: if aio_error(req) == 0: process result, maybe submit more
    else:
        compute a short time, maybe submit more
```

Possibly combined with threads; the pattern exists in many languages
(`async`/`await` in Rust). The slide ends with the open question
"Efficient?"; the next slide gives one part of the answer, the cost of the
system calls themselves.

## System calls [S3 p.99]

Base cost per call, Linux 6.12: `write(…, 1)` to a pipe **1 800 c**,
`write(…, 3500)` **3 600 c**. Two points give a linear model

$$\text{cost}(n) \approx 1\,800 + 0.51\,n \ \text{cycles},$$

so the per-byte cost with a buffer of $B$ bytes is $1\,800/B + 0.51$ c: 0.95
c/byte at 4 KB, 0.54 at 64 KB, 1 800 c/byte unbuffered. That is why C
`stdio` buffers several KB before calling `write()` (**batching**) [S3 p.99].

**Copying**: device → OS buffer → user buffer → application and back; each
hop costs bandwidth and cache. Interfaces with fewer copies: `mmap()`
(the page cache *is* the user buffer), `splice()` (zero copy between
descriptors). **Work in the kernel**: eBPF. **Shared-memory submission**:
io_uring [S3 p.99].

## io_uring [S3 p.100]

Two ring buffers shared between user space and kernel: a **submission queue**
(requests and data, user → kernel) and a **completion queue** (results and
error codes, kernel → user). Requests are executed asynchronously; either a
kernel thread polls the submission queue or the application calls
`io_uring_enter()` once for a batch. Both the per-call base cost and the
copies are amortised or avoided.

## Worked example: how much buffering is enough

A program writes $10^9$ bytes in 100-byte records. Unbuffered: $10^7$ calls ×
$(1\,800 + 51)$ c ≈ $1.85 \cdot 10^{10}$ c ≈ 6 s at 3 GHz. With `stdio`'s 4 KB
buffer: $2.4 \cdot 10^5$ calls × $(1\,800 + 2\,100)$ c ≈ $9.5 \cdot 10^8$ c
≈ 0.3 s. With 64 KB: $1.5 \cdot 10^4$ × $(1\,800 + 33\,500)$ ≈ $5.4 \cdot 10^8$
c ≈ 0.18 s (the 64 KB figure extrapolates a two-point fit made at 1 and
3 500 bytes), and the copy term (0.51 c/byte) now dominates: beyond this
point only fewer copies (`mmap`, `splice`) help, not bigger buffers. The
`user`/`system` split of note 02 shows which regime you are in.

## Pitfalls

- Optimising CPU time in a program that is not CPU-bound.
- One thread per connection without a pool; the spawn cost [S3 p.97].
- Measuring energy by wall time: a faster run at a higher clock can use more
  joules ($E \propto f^2$).
- Unbuffered small writes; `fflush` in a loop; `O_SYNC` by habit.
- Reading `system` time as "the kernel is slow" rather than "I am making too
  many calls".

## Exam-style questions

1. **Derive why halving the clock can quarter the energy of a task, and when it does not.** $P = CU^2f$ with $U \propto f$ gives $P \propto f^3$; $E = Pt$ with $t \propto 1/f$ gives $E \propto f^2$. Fails below the voltage knee, where $U$ no longer falls with $f$ (slide 72: flat below about 2 GHz on Zen 4), and when static/platform power dominates, so that the longer run time costs more than the lower dynamic power saves; then race to idle [S3 p.71, 72] [S21]. The $U \propto f$ step is the standard approximation, not on the slide.
2. **`write` of 1 byte costs 1 800 cycles, of 3 500 bytes 3 600. What is the per-byte copying cost and the break-even buffer size against copying?** Slope $(3\,600 - 1\,800)/3\,499 \approx 0.51$ c/byte; the base cost equals the copy cost at $B = 1\,800 / 0.51 \approx 3.5$ KB, consistent with `stdio` buffering "several KB" [S3 p.99] (the break-even is our derivation).
3. **Blocking vs asynchronous I/O: name the three POSIX AIO calls and the structure of the loop that uses them.** `aio_read`/`aio_write` submit, `aio_suspend` waits or polls, `aio_error` checks completion; a loop that waits with zero timeout when it has work and infinite otherwise, processes completed requests and submits new ones, computing in between [S3 p.97 to 98].
4. **What does io_uring change compared with `read`/`write`?** Requests and completions go through two queues in memory shared by user level and kernel, so many operations cost one `io_uring_enter()` (or none, with a polling kernel thread), and the per-call base cost is amortised [S3 p.99 to 100].
5. **How does packing a data structure affect CPU time, not only memory?** Smaller elements mean more elements per cache line and per page: the compulsory miss rate of a stream is $s/B$, TLB reach in elements is page size / $s$; fewer bytes also mean less bandwidth in the throughput-bound regime [S3 p.69] [S3 p.21].

Code: none (macOS has no `turbostat`, `perf` or io_uring). Sources: [S3 p.2, 69 to 74, 97 to 100] [S5] [S21].
