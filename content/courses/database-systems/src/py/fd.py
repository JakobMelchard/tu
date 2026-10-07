"""Functional dependencies and normal forms (note 04).

Attributes are single characters or strings; a set of attributes is a
frozenset.  An FD X -> Y is a pair (frozenset X, frozenset Y).

Implements, in the order the note derives them:
  closure(X, F)            attribute closure X+ (the fixpoint of Armstrong's axioms)
  implies(F, fd)           F |= X -> Y  iff  Y subset of X+
  candidate_keys(R, F)     all minimal keys (pruned search over supersets of the
                           attributes that appear on no right-hand side)
  minimal_cover(F)         canonical cover: singleton RHS, no extraneous LHS
                           attribute, no redundant FD
  project(F, S)            FDs of F that hold on the sub-schema S (exponential,
                           fine for exam-sized schemas)
  normal_form(R, F)        highest of 1NF, 2NF, 3NF, BCNF
  synthesize_3nf(R, F)     Bernstein-style 3NF synthesis (lossless, dep.-preserving)
  bcnf_decompose(R, F)     BCNF decomposition by splitting on violations (lossless)
  is_lossless(R, parts, F) chase (tableau) test
  preserves(F, parts)      dependency preservation via the restricted-closure loop

Sources: [S6] ch. 7 (Silberschatz et al. slides), [S10] ch. 8 and 11.
"""
from itertools import combinations


def fs(x):
    """'AB' or ['A','B'] -> frozenset."""
    return frozenset(x)


def parse(text):
    """'A->B, BC->D' -> [(fs('A'), fs('B')), ...]; attributes are single chars."""
    out = []
    for part in text.replace(";", ",").split(","):
        if part.strip():
            lhs, rhs = part.split("->")
            out.append((fs(lhs.strip()), fs(rhs.strip())))
    return out


def fmt(F):
    return ", ".join(f"{''.join(sorted(l))}->{''.join(sorted(r))}" for l, r in F)


def closure(X, F):
    """X+ under F.  Loop until no FD adds anything: O(|F|^2 |R|) worst case."""
    res = set(X)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in F:
            if lhs <= res and not rhs <= res:
                res |= rhs
                changed = True
    return frozenset(res)


def implies(F, fd):
    lhs, rhs = fd
    return rhs <= closure(lhs, F)


def equivalent(F, G):
    return all(implies(F, g) for g in G) and all(implies(G, f) for f in F)


def is_superkey(X, R, F):
    return closure(X, F) >= R


def candidate_keys(R, F):
    """Every key contains the attributes on no RHS (they cannot be derived) and
    no attribute that is only on RHSs (it is always derivable from the rest)."""
    R = fs(R)
    on_rhs = set().union(*(r for _, r in F)) if F else set()
    on_lhs = set().union(*(l for l, _ in F)) if F else set()
    core = R - on_rhs
    middle = sorted((R & on_rhs & on_lhs) - core)
    if is_superkey(core, R, F):
        return [frozenset(core)]
    keys = []
    for k in range(1, len(middle) + 1):
        for extra in combinations(middle, k):
            cand = core | set(extra)
            if any(key <= cand for key in keys):
                continue
            if is_superkey(cand, R, F):
                keys.append(frozenset(cand))
    return keys


def prime_attributes(R, F):
    return frozenset().union(*candidate_keys(R, F))


def minimal_cover(F):
    """1. split RHS; 2. drop extraneous LHS attributes; 3. drop redundant FDs."""
    G = [(l, fs([a])) for l, r in F for a in sorted(r) if a not in l]
    G = list(dict.fromkeys(G))
    H = []
    for lhs, rhs in G:
        lhs = set(lhs)
        for a in sorted(lhs):
            if len(lhs) > 1 and rhs <= closure(lhs - {a}, G):
                lhs.discard(a)
        H.append((frozenset(lhs), rhs))
    H = list(dict.fromkeys(H))
    i = 0
    while i < len(H):
        rest = H[:i] + H[i + 1:]
        if implies(rest, H[i]):
            H = rest
        else:
            i += 1
    return H


def project(F, S):
    """Nontrivial FDs X -> A with X subset S, A in S, implied by F (minimal cover of them)."""
    S = fs(S)
    out = []
    for k in range(1, len(S) + 1):
        for X in combinations(sorted(S), k):
            cl = closure(X, F) & S
            for a in sorted(cl - set(X)):
                out.append((fs(X), fs([a])))
    return minimal_cover(out)


def bcnf_violations(R, F):
    R = fs(R)
    return [(l, r) for l, r in F if not r <= l and not is_superkey(l, R, F)]


def is_bcnf(R, F):
    return not bcnf_violations(R, F)


def is_3nf(R, F):
    """X -> A with A not in X: X superkey or A prime.  Checking a minimal cover suffices."""
    R, prime = fs(R), prime_attributes(R, F)
    return all(is_superkey(l, R, F) or r <= prime for l, r in minimal_cover(F))


def is_2nf(R, F):
    """No non-prime attribute depends on a proper subset of a candidate key."""
    R, keys, prime = fs(R), candidate_keys(R, F), prime_attributes(R, F)
    for key in keys:
        for k in range(1, len(key)):
            for part in combinations(sorted(key), k):
                if (closure(part, F) - set(part)) - prime:
                    return False
    return True


def normal_form(R, F):
    """Highest normal form among 1NF (assumed: atomic domains), 2NF, 3NF, BCNF."""
    if is_bcnf(R, F):
        return "BCNF"
    if is_3nf(R, F):
        return "3NF"
    return "2NF" if is_2nf(R, F) else "1NF"


def synthesize_3nf(R, F):
    """One schema per LHS group of the minimal cover; add a key if none contains
    one; drop schemas contained in others."""
    R = fs(R)
    G = minimal_cover(F)
    groups = {}
    for l, r in G:
        groups.setdefault(l, set(l)).update(r)
    parts = [frozenset(s) for s in groups.values()]
    if not any(is_superkey(p, R, F) for p in parts):
        parts.append(candidate_keys(R, F)[0])
    used = set().union(*parts) if parts else set()
    if R - used:                                     # attributes in no FD
        parts.append(frozenset(R - used) | candidate_keys(R, F)[0])
    parts = [p for p in parts if not any(p < q for q in parts)]
    return list(dict.fromkeys(parts))


def bcnf_decompose(R, F):
    """Split R on a violating X -> Y into (X+ cap R) and X u (R - X+); recurse on
    the projected FDs.  Lossless by construction; may lose dependencies."""
    R = fs(R)
    FR = project(F, R)
    viol = bcnf_violations(R, FR)
    if not viol:
        return [R]
    X, _ = viol[0]
    R1 = closure(X, FR) & R
    R2 = X | (R - R1)
    return bcnf_decompose(R1, F) + bcnf_decompose(R2, F)


def is_lossless(R, parts, F):
    """Chase: one row per part, distinguished symbol 'a' on its attributes;
    equate rows agreeing on an FD's LHS; lossless iff some row becomes all 'a'."""
    R = sorted(fs(R))
    rows = [{A: ("a", A) if A in p else ("b", i, A) for A in R} for i, p in enumerate(parts)]
    changed = True
    while changed:
        changed = False
        for lhs, rhs in F:
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    if all(rows[i][A] == rows[j][A] for A in lhs):
                        for A in rhs:
                            x, y = rows[i][A], rows[j][A]
                            if x != y:
                                keep = x if x[0] == "a" else y if y[0] == "a" else min(x, y)
                                drop = y if keep == x else x
                                for row in rows:
                                    if row[A] == drop:
                                        row[A] = keep
                                changed = True
    return any(all(row[A][0] == "a" for A in R) for row in rows)


def preserves(F, parts):
    """X -> Y is preserved iff the closure computed only through the parts
    (Z := Z u ((Z cap Ri)+ cap Ri)) reaches Y.  Polynomial; no projection needed."""
    for lhs, rhs in F:
        Z = set(lhs)
        changed = True
        while changed:
            changed = False
            for p in parts:
                add = closure(Z & p, F) & p
                if not add <= Z:
                    Z |= add
                    changed = True
        if not rhs <= Z:
            return False
    return True


if __name__ == "__main__":
    R = fs("ABCDE")
    F = parse("A->B, B->C, CD->E, E->A")
    print("R =", "".join(sorted(R)), " F =", fmt(F))
    print("{A}+ =", "".join(sorted(closure("A", F))), " {CD}+ =", "".join(sorted(closure("CD", F))))
    print("keys:", ["".join(sorted(k)) for k in candidate_keys(R, F)])
    print("minimal cover:", fmt(minimal_cover(F)))
    print("normal form:", normal_form(R, F))
    s3 = synthesize_3nf(R, F)
    print("3NF synthesis:", ["".join(sorted(p)) for p in s3],
          "lossless", is_lossless(R, s3, F), "preserving", preserves(F, s3))
    b = bcnf_decompose(R, F)
    print("BCNF decomposition:", ["".join(sorted(p)) for p in b],
          "lossless", is_lossless(R, b, F), "preserving", preserves(F, b))
