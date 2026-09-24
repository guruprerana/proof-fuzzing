# Experimental analysis
In this section, we first evaluate the effectiveness and transferability of the mutation strategies produced after distillation.
Establishing transfer is essential before interpreting these strategies as general failure mechanisms of the judge, rather than artifacts specific to the proofs used during discovery.
This is assessed by testing them on an evaluation set of proofs, that are disjoint from the proofs used in the discovery phase. 
We compare the ability of an unguided agent and a strategy-guided agent to produce zero-shot mutations on evaluation proofs.
The unguided agent is provided the same prompt as during the discovery phase and is asked to produce one mutation on a proof.
The strategy-guided agent is additionally given access to the strategy file.
We provide each with several independent attempts at mutating each proof.
Then all these mutated proofs are similarly passed to the error checker agent followed by three independent judge agents, and finally the judge error checker.

### Datasets.

### Learned mutation strategies transfer to unseen proofs.

### Judges become less reliable with recent research-level math.

### Cross model evaluation of mutations.

### Higher reasoning budgets have little impact.

### Span of influence of mutations.

### Trends within datasets.
