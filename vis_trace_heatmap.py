import csv, sys
import numpy as np
import matplotlib.pyplot as plt
from sim.perf_model import *

plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')

def plot_scatter(dataX, dataY, xtitle, ytitle, title, outname, format):
  plt.figure(figsize=(2.5, 2), dpi=250)
  ax = plt.subplot(111)
  plt.grid(b=True, linestyle='--')
  ax.set_axisbelow(True)
  
  plt.plot(dataX, dataY, '.', markersize=0.0001, color='black')
  ax.set_xticks([])
  ax.set_yticks([])
  
  ax.set_ylabel(ytitle, fontsize='small')
  ax.set_xlabel(xtitle, fontsize='small')
  ax.set_title(title, fontsize='small')
  
  plt.tight_layout()
  plt.savefig(outname + "." + format, format=format)
  plt.show()

def plot_heatmap(data, xtitle, ytitle, title, outname, format):
  plt.figure(figsize=(3, 2), dpi=250)
  ax = plt.subplot(111)
  ax.set_axisbelow(True)
  
  im = ax.imshow(data, cmap='Reds', interpolation='nearest', aspect='auto', origin='lower')
  plt.colorbar(im, ticks=[0, int(np.max(data))])
  # ax.set_yticks([])
  
  ax.set_ylabel(ytitle, fontsize='small')
  ax.set_xlabel(xtitle, fontsize='small')
  ax.set_title(title, fontsize='small')
  
  plt.tight_layout()
  plt.savefig(outname + "." + format, format=format)
  plt.show()


if __name__ == "__main__":
  
  # Example run: python vis_trace_heatmap.py traces/pin_traces/trace_backprop_10000.txt heatmap.csv 5000
  trace_file = sys.argv[1]
  resfile = sys.argv[2]
  reqs_per_period = int(sys.argv[3])

  prof = Profile(trace_file)
  prof.init()
  sim = PerfModel(prof, 'Fast:NearSlow', 'oracle', 0.2, reqs_per_period)
  sim.init()

  # Plot memory access trace
  plot_scatter(range(prof.traffic.num_reqs), [req.page_id for req in prof.traffic.req_seq], 'Access (Time)', 'Page (Space)', 'Memory Access Trace', 'trace', 'png')

  # Plot heatmap of per page access counts across periods
  plot_heatmap([page.oracle_counts_binned_ep for page in prof.hmem.page_list], 'Period', 'Page', 'Page Access Counts', 'heatmap', 'png')

  # Write to csv: row = page, columns = per page access counts during a period
  w = csv.writer(open(resfile, "w"))
  for page in prof.hmem.page_list:
    # prints the page's access counts across periods
    w.writerow(page.oracle_counts_binned_ep)
  
