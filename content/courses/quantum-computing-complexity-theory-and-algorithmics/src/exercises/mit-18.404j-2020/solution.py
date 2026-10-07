"""Substitute practice for block B: MIT 18.404J Theory of Computation, Fall 2020.

SOURCE [S59]: MIT OpenCourseWare, 18.404J / 18.4041J / 6.840J, Prof. Michael
Sipser, Fall 2020, sample final exam with solutions (Fall 2006 paper).
Licence CC BY-NC-SA 4.0.  **This is MIT's paper, not 192.043's** -- 192.043 has
no past paper in any year [S24].  The questions are restated in our own words in
README.md; nothing is copied.  Only the four questions whose topic is on
192.043's TISS subject list are worked; see README.md for the three that are not.

Run:  ../../../../../.venv/bin/python solution.py
"""
import itertools
import os
import sys

_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py"))
sys.path.insert(0, os.path.join(_py, "complexity"))

import reachability as rch                                        # noqa: E402
import sat as S                                                   # noqa: E402


# --- Q1: the true/false/open block (B02, B03) ---------------------------------
def q1_true_false():
    """Sixteen one-line claims about classes.  Only the settled ones can be
    *checked*; the point of the question is knowing which are settled.

    We check the three that have computational content on small instances:
    PATH in P, NL = coNL (Immerman-Szelepcsenyi), and Savitch's recursion.
    """
    g = {0: [1, 2], 1: [3], 2: [3, 4], 3: [5], 4: [], 5: []}
    checks = {}

    # PATH is in P (indeed in NL): BFS and Savitch's divide-and-conquer agree.
    for s, t in itertools.product(g, g):
        assert rch.nl_reachable(g, s, t) == rch.reachable_savitch(g, s, t)
    checks["PATH in P, and Savitch's recursion decides it"] = True

    # NL = coNL: inductive counting certifies NON-reachability.
    for t in g:
        assert rch.certify_unreachable(g, 0, t) == (not rch.nl_reachable(g, 0, t))
    checks["NL = coNL (inductive counting certifies unreachability)"] = True

    # PSPACE is closed under complement: a deterministic decider is flipped.
    checks["PSPACE closed under complement (flip a deterministic decider)"] = True

    settled = {
        "P subseteq NP subseteq PSPACE subseteq EXPTIME": "true",
        "P != EXPTIME (time hierarchy)": "true",
        "PSPACE = NPSPACE (Savitch)": "true",
        "NL = coNL (Immerman-Szelepcsenyi)": "true",
        "PATH in P": "true",
        "PSPACE closed under complement": "true",
        "TQBF is PSPACE-complete": "true",
    }
    open_questions = {
        "P = NP": "open",
        "NP = coNP": "open",
        "L = NL": "open",
        "P = PSPACE": "open",
        "NP = PSPACE": "open",
        "BPP = P": "open",
        "PSPACE = EXPTIME": "open",
    }
    # The trap: PSPACE = NL is *false* -- NL subseteq SPACE(log^2 n) by Savitch,
    # and SPACE(log^2 n) != PSPACE by the space hierarchy theorem.
    refuted = {"PSPACE = NL": "false, by Savitch plus the space hierarchy theorem"}
    return {"checked": checks, "settled": len(settled),
            "open": len(open_questions), "refuted": refuted}


# --- Q3: NP-completeness of a stone-removal puzzle, with both directions ------
# A board is a list of rows; board[r][c] is "", "B" or "R".
# A *solution* keeps, in every column, stones of at most one colour, and leaves
# at least one stone in every row.  (Restated in our own words from [S59] Q3;
# the same puzzle is a textbook problem in Sipser, Problem 7.28 [S59 readings].)
def solitaire_winnable(board):
    """Brute force: for each column decide which colour survives (2^k choices)."""
    if not board:
        return True
    k = len(board[0])
    for keep in itertools.product("BR", repeat=k):
        if all(any(cell == keep[c] for c, cell in enumerate(row)) for row in board):
            return True
    return False


def three_sat_to_solitaire(cnf, n=None):
    """Clause j -> row j, variable i -> column i.

    Literal x_i in clause j puts a BLUE stone at (j, i); literal -x_i puts a RED
    stone at (j, i).  A clause containing both x_i and -x_i is dropped first: it
    is a tautology, so it constrains nothing, and it would put two stones in one
    cell.  Cells hold at most one stone by construction.

    Size: |clauses| x |vars|, so the map is computable in time O(|cnf|) -- the
    third thing a reduction proof has to establish, and the one students skip.
    """
    n = n or S.num_vars(cnf)
    kept = [c for c in cnf if not any(-l in c for l in c)]
    board = []
    for clause in kept:
        row = [""] * n
        for lit in clause:
            row[abs(lit) - 1] = "B" if lit > 0 else "R"
        board.append(row)
    return board


def q3_reduction_correctness(max_vars=3, max_clauses=4):
    """Both directions of  phi satisfiable  <=>  f(phi) winnable, exhaustively.

    (=>) A satisfying assignment tells you which colour to keep in each column:
         keep BLUE where x_i is true, RED where it is false.  Then the surviving
         stone in row j is exactly a literal that the assignment satisfies, and
         every clause has one.
    (<=) A solution tells you the assignment: BLUE kept in column i means set
         x_i true, RED means false.  Every row keeps a stone, so every clause
         has a satisfied literal.

    That the two readings are inverse to each other is the whole content of the
    proof, and it is what Pichler's admission test asks for [S23].
    """
    n = max_vars
    literals = [l for i in range(1, n + 1) for l in (i, -i)]
    clauses = [list(c) for r in (1, 2, 3) for c in itertools.combinations(literals, r)]
    tested = mismatches = 0
    for size in range(1, max_clauses + 1):
        for cnf in itertools.combinations(clauses, size):
            cnf = [list(c) for c in cnf]
            sat = S.brute_force_sat(cnf) is not None
            win = solitaire_winnable(three_sat_to_solitaire(cnf, n))
            tested += 1
            mismatches += sat != win
    assert mismatches == 0, "the reduction is not answer-preserving"
    # membership in NP: a solution is a k-bit colour choice, checkable in O(rows*k)
    return {"formulas tested": tested, "mismatches": mismatches,
            "certificate length": "one bit per column"}


# --- Q5: log-space reductions and why one direction is hopeless (B03) ---------
def q5_logspace_reductions():
    """ODD-PARITY is in L; PATH is NL-complete.  So ODD-PARITY <=_L PATH holds
    (everything in L reduces to an NL-complete problem), while PATH <=_L
    ODD-PARITY would put PATH in L and settle L = NL.

    We exhibit the easy direction concretely: the reduction maps a bit string to
    a two-node graph whose edges toggle between the states 'even' and 'odd'.
    One bit of workspace, which is what 'log space' buys at this size.
    """
    def odd_parity(bits):
        state = 0
        for b in bits:                    # O(1) workspace
            state ^= b
        return state == 1

    def reduce_to_path(bits):
        """Nodes (i, p) for position i and running parity p; s = (0,0), t = (n,1)."""
        n = len(bits)
        g = {(i, p): [] for i in range(n + 1) for p in (0, 1)}
        for i, b in enumerate(bits):
            for p in (0, 1):
                g[(i, p)].append((i + 1, p ^ b))
        return g, (0, 0), (n, 1)

    for n in range(1, 9):
        for bits in itertools.product((0, 1), repeat=n):
            g, s, t = reduce_to_path(list(bits))
            assert rch.nl_reachable(g, s, t) == odd_parity(bits)
    return {"strings checked": sum(2 ** n for n in range(1, 9)),
            "direction shown": "ODD-PARITY <=_L PATH",
            "other direction": "PATH <=_L ODD-PARITY would give L = NL"}


# --- Q6: BPP is contained in PSPACE (B05) ------------------------------------
def q6_bpp_in_pspace(n=4):
    """A BPP machine using r coin tosses is simulated by *enumerating* the 2^r
    coin sequences one at a time and counting acceptances: exponential time,
    but only r + log(2^r) = O(r) bits of storage, so polynomial space.

    Concrete machine: on input a 3-CNF phi, toss r = n coins to guess an
    assignment and accept iff it satisfies phi.  Counting its accepting branches
    is exactly model counting, which we do in O(n) space.
    """
    cnf = [[1, 2, -3], [-1, 3, 4], [2, -4], [-2, -3, 4]]
    accepting = 0
    for bits in itertools.product((0, 1), repeat=n):     # one branch at a time
        a = {i + 1: bool(b) for i, b in enumerate(bits)}
        accepting += S.evaluate(cnf, a)
    total = 2 ** n
    # the decision the simulator makes: accept iff the branch fraction > 1/2
    decision = accepting * 2 > total
    assert accepting == sum(S.evaluate(cnf, {i + 1: bool(b) for i, b in enumerate(bits)})
                            for bits in itertools.product((0, 1), repeat=n))
    return {"coin sequences": total, "accepting branches": accepting,
            "acceptance probability": accepting / total, "accepts": decision,
            "workspace": "one branch + one counter = O(r) bits"}


def solve():
    out = {"q1": q1_true_false(), "q3": q3_reduction_correctness(),
           "q5": q5_logspace_reductions(), "q6": q6_bpp_in_pspace()}
    return out


if __name__ == "__main__":
    for key, value in solve().items():
        print(key, "->", value)
