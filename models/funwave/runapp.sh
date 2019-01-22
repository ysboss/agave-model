echo RUNNING FUNWAVE
cd /workdir/input
if [ -r /workdir/nodes.txt ]
then
    mpirun -np $NP -machinefile /workdir/nodes.txt /model/FUNWAVE-TVD/src/funwave_vessel
else
    mpirun -np $NP /model/FUNWAVE-TVD/src/funwave_vessel
fi
