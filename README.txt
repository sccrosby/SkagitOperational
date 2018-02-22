Skagit Operational Model (Current name is antiquated, suggested new title, SalishSeaForecasts)

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
run_script_hourly.sh get runs by crontab 24x a day to update validation plots
Current models run are D3D-Wave simulations for Bellingham Bay and Skagit Delta
Currently Plots and movies are generated of wind predictions and wave output

Next Steps:
Code and system need complete refactoring. Here is rough list of needed changes:
- Switch from Delft3d to SWAN for waves, Delft3d is difficult and hacked for python/ubuntu.
- New SWAN based system runs each hour independently, and skips hours were wind speeds are low in the middle of the basin, low wind speeds should be defined by a parameter, for now low wind speeds are those < 2.5 m/s, 
- Switch from using pygrib to wgrib, pygrib incorrectly reads wind speed data (~30% lower, reason is unknown)
- Build general/modular code to read in grib files (u,v,slp)
- Develop generic framework for each modeled basin. We will expand to additional basins including, Bellingham Bay, Skagit Delta, Seattle, tacoma, Juan de Fuca.
- Outputs will be switch from movies to images, these will be hosted thru ftp to a wwu server (instead of google drive)
- Add an additional weather product (in addition to HRDPS) that provides 7-day forecasts of SLP).

New Output plots will include:
- Wind and wave plots for each basin
- Large overall domain wind plots with slp contours
- Site-based time series of water level observations, predictions.
- Site-based MET conditions, observed and predicted 


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

Additional software installed on Ubunutu
wgrib2 - http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/, http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/compile_questions.html








