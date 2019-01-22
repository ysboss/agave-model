echo RUNNING SWAN 
cd /workdir/input 
if [ -r /workdir/nodes.txt ]
then
    mpirun -np $NP -machinefile /workdir/nodes.txt /usr/local/bin/swan.exe
else
    mpirun -np $NP /usr/local/bin/swan.exe 
fi
