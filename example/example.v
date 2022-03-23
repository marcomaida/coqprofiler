Lemma a_slow_and_long_lemma:
    forall x : nat, 
    x = x.
Proof.
    intro x.
    all: do 1 (try destruct x).
    all: do 2 (try destruct x).
    all: do 3 (try destruct x).
    all: do 4 (try destruct x).
    all: do 5 (try destruct x).
    all: do 6 (try destruct x).
    all: do 7 (try destruct x).
    all: do 8 (try destruct x).
    all: do 9 (try destruct x).
    all: do 10 (try destruct x).
    all: do 11 (try destruct x).
    all: do 12 (try destruct x).
    all: do 13 (try destruct x).
    all: do 14 (try destruct x).
    all: do 15 (try destruct x).
    all: do 16 (try destruct x).
    all: do 17 (try destruct x).
    all: do 18 (try destruct x).
    all: do 19 (try destruct x).
    all: do 20 (try destruct x).
    all: do 21 (try destruct x).
    all: do 23 (try destruct x).
    all: do 24 (try destruct x).
    all: do 25 (try destruct x).
    all: do 26 (try destruct x).
    all: do 27 (try destruct x).
    all: do 28 (try destruct x).
    all: do 29 (try destruct x).
    { do 10030 (try destruct x). reflexivity. }
    all: reflexivity.
Qed.