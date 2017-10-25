Skagit Operational Model (Current name is antiquated, suggested new title, COSMOS_PS_Operational)

Assumed file structure on local machine (or virtual machine)

Documents/
    SkagitOperational/  (git repo)
        Archive/
        
    Grids/
        delft3d/
            skagit/
            bbay/
        delftfm/
        suntans/
        
    Data/
        raw_downloads/
            hrdps/
                max_files/
                hrdps_grib_xxxxx/            
        crop/
            hrdps/
                hrdps_crop_xxxxx/
        d3d_input/
            skagit/    
    
    ModelRuns/
        skagit_wave_50m/
        bbay_150m/
    
    Plots/
        skagit_50m/
            plotting_files/
    
    GoogleDrive/
        SkagitPlots/
        BellinghamBay/
                   
    openearthtools/ (svn repo)

Notes:
run_script.sh gets run by crontab 4x a day when we believe Env Canada has released their most recent MET predictions.
run_script_scrub.sh gets run by crontab 48x a day to scrub MET info from Davis Weatherlink stations in PS.
Current models run are D3D-Wave simulations for Bellingham Bay and Skagit Delta
Plots and movies are generated of wind predictions and wave output
Validation at Bellingham Bay buoy is included

Next Steps:
Implement DefltFM-FLOW model for entire Puget-Sound domain (DFM-PS)
Run DFM-PS on WWU cluster in 48-hour forecast mode 
Couple D3D-Wave model domains including Skagit, BellinghamBay to DFM-PS
Incorporate more validation work using NOAA buoy and weather stations as well as scrubbed Davis WeatherLink data
Optimize data management including: Download and archiving of predictions and critical model outputs

Guidance:
Emphasize repeatability, e.g. use Docker or similar for compiling
Emphasize documentation/access, e.g. use Github or similar
Emphasize modularity, e.g. generic functions that will apply to new future model domains of interest
Emphasize optimization, e.g. speed test each component, identify bottlenecks, etc.

Packages installed on Ubuntu
sudo apt install wget byacc flex gfortran g++ libmpich-dev libnetcdf-dev
sudo apt install libexpat1 libexpat1-dev libmpich-dev libmpich12 libnetcdff-dev
sudo apt install libmpich-dev libmpich12 autoconf libtool uuid-dev
sudo apt install subversion
sudo apt install python-matplotlib python-pyproj 
sudo apt install python-scipy python-netcdf4
Sudo apt install python-gdal 
sudo apt install git xtide montage graphicsmagick
sudo apt install ffmpeg
sudo apt install python-pip
pip install pytz









