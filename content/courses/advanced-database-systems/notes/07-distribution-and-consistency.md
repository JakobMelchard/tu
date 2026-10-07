# 07 Distributed databases, CAP/PACELC, consistency, quorums, clocks

> **Sourcing.** Distributed DBMS topics (fragmentation, replication, 2PC,
> semi-join, quorums, clocks) appear on the 2026 block-2 cheat sheet [S4] and the
> 2025 block-3 cheat sheet [S5]; which block owns them in 2028 is open.
> 2PC: Gray and Lamport [S41]. CAP: Gilbert and Lynch [S26], Brewer [S27];
> PACELC: Abadi [S28]; eventual consistency and BASE: Vogels [S37]; which models
> survive partitions: Bailis et al. [S29], [S30]; Dynamo's quorums and vector
> clocks [S24]; logical clocks: Lamport [S31]. Code: `nosql.py`.

## Distributed DBMS vocabulary

- **Distributed database**: data stored on several nodes connected by a network,
  presented to the user as one database (**distribution transparency**:
  location, fragmentation, replication, failure).
- Architectures: **shared memory**, **shared disk**, **shared nothing** (each node
  has its own CPU, memory, disk; scales best).
- **Speed-up**: same problem, $k\times$ resources, time $/k$ if linear.
  **Scale-up**: $k\times$ problem and $k\times$ resources, same time if linear.
  "Linear scale-up means doubling CPUs halves the time" is **false**: that is speed-up.
- **Fragmentation**: horizontal (sharding: $R = R_1 \cup \cdots \cup R_k$ by a predicate
  or hash on rows) or vertical ($R = R_1 \bowtie \cdots \bowtie R_k$, each fragment keeps
  the key). Correctness: completeness, reconstruction, disjointness.
- **Replication**: several copies per fragment. Primary-secondary (writes at the
  primary, propagated) vs multi-primary (writes anywhere, conflicts possible).

## Distributed concurrency control (topic list of [S5]; no primary source consulted)

- **Locking replicated data**: *primary copy* (lock only at the item's primary
  site), *distinguished copy* variants, or *voting* (lock a majority of copies;
  more messages, survives failures).
- **Distributed deadlock**: a cycle in the global waits-for graph (WFG) that no
  single site sees. Detection: *centralised* (sites send local WFGs to one
  site), *hierarchical* (to a parent site), or *timeout* (abort after waiting too long; may abort non-deadlocked transactions).

## Semi-join reduction (worked example)

$R(A,B)$ at site 1: 10 000 tuples of 100 B. $S(B,C)$ at site 2: 2 000 tuples,
500 distinct $B$ values of 4 B. 2 000 tuples of $R$ have a partner. Result needed at site 2.

| plan | shipped bytes |
|---|---|
| ship $R$ to site 2, join there | $10\,000 \cdot 100 = 1\,000\,000$ |
| ship $\pi_B(S)$ to site 1 ($500 \cdot 4 = 2\,000$), compute $R \ltimes S$, ship it ($2\,000 \cdot 100 = 200\,000$), join | $202\,000$ |

$R \ltimes S = \pi_{\text{attr}(R)}(R \bowtie S)$. The semi-join pays iff
$|\pi_B(S)|\,w_B + |R \ltimes S|\,w_R < |R|\,w_R$: selective joins, small join keys.

## Two-phase commit (2PC) [S41 3]

Goal: a distributed transaction commits at **all** participants or at none.

1. **Prepare (voting)**: coordinator logs *start*, sends PREPARE. Each participant
   either force-writes *prepared/ready* and votes YES (it can now no longer
   abort on its own), or logs *abort* and votes NO.
2. **Decision**: all YES: coordinator force-writes *commit*, sends COMMIT; any NO
   or timeout: *abort*, sends ABORT. Participants log the decision, act, ACK;
   after all ACKs the coordinator logs *end*.

Recovery: a participant that finds *commit* in its log redoes, *abort* undoes,
*prepared* without decision is **in doubt** and must ask the coordinator; no
log record means it never voted, so abort. **Blocking**: if the coordinator
fails after participants voted YES, they hold their locks until it returns [S41].
Three-phase commit and Paxos Commit (multiple coordinators, progress with a
majority) avoid this [S41].

## CAP [S26], [S27]

- **C**onsistency here means **linearizability** (atomic consistency): every read
  returns the value of the most recent completed write, as if there were one copy.
- **A**vailability: every request to a non-failing node receives a response.
- **P**artition tolerance: the system keeps its guarantees when the network loses
  arbitrarily many messages between groups of nodes.
- **Theorem** (Gilbert and Lynch 2002, as restated in their 2012 survey [S26]): in
  a network subject to communication failures, no service can implement an
  atomic read/write register that answers every request.
- Partitions happen, so the real choice *during a partition* is **C or A**
  (CP or AP). "Pick 2 of 3" is misleading: without a partition you can have both [S27].

## PACELC [S28]

**If P**artition, choose **A** or **C**; **E**lse (normal operation), choose
**L**atency or **C**onsistency. Replication makes the else-branch unavoidable:
synchronous replication costs latency.

| class | examples in [S28] |
|---|---|
| PA/EL | default Dynamo, Cassandra, Riak |
| PC/EC | fully ACID: VoltDB/H-Store, Megastore |
| PA/EC | MongoDB |
| PC/EL | PNUTS |

## Consistency models (strong to weak)

| model | guarantee |
|---|---|
| linearizable | one global order consistent with real time; reads see the latest write |
| sequential | one global order consistent with each client's program order |
| causal | writes that are causally related (a read-then-write chain) are seen in that order by everyone; concurrent writes in any order |
| read-your-writes, monotonic reads (session guarantees) | a client sees its own writes; never goes back in time |
| eventual | if updates stop, all replicas converge [S37] |

**BASE** (Basically Available, Soft state, Eventually consistent) is the NoSQL
counter-slogan to ACID [S37]. Bailis et al. [S29] show which guarantees
remain achievable under partitions ("highly available transactions"):
read committed and many session guarantees yes; read-your-writes, PRAM and
causal consistency only with *sticky* clients (a client stays with its
replicas); snapshot isolation, repeatable read, serializability and
linearizability no.

## Quorums [S24 4.5]

$N$ replicas per item; a write succeeds after $W$ acknowledgements, a read
collects $R$ answers and returns the newest version.

$$R + W > N \;\Rightarrow\; \text{every read set meets every write set (pigeonhole)} \Rightarrow \text{reads see the latest successful write}.$$

$W > N/2$ additionally makes any two write quorums intersect (no two
concurrent writes both succeed unseen). Settings: **ROWA** (read one, write
all) $R = 1, W = N$: fast reads, writes fail when one replica is down;
**majority** $R = W = \lfloor N/2 \rfloor + 1$; Dynamo's typical $(N,R,W) = (3,2,2)$ [S24].
With $R + W \le N$ reads may be stale; how stale is quantified by PBS [S30].
**Sloppy quorum and hinted handoff** [S24 4.6]: if a replica is down the write
goes to the next healthy node with a hint and is handed back later: availability
over strict quorum guarantees.

`nosql.quorums_always_intersect(N, R, W)` enumerates all read and write sets and
returns True exactly when $R + W > N$ (tested for $N \le 5$).

## Logical clocks [S31], vector clocks [S24 4.4]

$a \to b$ (**happened before**): same process and $a$ first, or $a$ sends a
message that $b$ receives, or transitively.

- **Lamport clock**: counter $C_i$; tick before each event; send $C_i$ with messages;
  on receive $C_j := \max(C_j, C_{msg}) + 1$. Guarantees $a \to b \Rightarrow C(a) < C(b)$,
  **not** the converse: equal or smaller numbers say nothing about concurrency.
- **Vector clock**: vector $V$ with one counter per node; node $i$ increments $V[i]$
  on its events; on receive take the componentwise max, then increment own entry.
  $V(a) \le V(b)$ componentwise (and $\ne$) iff $a \to b$; neither $\le$ means
  **concurrent**, i.e. a conflict that the application must reconcile.

### Worked example: Dynamo's D1..D5 (`nosql.dynamo_example`)

| version | written by | clock | relation |
|---|---|---|---|
| D1 | Sx | [Sx:1] | |
| D2 | Sx | [Sx:2] | D1 before D2: D1 can be discarded |
| D3 | Sy (from D2) | [Sx:2, Sy:1] | after D2 |
| D4 | Sz (from D2) | [Sx:2, Sz:1] | **concurrent** with D3: client sees both |
| D5 | Sx reconciles D3, D4 | [Sx:3, Sy:1, Sz:1] | after D3 and D4 |

## Pitfalls

- CAP's C is linearizability, not the C of ACID (integrity constraints).
- $R + W > N$ does not prevent conflicts from concurrent writes unless $W > N/2$ as well.
- Sloppy quorums break the $R + W > N$ argument: the $W$ nodes may be outside the preference list.
- Lamport timestamps order all events but cannot detect concurrency.
- 2PC is about atomicity, not replication consistency, and it blocks.

## Exam-style questions

1. *$N = 5$. Which $(R, W)$ guarantee fresh reads with the fewest nodes per write?* $W = 1$ needs $R = 5$; the balanced choice is $R = W = 3$; any $R + W \ge 6$ works.
2. *Vector clocks [A:2, B:1] and [A:1, B:2]: relation?* Concurrent.
3. *A participant crashed after writing "prepared" and restarts. What does it do?* It is in doubt: keeps locks and asks the coordinator for the decision.
4. *Classify Cassandra with default settings in PACELC and justify.* PA/EL: during partitions it stays available; normally it answers from fewer replicas than needed for consistency to save latency [S28].
5. *Semi-join or full shipment: $|R| = 1000$ tuples of 50 B, all match, keys 8 B, $|\pi_B(S)| = 900$?* Semi-join: $900 \cdot 8 + 1000 \cdot 50 = 57\,200 > 50\,000$: ship $R$ directly.

## Code

- `nosql.quorums_always_intersect`, `nosql.QuorumStore` (`put`, `get` with `read_from` and `repair`), `nosql.VectorClock` (`tick`, `merge`, `compare`), `nosql.dynamo_example`.
