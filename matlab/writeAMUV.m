function  writeAMUV( u_grid, v_grid, time, fname, Grd)
%writeAMUV( u_grid, v_grid, time, fname, Grd)
%   u,v grids should be wind in m/s
%   time in datenum for each time step
%   fname.amu,.amv file names
%   Grd structure contains meteo grid information

nodata = -999.000; %ASCII file

% Set output file names
uwnd = [fname '.amu'];
vwnd = [fname '.amv'];

% Set format line
dataline_format = [repmat('%11.3f',1,size(u_grid,2)) '\n'];

% Set nan values to nodata specification
u_grid(isnan(u_grid)) = nodata;
v_grid(isnan(v_grid)) = nodata;

% I don't know why abbass had this line.
% u_grid(:,1,:) = nodata;
% v_grid(:,1,:) = nodata;

% Open file for writing
ufid = fopen(uwnd,'w');
vfid = fopen(vwnd,'w');

% Write files simultaneaously 
uvfd = [ufid vfid];

% Write header
mfprintf(uvfd,'### START OF HEADER\n');
mfprintf(uvfd,'FileVersion      =    1.03\n');
mfprintf(uvfd,'Filetype         =    meteo_on_equidistant_grid\n');
mfprintf(uvfd,'NODATA_value     =    %7.3f\n',nodata);
mfprintf(uvfd,'n_cols           =    %i\n',size(u_grid,2));
mfprintf(uvfd,'n_rows           =    %i\n',size(u_grid,1));
mfprintf(uvfd,'grid_unit        =    m\n');
mfprintf(uvfd,'x_llcenter       =    %7.3f\n',Grd.xq(1,1));
mfprintf(uvfd,'y_llcenter       =    %7.3f\n',Grd.yq(1,1));
mfprintf(uvfd,'dx               =    %7.3f\n',Grd.dx);
mfprintf(uvfd,'dy               =    %7.3f\n',Grd.dy);
mfprintf(uvfd,'n_quantity       =    1\n');
fprintf (ufid,'quantity1        =    x_wind\n');
fprintf (vfid,'quantity1        =    y_wind\n');
mfprintf(uvfd,'unit1            =    m s-1\n');
mfprintf(uvfd,'### END OF HEADER\n');

% Set start date as vector
start_day_vec = round(datevec(time(1)));

% Write date and data
for i = 1 : length(time)
    % write date string
    mfprintf(uvfd,...
      'TIME =   %1.1f minutes since %04d-%02d-%02d %02d:%02d:%02d +00:00\n',...
      (time(i)-time(1))*24*60,start_day_vec);
  
    % Squeeze time step
    u_grid_temp = flipud(squeeze(u_grid(:,:,i)));
    v_grid_temp = flipud(squeeze(v_grid(:,:,i)));
    
    % Write data 
    for j = 1 : size(u_grid_temp,1)
        fprintf(ufid,dataline_format,u_grid_temp(j,:));
        fprintf(vfid,dataline_format,v_grid_temp(j,:));
    end

end
fclose(ufid);
fclose(vfid);

end

