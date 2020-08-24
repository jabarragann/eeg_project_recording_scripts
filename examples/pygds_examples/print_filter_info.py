from pygds import GDS

d = GDS()

#Print sample rate
print('Sampling: ', d.SamplingRate)

# get all applicable filters
N = [x for x in d.GetNotchFilters()[0] if x['SamplingRate']
     == d.SamplingRate]
BP = [x for x in d.GetBandpassFilters()[0] if x['SamplingRate']
      == d.SamplingRate]

print("Notch filters")
for n in N:
    print(n)

print("Band pass filters")
for bp in BP:
    print(bp)

d.Close()