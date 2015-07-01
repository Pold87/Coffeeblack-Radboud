# Team Coffeeblack

To test a policy, run evaluation.py (currently still uses 10000
instead of 100000 ids).

evaluation.py first retrieves the entire context for a runid, using 10
threads.

After that, 2200 rounds of epsilon-greedy are performed, with a very
high epsilon (0.8) to explore a lot (but also exploit sometimes,
mainly to get some confidence in an arm).

Finally, the 15 best arms from epsilon-greedy are chosen, and used as
possible arms for contextual BTS (Bootstrap Thompson Sampling).

## Other files

- getcontext.py: contains methods for retrieving contexts.

IMPORTANT: there's a variables startchunk in getcontext, it
determines, from whereon the contexts should be retrieved (e.g., after
a crash, contexts can be resumed from that id).

- bandits.py: contains the code for the two phase model
(epsilon-greedy and contextual BTS).