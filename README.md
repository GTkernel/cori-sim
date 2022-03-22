# Cori: Tuner of hybrid memory periodic page schedulers

## Memory Access Trace Collection
Memory access trace collected following the instructions in `traces/`

## Run Cori
```
python run_cori.py <path_to_trace>
```

## Hybrid Memory Simulation
`sim/` includes a lightweight (not cycle accurate) simulation of a hybrid memory system with a fast and slow memory component. 
The parameters of the performance model are tunable inside `sim/perf_model.py` 

The accuracy of the simulator has been validated with Intel's Optane Persistent Memory. You can find the analysis in the paper reference at the end.
 
## Visualize the effect of period length on the memory access trace
```
python vis_trace_heatmap.py <path_to_trace> <out.csv> <number of memory access per period> 
```
## Paper reference

<b>Cori: Dancing to the Right Beat of Periodic Data Movements over Hybrid Memory Systems.</b><br/>
Thaleia Dimitra Doudali, Daniel Zahka, Ada Gavrilovska. <br/>
In Proceedings of the 35th IEEE International Parallel and Distributed Processing Symposium (IPDPS 2021).

Extended version: [https://arxiv.org/abs/2101.07200](https://arxiv.org/abs/2101.07200)

