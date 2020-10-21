import sys
from sim.perf_model import *

def get_reuse_hist(trace_file, bin_size):
  prof = Profile(trace_file)
  prof.init()
  bins, heights = prof.hmem.get_page_reuse_histogram(prof.traffic.num_reqs, bin_size)
  return bins, heights, prof

def get_dominant_reuse(bins, heights):
  ws = [r * w for r, w in zip(heights, np.linspace(0, 1.0, num=len(bins))[::-1])]
  dom_reuse = int(np.average(bins, weights=ws))
  return dom_reuse

def get_candidates(dom_reuse, max_dur):
  period_durs = []
  period_set = set()
  reuse = dom_reuse
  while reuse <= max_dur:
    nperiods = int((max_dur * 2) / reuse)
    if nperiods not in period_set: # durations that create distinct number of total periods
      period_durs.append(reuse)
      period_set.add(nperiods)
    reuse += dom_reuse
  return period_durs

if __name__ == "__main__":
  
  # Input
  trace_file = sys.argv[1]
  
  # Step 1 - Reuse Collector: Get page reuse histogram from the collected memory access trace of the particular application
  bin_size = 1000 # number of memory requests to bin together
  bins, heights, prof = get_reuse_hist(trace_file, bin_size)
  
  # Step 2 - Frequency Generator: Calculate dominant reuse + candidate period durations
  dom_reuse = get_dominant_reuse(bins, heights)
  cand_reqs_per_period = get_candidates(dom_reuse, prof.traffic.num_reqs / 2.0)

  # Step 3 - Tuner
  res_perf = []
  for reqs_per_ep in cand_reqs_per_period:
    sim = PerfModel(prof, 'Fast:NearSlow', 'history', 0.2, reqs_per_ep)
    sim.init()
    sim.run()
    print sim.stats # Dictionary with stats
    