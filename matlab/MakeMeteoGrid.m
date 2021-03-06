% Create meteo.grd and meteo.enc files
% check openearth tools path (hardcoded)

clearvars

% Add delft3d matlab tools
addpath C:\openearthtools\matlab\applications\delft3d_matlab

grid_path = '../../Grids/delft3d/'; % Set path to grid files
grid_file = 'skagit_50m.grd';       % Set grd file name
res = 50;                         % Set resolution [m]
meteo_file = 'skagit_meteo_50m.grd';    % Set meteo/enc file name     

% Use Delft3d read/write grd tool
[Grd.x,Grd.y,Grd.grd.ENC,Grd.CS,Grd.nodatavalue] = ...
    wlgrid('read',sprintf('%s%s',grid_path,grid_file));

% Generate meteo grd
Grd.dx = res; % [m]
Grd.dy = res; % [m]
Grd.x_max = max(Grd.x(:));
Grd.x_min = min(Grd.x(:));
Grd.y_max = max(Grd.y(:));
Grd.y_min = min(Grd.y(:));
[Grd.xq,Grd.yq] = meshgrid(Grd.x_min : Grd.dx : Grd.x_max+Grd.dx,...
    Grd.y_min : Grd.dy : Grd.y_max+Grd.dy);

% Write meteo.grd file using grid specified
out_file = sprintf('%s%s',grid_path,meteo_file);
wlgrid('write','Filename',out_file,'X',Grd.xq','Y',Grd.yq','AutoEnclosure');
