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
 
