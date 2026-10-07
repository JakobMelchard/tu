"""Tests for the educational toy code in groups.py: safe primes, generators of the order-q subgroup."""
import sympy

from groups import MEDIUM, TINY, TOY


def test_safe_primes_and_generators():
    for G in (TINY, TOY, MEDIUM):
        assert sympy.isprime(G.p) and sympy.isprime(G.q) and G.p == 2 * G.q + 1
        assert G.g != 1 and pow(G.g, G.q, G.p) == 1          # order exactly q
        assert G.is_member(G.hash_to_group("x")) and not G.is_member(G.p - 1)


def test_bruteforce_dlog_on_toy():
    for x in (0, 1, 500, TOY.q - 1):
        assert TOY.dlog_bruteforce(TOY.exp(TOY.g, x)) == x
