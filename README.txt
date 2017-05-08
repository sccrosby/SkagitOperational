Skagit Operational Model Development

As we proceed try to 
-use functions as much as possible
-Emphasize generalization, methodology will be applied to many "local models"
-include comments describing input/output and steps
-utilize git branching and comment commits appropriately

Work in progress includes
-Better treatment of Time Zones
-Pipe all running output to file rather than console (allows review of errors) (line 80-84 run_models)
-Get tides function should be run for next 10/100 years
-Remember utcCanada is the variable with the 6, 12, 18, 0 hour in it. Change variable names to improve readability
-Consider xTides vs downloading-manipulating text files served on web (NOAA, etc)

Larger improvements
-Reducing resolutoin of gridded meteo files. Will save space and have neglible impact on model
-Make switcht to Delft-FM to leverage varying grid spacing
  - Will save computation time
  - May allow higher resolution (25m) at shoreline


