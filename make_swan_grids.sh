COUNTER=0
mkdir ../SWAN_runs
while [  $COUNTER -lt 48 ]; do
   echo $COUNTER
   mkdir ../SWAN_runs/SWAN_$COUNTER
   cp INPUT ../SWAN_runs/SWAN_$COUNTER/
   cp bbay_150m_bathy.bot ../SWAN_runs/SWAN_$COUNTER/
   cp bbay_150m_coord.grd ../SWAN_runs/SWAN_$COUNTER/
   ((COUNTER=$COUNTER + 1 ))
done
