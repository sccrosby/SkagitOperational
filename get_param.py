# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 14:36:13 2017

@author: crosby
"""


# Import custom libaraies
import op_functions

# Import standard libraries
import numpy as np


def get_param_skagit():     
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[275,109],[285,124]]) # Skagit
    param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 2     # Line number in meteo grid with Nx, Ny
    param['line_header_skip']       = 4     # Number of header lines in meteo file
    param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
    param['yLL']                    = 5343228.0
    
    # Set locations
    param['fol_model']              = '../ModelRuns/skagit_wave_50m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/skagit'
    param['fol_plots']              = '../Plots/skagit_50m'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google_drive']   = 'SkagitPlots'
    param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
    param['fname_meteo_grid']       = 'skagit_meteo_50m.grd'
    param['fname_meteo_enc']        = 'skagit_meteo_50m.enc'
    param['fname_grid']             = 'skagit_50m.grd'
    param['fname_dep']              = 'skagit_50m.dep'
    param['fname_enc']              = 'skagit_50m.enc'
    param['wind_u_name']            = 'wind_skagit.amu'    
    param['wind_v_name']            = 'wind_skagit.amv'
    param['fname_mdw']              = 'skagit_50m.mdw'
    param['run_script']             = 'run_wave.sh'
    
    # Set Output Locs
    param['output_locs']            = []
    #param['output_locs']            = ['LongB.loc',
    #                                   'CrossBN.loc',
    #                                   'CrossBS.loc']   
                                       
    # HRDPS prefixes and url
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()

    return param
    
def get_param_skagit_SC():     
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[275,109],[285,124]]) # Skagit
    param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
    param['yLL']                    = 5343228.0
    
    # Set locations
    param['fol_model']              = '../ModelRuns/skagit_wave_50m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/skagit_sc'
    param['fol_plots']              = '../Plots/skagit_50m'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google_drive']   = 'SkagitPlots'
    param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
    param['fname_meteo_grid']       = 'skagit_meteo_50m.grd'
    param['fname_meteo_enc']        = 'skagit_meteo_50m.enc'
    param['fname_grid']             = 'skagit_50m.grd'
    param['fname_dep']              = 'skagit_50m.dep'
    param['fname_enc']              = 'skagit_50m.enc'
    param['wind_u_name']            = 'wind_skagit.amu'    
    param['wind_v_name']            = 'wind_skagit.amv'
    param['fname_mdw']              = 'skagit_50m.mdw'
    param['run_script']             = 'run_wave.sh'
    param['extract_script']         = 'extract_dat.m'
    
    # Set Output Locs
    param['output_locs']            = []
#    param['output_locs']            = ['skagit_FirIslandFarms.loc',
#                                       'skagit_LT2.loc',
#                                       'skagit_Snee2.loc']   
                                       
    # HRDPS prefixes and url 
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()

    return param
    
def get_param_skagit_SC100m():     
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[270,105],[288,129]]) # Skagit
    param['plot_bounds']            = [[48.24, 48.452],[-122.600, -122.37]] 
    param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
    param['yLL']                    = 5343228.0
    
    # Set locations
    param['fol_model']              = '../ModelRuns/skagit_wave_100m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/skagit_100m'
    param['fol_plots']              = '../Plots/skagit_50m'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google']         = 'BellinghamBay'
    param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
    param['fname_meteo_grid']       = 'skagit_100m.grd'
    param['fname_meteo_enc']        = 'skagit_100m.enc'
    param['fname_grid']             = 'skagit_100m.grd'
    param['fname_dep']              = 'skagit_100m.dep'
    param['fname_enc']              = 'skagit_100m.enc'
    param['wind_u_name']            = 'wind_skagit.amu'    
    param['wind_v_name']            = 'wind_skagit.amv'
    param['fname_mdw']              = 'skagit_50m.mdw'
    param['run_script']             = 'run_wave.sh'
    param['fname_prefix_plot']      = 'Skagit_'
    
    # Set Output Locs
    param['output_locs']            = []
#    param['output_locs']            = ['skagit_FirIslandFarms.loc',
#                                       'skagit_LT2.loc',
#                                       'skagit_Snee2.loc']   
                                       
    # HRDPS prefixes and url 
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()

    return param
    
def get_param_skagitE_200m():     
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[270,105],[288,129]]) # Skagit
    param['plot_bounds']            = [[48.24, 48.452],[-122.600, -122.37]] 
    param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
    param['yLL']                    = 5343228.0
    
    # Set locations
    param['fol_model']              = '../ModelRuns/skagit_wave_100m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/skagitE_200m'
    param['fol_plots']              = '../Plots/skagit_50m'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google']         = 'BellinghamBay'
    param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
    param['fname_meteo_grid']       = 'SkagitE_200m.grd'
    param['fname_meteo_enc']        = 'SkagitE_200m.enc'
    param['fname_grid']             = 'SkagitE_200m.grd'
    param['fname_dep']              = 'SkagitE_200m.dep'
    param['fname_enc']              = 'SkagitE_200m.enc'
    param['wind_u_name']            = 'wind_skagit.amu'    
    param['wind_v_name']            = 'wind_skagit.amv'
    param['fname_mdw']              = 'skagit_50m.mdw'
    param['run_script']             = 'run_wave.sh'
    param['fname_prefix_plot']      = 'Skagit_'
    param['extract_script']         = 'extract_dat.m'
    
    # Set Output Locs
    param['output_locs']            = []
#    param['output_locs']            = ['skagit_FirIslandFarms.loc',
#                                       'skagit_LT2.loc',
#                                       'skagit_Snee2.loc']   
    # Obstacles
    param['objfile']                = 'dike.obt'
    param['objpoly']                = 'dike.pol'   
                                       
    # HRDPS prefixes and url 
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()

    return param
    
def get_param_skagitE_50m():     
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[270,105],[288,129]]) # Skagit
    param['plot_bounds']            = [[48.24, 48.452],[-122.600, -122.37]] 
    param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
    param['yLL']                    = 5343228.0
    
    # Set locations
    param['fol_model']              = '../ModelRuns/skagit_LUT_50m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/skagitE_50m'
    param['fol_plots']              = '../Plots/skagit_50m'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google']         = 'BellinghamBay'
    param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
    param['fname_meteo_grid']       = 'SkagitE_50m.grd'
    param['fname_meteo_enc']        = 'SkagitE_50m.enc'
    param['fname_grid']             = 'SkagitE_50m.grd'
    param['fname_dep']              = 'SkagitE_50m.dep'
    param['fname_enc']              = 'SkagitE_50m.enc'
    param['wind_u_name']            = 'wind_skagit.amu'    
    param['wind_v_name']            = 'wind_skagit.amv'
    param['fname_mdw']              = 'skagit_50m.mdw'
    param['run_script']             = 'run_wave.sh'
    param['fname_prefix_plot']      = 'Skagit_'
    param['extract_script']         = 'extract_dat.m'    
    
    # Set Output Locs
    param['output_locs']            = []
#    param['output_locs']            = ['skagit_FirIslandFarms.loc',
#                                       'skagit_LT2.loc',
#                                       'skagit_Snee2.loc']   
    # Obstacles
    param['objfile']                = 'dike.obt'
    param['objpoly']                = 'dike.pol'   
                                       
    # HRDPS prefixes and url 
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()

    return param
    
def get_param_bbay():   
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[270,117],[288,141]]) # Bellingham Bay
    param['plot_bounds']            = [[48.58, 48.785],[-122.645, -122.47]]  #[[48.64, 48.785],[-122.65, -122.47]]
    param['tide_file']              = 'tide_pred_9449211_xtide.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny (Actually line_number - 1, since python starts at 0)
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    
    # Set locations
    param['fol_model']              = '../ModelRuns/bbay_150m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/bbay'
    param['fol_plots']              = '../Plots/bbay'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google']         = 'BellinghamBay'
    param['fname_prefix_wind']      = 'wind_crop_' 
    param['fname_meteo_grid']       = 'Bbay_150m.grd'
    param['fname_meteo_enc']        = 'Bbay_150m.enc'
    param['fname_grid']             = 'Bbay_150m.grd'
    param['fname_dep']              = 'Bbay_150m.dep'
    param['fname_enc']              = 'Bbay_150m.enc'
    param['wind_u_name']            = 'wind_bbay.amu'    
    param['wind_v_name']            = 'wind_bbay.amv'
    param['fname_mdw']              = 'bbay.mdw'
    param['run_script']             = 'run_wave.sh'
    param['fname_prefix_plot']      = 'BellinghamBay_'
    
    # Set Output Locs
    param['output_locs']            = []
    #param['output_locs']            = ['LongB.loc',
    #                                   'CrossBN.loc',
    #                                   'CrossBS.loc']   
                                       
    # HRDPS prefixes and url
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()
    
    # Set reat-time wind observation station to compare with
    param['ndbc_sta_id']            = '46118'
    param['ndbc_lat']               = 48.724
    param['ndbc_lon']               = -122.576
    
    return param


def get_param_Puget():   
    # Model parameters contained in this dictionary, paths, file names, etc
    param = {}
    
    param['lats'] = [47.032,48.4681]
    param['lons'] = [-123.171,-122.128]
    # Length of forecast
    param['num_forecast_hours']     = 48    # numer of files [hours]
    param['crop_bounds']            = np.asarray([[270,117],[288,141]]) # Bellingham Bay
    param['plot_bounds']            = [[48.58, 48.785],[-122.645, -122.47]]  #[[48.64, 48.785],[-122.65, -122.47]]
    param['tide_file']              = 'tide_pred_9449211_xtide.txt' # Set tide file to use
    
    # Set some constants for creating amu/avu files
    param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny (Actually line_number - 1, since python starts at 0)
    param['line_header_skip']       = 3     # Number of header lines in meteo file
    
    # Set locations
    param['fol_model']              = '../ModelRuns/bbay_150m'
    param['fol_wind_grib']          = '../Data/downloads/hrdps'
    param['fol_wind_crop']          = '../Data/crop/hrdps'
    param['fol_grid']               = '../Grids/delft3d/bbay'
    param['fol_plots']              = '../Plots/bbay'
    param['fol_google']             = '../GoogleDrive'
        
    # Set file names and prefixes
    param['folname_crop_prefix']    = 'hrdps_crop_'
    param['folname_grib_prefix']    = 'hrdps_grib_'
    param['folname_google']         = 'BellinghamBay'
    param['fname_prefix_wind']      = 'wind_crop_' 
    param['fname_meteo_grid']       = 'Bbay_150m.grd'
    param['fname_meteo_enc']        = 'Bbay_150m.enc'
    param['fname_grid']             = 'Bbay_150m.grd'
    param['fname_dep']              = 'Bbay_150m.dep'
    param['fname_enc']              = 'Bbay_150m.enc'
    param['wind_u_name']            = 'wind_bbay.amu'    
    param['wind_v_name']            = 'wind_bbay.amv'
    param['fname_mdw']              = 'bbay.mdw'
    param['run_script']             = 'run_wave.sh'
    param['fname_prefix_plot']      = 'BellinghamBay_'
    
    # Set Output Locs
    param['output_locs']            = []
    #param['output_locs']            = ['LongB.loc',
    #                                   'CrossBN.loc',
    #                                   'CrossBS.loc']   
                                       
    # HRDPS prefixes and url
    param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
    param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
    param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
    param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'
    
    # Set GMT offset to local time
    param['gmt_offset']             = op_functions.get_gmt_offset_2()
    
    # Set reat-time wind observation station to compare with
    param['ndbc_sta_id']            = '46118'
    param['ndbc_lat']               = 48.724
    param['ndbc_lon']               = -122.576
    
    return param
