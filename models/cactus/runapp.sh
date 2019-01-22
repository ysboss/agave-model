#!/bin/bash
cd /workdir/input
if [ -r /workdir/nodes.txt ]
then
  mpirun -np $NP -machinefile /workdir/nodes.txt /usr/cactus/CactusFW2/exe/cactus_sim -Roe input.txt
else
  # SLURM automagically knows the hostfile
  mpirun -np $NP /usr/cactus/CactusFW2/exe/cactus_sim -Roe input.txt
fi
