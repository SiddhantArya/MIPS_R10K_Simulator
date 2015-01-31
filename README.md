# MIPS_R10K_Simulator
Simulator for MIPS R10000K 4-way issue superscalar processor in Python.
MIPS R10K Simulator:

A 4-way issue MIPS R10K simulator has been implemented in Python.
For the issue stage I have used an 8-entry instruction buffer that holds 8 instructions which prefetches 4 instructions per cycle in order to be given to the decode stage. An instruction is removed from the instruction buffer if and only if there is an empty slot available in the active list. Furthermore, the decode stage is responsible for mapping the source and destination operands for each instruction. In order to do this, a Map Table has been implemented that stores the current mapping of the 64 logical registers. The previos mappings of the operands are stored in the Active List.

Furthermore, MIPS R10K allows for out-of-order execution. This has been implemented with the help of 3 queue namely - Address Queue, Integer Queue and Floating Point Queue. The decode stage checks if there is an empty slot in any of these queues for the respective instruction, if not decode stalls. Once placed in these queues, the instructions can be picked up for execution in any order (thereby out-of order). This out-of-order execution is facilitated by the
Issue stage which checks whether a particular instruction is ready or not. While checking the operands for the instructions present in queue, if the operands are available the Issue stage marks respective instructions as ready for their execution to begin.

Each functional unit picks up a ready instruction from their respective queues and can execute them out-of-order. The execution units implemented are ALU1, ALU2, FPAdd, FPMul and LS units. There are a few design considerations, that have been taken into account like:

1. Issue Stage has been used for tagging instructions as ready.
2. Decode Stage is responsible for checking whether the respective data structures are available.
3. The branch instructions are executed on priority in ALU1 Execution unit.
4. There is no Branch Bubble in the implementation i.e. assuming we have a perfect fetch unit there is no delay once an instruction is mispredicted.
5. When a branch instruction is mispredicted, all the furhter instructions are flushed from the instruction buffer and have to be fetched again along with the mispredicted branch (with the extra bit changed).
6. There are different Functional Units for Addition and Multiplication.
7. Floating Point Instructions take 3 cycles to execute, but their results are available after the second cycle.
8. For Load and Store instructions, any unresolved Store should not be present.
9. Memory Disambiguation is maintained.
10. If a Store does not have the same address as any of the previous Store instruction present
in the Active List, it can be allowed to execute.
11. Maximum 4 instructions are allowed to commit.
12. All commits happen in order.
13. Multiple CDB Writes are possible.


Running Instructions:
Implemented in Python 3.4.1
for each test modify trace.txt
and run> python module.py

Contact Info:
Siddhant Arya (a.k.a Sid)
siddhant.arya18@gmail.com
