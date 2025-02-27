DEBUG = 1
STOP_MIN = 3

SEQ_PARTT = 'seq'
COMB_PARTT = 'comb'
# OP_COMB_PARTT = 'opcomb'

ParttAlg= {}
ParttAlg[SEQ_PARTT] = "Sequential"
ParttAlg[COMB_PARTT] = "Combinational"
# ParttAlg[OP_COMB_PARTT] = "Optimized Combinational"

HYBRID_APPROACH = 'hybrid'
EARLY_ACCETP_APPROACH = 'early-accept'
EARLY_REJECT_APPROACH = 'early-reject'
ONE_SHOT_APPROACH = 'one-shot'

Approach = {}
Approach[HYBRID_APPROACH] = "Hybrid"
Approach[EARLY_ACCETP_APPROACH] = "Early_Accept"
Approach[EARLY_REJECT_APPROACH] = "Early_Reject"
Approach[ONE_SHOT_APPROACH] = "One_Shot"


TEST_DIR="tests/"
RESULT_DIR = "result/"
ALL_FILES='all'

