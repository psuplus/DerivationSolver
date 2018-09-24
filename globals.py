#     This file is part of Derivation Solver. Derivation Solver provides
#     implementation of derivation solvers for dependent type inference.
# 
#     Copyright (C) 2018  Peixuan Li
# 
#     Derivation Solver is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Derivation Solver is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
# 
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

