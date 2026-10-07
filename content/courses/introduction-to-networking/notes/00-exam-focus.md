# 00 Exam focus — what is actually asked

**There are no past papers, and there will not be any before you sit the first
exam.** Read this note for what that means, not for a question bank.

## Why there is nothing to mine

| fact | source |
|---|---|
| 191.030 is **new in 2026W** | [S1] |
| TISS has **no 2025W and no 2024W offering**; requesting either serves the 2026W page, and the course search over 2026W/2027S returns exactly one row | [S2], [S3] |
| The lecturer, **Tobias Fiebig**, took up the Computer Networks chair at TU Wien on **1 March 2026** | [S5] |
| 191.030 is his **only lecture** here (his other 2026W entries are the generic project/thesis/practical numbers 191.005–191.009, 191.033) | [S4] |
| **VoWi has no page** for the course and none naming him | [S7] |
| TISS: "No lecture notes are available" | [S1] |
| No script, exercise sheet or past paper of his is public. **Update 2026-10-05: lecture slides are**, on the course site, from lecture 1 on [S36] | [S5], [S36] |

So the usual method — read three past papers, count which topics recur — is
unavailable. Everything below is either **stated by TISS** (high confidence),
**stated by the lecturer in lecture 1** (highest confidence, next section) or
**inferred** (labelled as such).

## What lecture 1 stated (05.10.2026) [S36]

Source: the three published decks (Organization, Networks and protocols,
IETF/IANA/ICANN/RIR/NIC) and the course page. This replaces the earlier
"ask in the first lecture" guesses.

| item | stated |
|---|---|
| course site | <https://internet.wien/teaching/introduction-to-networking/introduction-to-networking-2026/>: lecture dates, slides, assignments. This is where material lives; there is no TUWEL course |
| contact | teaching@internet.wien (slides); the site footer also lists contact@internet.wien |
| team | Tobias Fiebig and **Daniel Wagner** (DE-CIX; IRR/RPKI, botnets, DDoS) as co-lecturers; **Charmaine Taus** as team assistant and student contact point. **No tutors, no PhD students**, "things might take a bit longer" |
| exams | both **in person, closed book, 2 h**, registration required; allowed: **one hand-written, two-sided DIN A4 sheet** (confirms the inference from S33) |
| exercises | five, **voluntary**, 20 pts each, after lectures 7, 9, 16, 19, 22 |
| grades | 240+ = 1, 211-240 = 2, 181-210 = 3, 150-180 = 4. The overlap at 240 is unchanged on the slides: still assume 241+ |
| oral exam | only if you took both exams, or one exam and all five exercises, and still have under 150 |
| workload | 180 h: about 2 h lecture + 1 h exercises + 8.25 h self-study per week over 15 weeks, plus 11.25 h exam preparation |
| literature | background reading **Kurose and Ross, 8th ed.** (inspiration; order, content, depth differ, "significant additional material") and Peterson and Davie, *Computer Networks: A Systems Approach* |
| learning objectives | the five TISS outcomes, unchanged |
| "protocols and details matter" | "precisely parsing an IP header is harder than you might think": expect bit-level questions on headers |
| explicitly out of scope | applications (Instagram), AI, containers (Docker), front end, **security and privacy (Tor, VPNs)** |

Lecture-by-lecture topics from the course page (slot = Monday; lecture numbers
as in the section above):

| date | topics |
|---|---|
| 05.10 | organization; networked communication; Internet governance (IETF, IANA, ICANN, RIR, NIC) |
| 12.10 | Layer 1 refresher; forwarding paradigms; Ethernet I |
| 19.10 | Ethernet II; IPv4/IPv6; ARP/NDP |
| 09.11 | static routing; link-state algorithms; OSPF, IS-IS |
| 16.11 | distance-vector algorithms; Babel, BGP |
| 23.11 | ICMP/ICMPv6; UDP |
| 30.11 | **mid-term** |
| 07.12 | TCP introduction and mechanisms |
| 14.12 | congestion control; socket programming |
| 11.01 | DNS, DNSSEC; Telnet |
| 18.01 | unicast/anycast/multicast; Q&A |
| 25.01 | **final** |

What this changes against the inferred scope: the mid-term covers everything
through UDP (L1, Ethernet, IP, ARP/NDP, routing incl. **IS-IS, Babel and
distance vector**, ICMP), the final TCP onward plus DNS and multicast
(cumulative scope is not stated). **Distance vector and Babel are named after
all**, contrary to the subject list. Lecture 1 also spent a whole deck on
internet history and the registry hierarchy; see note 01.

## What TISS states [S1]

State as of **2026-09-27** (TISS re-read in a logged-in browser that day; dates,
exams and registration unchanged since the 2026-09-22 transcription):

| item | value |
|---|---|
| registration | deregistration possible until **02.10.2026 12:00** |
| lectures | twelve, Mon 12:00–14:00, EI 11 HS: 05.10, 12.10, 19.10, 09.11, 16.11, 23.11, 30.11, 07.12, 14.12.2026, 11.01, 18.01, 25.01.2027 |
| mid-term | Mon 30.11.2026 12:00–14:00, lecture room; registration 12.10.2026 12:00 – 23.11.2026 12:00 |
| final | Mon 25.01.2027 12:00–14:00; registration 12.10.2026 12:00 – 18.01.2027 12:00 |
| points | 5 exercises × 20 (after lectures 7, 9, 16, 19, 22) + mid-term 100 + final 100 = 300; pass at 150 |
| TUWEL | **no TUWEL course is linked** from TISS |
| TISS text change | the API's "Subject of course" lost its last sentences between 2026-09-22 and 2026-09-27: the practical-part examples and the sentence scheduling the five exercises "according to the overview in the examination description". The five-exercise schedule itself still stands in the examination modalities. See [`../docs/tiss.md`](../docs/tiss.md) |


### Points

| part | when | points |
|---|---|---|
| Exercise 1 | after lecture 7 | 20 |
| Exercise 2 | after lecture 9 | 20 |
| **Mid-term exam** | after lecture 14, **Mon 30.11.2026 12:00–14:00**, in the lecture room | **100** |
| Exercise 3 | after lecture 16 | 20 |
| Exercise 4 | after lecture 19 | 20 |
| Exercise 5 | after lecture 22 | 20 |
| **Final exam** | after lecture 24, **Mon 25.01.2027 12:00–14:00** | **100** |
| | | **300** |

Pass at **150**. Grades: genügend 150–180, befriedigend 181–210, gut 211–240,
sehr gut 240+. (The scale as TISS prints it overlaps at exactly 240, which is
listed under both "gut" and "sehr gut"; assume 241+ for a 1 and ask in the first
lecture.) Below 150 **after taking part in at least two parts** (both exams, or
one exam and all five exercises) you may request an oral exam with the lecturer
and an external professor.

Arithmetic worth doing once:

- The two exams alone are 200 points, so they can carry a pass on their own.
- The five exercises alone are 100 points and **cannot**.
- 150/300 is exactly 50 %, and there is no separate hurdle on either component.
  A perfect exercise score plus one exam at 50 % already passes (100 + 50).
- Mode of examination is **written** for both exams; the mid-term is explicitly
  "takes place in the lecture room", i.e. in the normal Monday slot.

### The lecture calendar, and what "after lecture N" means

TISS lists the ECTS breakdown as 24 h of lectures and shows **twelve** single
appointments, all Mon 12:00–14:00 in EI 11 HS [S1]:

| # | date | # | date |
|---|---|---|---|
| 1 | 05.10.2026 | 7 | **30.11.2026 — mid-term** |
| 2 | 12.10.2026 | 8 | 07.12.2026 |
| 3 | 19.10.2026 | 9 | 14.12.2026 |
| 4 | 09.11.2026 | 10 | 11.01.2027 |
| 5 | 16.11.2026 | 11 | 18.01.2027 |
| 6 | 23.11.2026 | 12 | **25.01.2027 — final** |

(26.10 and 02.11 are skipped, as is the 21.12–04.01 break.)

Twelve slots × 2 h = the 24 h of the breakdown, so **"lecture N" counts
teaching hours, not Mondays**: slot *k* delivers lectures 2*k*−1 and 2*k*. That
mapping lands both exams exactly where TISS schedules them — lecture 14 is slot
7 = 30.11 and lecture 24 is slot 12 = 25.01 — which is strong evidence it is
right. Under it, the exercises come out at:

| exercise | after lecture | ⇒ released around |
|---|---|---|
| 1 | 7 | 09.11.2026 |
| 2 | 9 | 16.11.2026 |
| 3 | 16 | 07.12.2026 |
| 4 | 19 | 11.01.2027 |
| 5 | 22 | 18.01.2027 |

**Inferred, not stated.** But note the shape it implies and plan for it: two
exercises in three weeks before the mid-term, then three in the last seven
teaching weeks, at 20 h each against a 100 h budget. Exercises 4 and 5 land in
January on top of final-exam revision.

### Registration deadlines [S1]

Course 01.08.2026 12:00 – 05.10.2026 12:00.
Deregistration until **02.10.2026 12:00**, i.e. three days *before*
registration closes. Mid-term 12.10.2026 12:00 – 23.11.2026 12:00. Final
12.10.2026 12:00 – 18.01.2027 12:00. Exam registration for both opens on the
same day, a week after the course starts, and is separate from the course
registration: both exams need their own.

### What the learning outcomes commit the exam to [S1]

The five outcomes are unusually operational, and each maps to a question type:

| outcome | what a question looks like | our note |
|---|---|---|
| "explain basic concepts … Layer 2 (Ethernet, ARP), 3 (IPv4, IPv6), 4 (TCP/UDP)" | header fields, what each does, why | 02–05 |
| "describe how the layers approach … is supported by layering and encapsulation" | what changes at each hop and what does not | 01 |
| **"Solve networking and routing scenarios, i.e., given partial network information, synthesize remaining information"** | the subnetting / forwarding-table / topology-derivation exercise | 03, 06, 07, 11 |
| "Describe a given protocol or network using the terminology … to assess its feasibility" | "here is protocol X, criticise it" | 10 |
| "Design rudimentary network protocols for a given use-case" | "design a protocol for Y; justify transport, framing, error handling" | 10 |

The third is the one written as a *skill* rather than as knowledge. The
practical-part text used to repeat it with three examples, "describing packet
traces received", "deriving a topology based on provided information",
"describe TCP behavior given a specific scenario" (**stated on TISS until
2026-09-2x, removed by 2026-09-27** [S1]; recorded here on 2026-09-22). They
were the most concrete statement in the TISS record of what you would be asked
to *do*, and note 11 is built around them. Their removal is not a retraction:
the learning outcome they illustrated is unchanged, and the five exercises are
still scheduled in the examination modalities. But from 2026-09-27 the three
exercise types are **inference from the outcome, not a TISS statement**.
Confirm in the first lecture (05.10.2026).

The last outcome is the unusual one for an introductory networking course, and
the subject list backs it ("Implementation and Applications: Protocoll
Development; Socket programming"). Most comparable courses stop at describing
protocols; this one expects you to produce one.

## What is inference

### From the subject list [S1]

The three-part list is the note order, and it is short enough to be read as an
exhaustive scope statement:

1. *Foundations*: terms; **multi-stakeholder principle of Internet governance**;
   L2 (Ethernet, ARP); L3 (IPv4, IPv6); L4 (TCP/UDP).
2. *Protocols and technologies*: routing/forwarding; **link-state and
   path-vector** algorithms; DNS, **DNSSEC**, Telnet; unicast/multicast routing.
3. *Implementation and applications*: protocol development; socket programming.

Three things are named that a standard Kurose–Ross course would not emphasise,
and they are the fingerprint of this particular lecturer:

- **Internet governance as a lecture topic**, not a footnote. It is listed first.
- **DNSSEC** named separately from DNS.
- **Path vector named alongside link state** — i.e. BGP is core, not an aside.

Conversely, the list names **no** distance-vector protocol, no wireless, no
security beyond DNSSEC, no HTTP, no congestion-control zoo, no queueing theory.
Note 07 keeps Bellman–Ford and count-to-infinity because they are the standard
contrast that makes path vector make sense — but they are marked as contrast,
not as listed content.

### From what the lecturer works on [S5]

His research is Internet measurement and operations: misconfiguration (his 2017
thesis), **DNS**, **BGP**, **SMTP and mail security (SPF, DMARC, MTA-STS)**,
**IPv6 readiness**, and human factors in system administration. He won a
teaching award at TU Delft for an ICT risk course, not for a networking one.

Reasonable bets, all **unconfirmed**:

- Questions will lean towards *what operators actually do and get wrong* rather
  than towards derivations. "Why does this break in practice" over "prove this".
- DNS and BGP will be heavier than their share of the syllabus suggests.
- Real data may show up — RIPE/RIPEstat, PeeringDB, BGP tables, measurement
  plots. Notes 06 and 08 now carry the Austrian instances of exactly that
  (AS1853 ACOnet, AS679 TUNET, VIX) [S18]–[S20].
- The "hardware/real-world demonstrations" in the teaching methods [S1] suggest
  live captures and live lookups in the lecture; expect trace reading.

### From the neighbouring course [S6]

182.752 Computer Networks (Schmid/Siegl, E191, 3 ECTS) is **mandatory in the
3rd semester of 033 535 Computer Engineering** — the same curriculum for which
191.030 is a mandatory elective. Its student-reported topic list is switches,
spanning tree, MAC-table flooding, VLAN, port aggregation, trunks, QoS, 802.1X,
IPv4/v6, ARP and ARP spoofing, DNS, routing, masquerading, DHCP, TCP/UDP, load
balancers, firewalls, IDS/IPS, TLS, WLAN, streaming, web, e-mail, LoRa,
Bluetooth, NFC/RFID, KNX, Modbus.

Use it as a floor, not as a model: a Computer Engineering student arriving in
191.030 has already met VLANs, STP, ARP spoofing and DHCP. Its **format** —
student presentations, a 15-page paper, an oral exam over a question catalogue
the students write themselves — has nothing in common with 191.030's two written
exams, and its lecturers are different people.

## How to prepare, given all that

1. **Be able to compute, not just recite.** The one outcome written as a skill is
   "synthesize remaining information". Subnetting, VLSM, longest-prefix match,
   Dijkstra tables, TCP seq/ack/cwnd traces — those are practised, not read.
   Notes 03, 06, 07, 11; `subnet.py`, `linkstate.py`, `tcp_sim.py`,
   `tcp_fsm.py` (connection states, RFC 9293 Figure 5).
2. **Know the header layouts cold.** Fields, widths, what changes per hop. It is
   the cheapest possible marks and every listed layer has one. Note 01's
   encapsulation table and `headers.py`.
3. **Learn the constants with their provenance**, because this lecturer measures
   deployed networks for a living and is likely to care about the difference
   between "the RFC says" and "Cisco ships". The three that most people get
   wrong are in note 07 (OSPF's 10/40 is an Appendix C *sample*, not a default
   [S8]), note 07 again (BGP's 90/30/120 s *are* RFC 4271 §10 suggested
   defaults, and MRAI is 30 s on eBGP but 5 s on iBGP [S9]), and note 05 (RFC
   6298 rounds any RTO under 1 s **up to 1 s** [S14]).
4. **Practise protocol design out loud.** Transport, framing, identification,
   error handling, versioning, security — six decisions, each with a reason.
   Note 10's checklist is the answer template.
5. **Have a governance answer ready.** It is listed first in the subject list and
   is the easiest thing to be caught out on: who runs numbers (IANA/RIRs), who
   writes protocols (IETF), who runs names policy (ICANN), and what
   "multi-stakeholder" excludes. Note 01.

## Exam-style questions in these notes

Every "exam-style question" in notes 01–11 is **ours**. None is modelled on a
past paper of 191.030, because none exists; none is taken from 182.752 either,
whose oral catalogue is a different kind of question entirely. They are written
to match the *verbs* of the learning outcomes above — explain, describe, solve,
assess, design — and are marked as such rather than presented as recovered
questions.
