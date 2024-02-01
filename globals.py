DEBUG = 1
STOP_MIN = 3

SEQ_PARTT = 0
COMB_PARTT = 1
# OP_COMB_PARTT = 2

ParttAlg= {}
ParttAlg[SEQ_PARTT] = "Sequential"
ParttAlg[COMB_PARTT] = "Combinational"
# ParttAlg[OP_COMB_PARTT] = "Optimized Combinational"

HYBRID_APPROACH = 0
EARLY_ACCETP_APPROACH = 1
EARLY_REJECT_APPROACH = 3
ONE_SHOT_APPROACH = 2

Approach = {}
Approach[HYBRID_APPROACH] = "Hybrid"
Approach[EARLY_ACCETP_APPROACH] = "Early_Accept"
Approach[EARLY_REJECT_APPROACH] = "Early_Reject"
Approach[ONE_SHOT_APPROACH] = "One_Shot"

