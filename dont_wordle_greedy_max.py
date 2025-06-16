#!/usr/bin/env python3
"""
dont_wordle_solver.py
---------------------

CLI helper for *Don't Wordle*.

• All five‑letter words are read from **all_words.txt** in the current directory  
  (one word per line, upper‑ or lower‑case).  
• Pass previous guesses on the command line as  `WORD:PATTERN`,
  where PATTERN is five letters in **g y w** (green / yellow / white).

Example
--------
$ python dont_wordle_solver.py CRANE:wwywg SLOTH:gywww
Pool size  =  2211
Phase      =  huge  (depth 1, sample 800)

Top suggestions
---------------
1. TORUS   →  1236.7
2. MOIST   →  1240.8
...
20. PIOUS  →  1319.2
"""
from __future__ import annotations

import argparse, random, sys, pathlib, heapq
from array import array
from typing import List, Tuple, Dict
from tqdm import tqdm

# ---------------------------------------------------------------------------
# 1. word list
# ---------------------------------------------------------------------------

WORDS: List[str] = [w.strip().upper() for w in pathlib.Path("all_words.txt").read_text().splitlines()
                    if len(w.strip()) == 5]
N = len(WORDS)
INDEX = {w: i for i, w in enumerate(WORDS)}

# ---------------------------------------------------------------------------
# 2. pattern encoder (Wordle rules)
# ---------------------------------------------------------------------------

POW3 = [3**i for i in range(5)]                 # 1,3,9,27,81

def encode_pattern(guess: str, sol: str) -> int:
    """Return base‑3 code: 0=white,1=yellow,2=green, least‑significant first."""
    res = [0]*5
    taken = [False]*5                     # marks letters already matched/yellowed in sol

    # first pass – greens
    for i,(g,s) in enumerate(zip(guess, sol)):
        if g == s:
            res[i] = 2
            taken[i] = True

    # second pass – yellows
    for i,g in enumerate(guess):
        if res[i]:          # already green
            continue
        for j,s in enumerate(sol):
            if not taken[j] and g == s:
                res[i] = 1
                taken[j] = True
                break
    # compact into int
    return res[0] + 3*res[1] + 9*res[2] + 27*res[3] + 81*res[4]

# map CLI pattern chars to digits
CHAR2DIGIT = {'w':0,'W':0,'y':1,'Y':1,'g':2,'G':2}

def strpat_to_code(pat: str) -> int:
    if len(pat)!=5:
        raise ValueError("pattern must be 5 chars of g/y/w")
    digits = [CHAR2DIGIT[c] for c in pat]
    return sum(d*POW3[i] for i,d in enumerate(digits))

# ---------------------------------------------------------------------------
# 3. lazy row cache (guess × solutions → codes)
# ---------------------------------------------------------------------------

_ROW_CACHE: Dict[int, array] = {}

def pattern_row(g_idx: int) -> array:
    """Return array('B', len=N) with codes for guess `g_idx` versus every solution."""
    if g_idx in _ROW_CACHE:
        return _ROW_CACHE[g_idx]
    g = WORDS[g_idx]
    row = array('B', (encode_pattern(g, s) for s in WORDS))
    _ROW_CACHE[g_idx] = row
    return row

# ---------------------------------------------------------------------------
# 4. expected pool size scorer (depth 1)
# ---------------------------------------------------------------------------

def exp_size_one(guess_idx: int, C: List[int]) -> float:
    """Expected size of remaining pool after playing `guess` once (depth=1)."""
    row = pattern_row(guess_idx)
    buckets: Dict[int,int] = {}
    for s_idx in C:
        code = row[s_idx]
        buckets[code] = buckets.get(code,0)+1
    tot = sum(v*v for v in buckets.values())
    return tot / len(C)

# ---------------------------------------------------------------------------
# 5. depth‑limited beam scorer
# ---------------------------------------------------------------------------

def score_depth(guess_idx: int, C: List[int], depth: int, sample_k: int | None) -> float:
    """
    Recursive beam evaluator:
      depth==1 -> greedy‑max
      depth==2 -> one ply look‑ahead with best second move (greedy) per branch
    """
    if depth == 1:
        return exp_size_one(guess_idx, C)

    # depth >=2 ; here we only use depth==2 per our plan
    row = pattern_row(guess_idx)
    # group solutions by pattern
    groups: Dict[int, List[int]] = {}
    for s_idx in C:
        code = row[s_idx]
        groups.setdefault(code, []).append(s_idx)

    total = 0.0
    for subset in tqdm(groups.values(), desc="Deep search branches", disable=len(groups)<100):
        if len(subset) == 0:
            continue
        # second move: evaluate (depth‑1 == 1) over subset
        if sample_k and len(subset) > sample_k:
            second_pool = random.sample(subset, sample_k)
        else:
            second_pool = subset
        best_second = max(exp_size_one(h_idx, subset) for h_idx in second_pool)
        total += best_second * len(subset)

    return total / len(C)

# ---------------------------------------------------------------------------
# 6. main chooser
# ---------------------------------------------------------------------------

def recommend(C: List[int], depth: int, sample_k: int | None, top_n: int = 20,
              rng: random.Random | None = None) -> List[Tuple[str,float]]:
    if rng is None:
        rng = random
    pool = C
    if sample_k and len(pool) > sample_k:
        pool = rng.sample(pool, sample_k)

    heap: List[Tuple[float,int]] = []
    for g_idx in tqdm(pool, desc="Evaluating guesses", disable=len(pool)<100):
        sc = score_depth(g_idx, C, depth, sample_k)
        heapq.heappush(heap, (-sc, g_idx))
    # pull top_n
    out: List[Tuple[str,float]] = []
    for _ in range(min(top_n, len(heap))):
        sc_neg, idx = heapq.heappop(heap)
        out.append((WORDS[idx], -sc_neg))
    return out

# ---------------------------------------------------------------------------
# 7. CLI parsing & constraint filtering
# ---------------------------------------------------------------------------

def filter_candidates(constraints: List[Tuple[str,int]], banned_letters: str) -> List[int]:
    """Return indices of words compatible with all (guess,pattern_code) constraints."""
    C = list(range(N))          # start with all words
    for guess, pat_code in constraints:
        g_idx = INDEX.get(guess)
        if g_idx is None:
            raise ValueError(f"unknown word {guess}")
        row = pattern_row(g_idx)
        C = [s_idx for s_idx in C if row[s_idx] == pat_code]
    if banned_letters:
        banned_upper = banned_letters.upper()
        C = [s_idx for s_idx in C if not any(letter in WORDS[s_idx] for letter in banned_upper)]
    return C

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Don't Wordle helper")
    p.add_argument("history", nargs="*",
                   help="GUESS:PATTERN pairs where PATTERN is 5 letters g/y/w")
    p.add_argument("--seed", type=int, default=0,
                   help="random seed for reproducibility (default 0)")
    p.add_argument("--banned-letters", type=str, default="",
                   help="letters that are banned from the solution (e.g. 'abc'). To be used if you've done Undos to limit the pool size.")
    return p.parse_args()

def main() -> None:
    ns = parse_args()
    rng = random.Random(ns.seed)

    # read history
    constraints: List[Tuple[str,int]] = []
    for item in ns.history:
        try:
            guess, pat = item.split(":")
        except ValueError:
            sys.exit(f"Bad history token '{item}'. Use WORD:PATTERN")
        constraints.append((guess.upper(), strpat_to_code(pat)))

    C = filter_candidates(constraints, ns.banned_letters)
    size = len(C)

    # decide phase/depth/sample
    if size > 1000:
        depth, sample_k, phase = 1, 1000, "huge"
    elif size > 500:
        depth, sample_k, phase = 1, None, "mid"
    else:
        depth, sample_k, phase = 2, None, "end"

    # recommend
    top = recommend(C, depth=depth, sample_k=sample_k, rng=rng)

    # ---------- output ----------
    print(f"Pool size  =  {size}")
    print(f"Phase      =  {phase}  (depth {depth}, "
          f"sample {'full' if sample_k is None else sample_k})\n")
    print("Top suggestions")
    print("---------------")
    for i,(w,sc) in enumerate(top,1):
        print(f"{i:2}. {w:<5}  →  {sc:0.1f}")

if __name__ == "__main__":
    main()

