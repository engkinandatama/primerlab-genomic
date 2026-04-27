import primer3

ta = primer3.thermoanalysis.ThermoAnalysis()
print(dir(ta))
try:
    print("tm calcTm:", ta.calcTm("ATGCGTACG"))
except Exception as e:
    print("calcTm error:", e)

try:
    print("tm calc_tm:", ta.calc_tm("ATGCGTACG"))
except Exception as e:
    print("calc_tm error:", e)

try:
    res = ta.calcHairpin("ATGCGTACG")
    print("hairpin calcHairpin:", res, dir(res))
    if res:
        print(res.tm, res.dg, res.dh, res.ds, res.structure)
except Exception as e:
    print("calcHairpin error:", e)

try:
    res = ta.calc_hairpin("ATGCGTACG")
    print("hairpin calc_hairpin:", res, dir(res))
    if res:
        print(res.tm, res.dg, res.dh, res.ds, res.structure)
except Exception as e:
    print("calc_hairpin error:", e)
