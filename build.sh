if [ "$model" == 'nhwave' ]
then
    ./build-nhwave.sh
fi

if [ "$model" == 'swan' ]
then
    ./build-swan.sh
fi

if [ "$model" == 'funwave_tvd' ]
then
    ./build-funwave.sh
fi

if [ "$model" == 'openfoam' ]
then
    ./build-openfoam.sh
fi
