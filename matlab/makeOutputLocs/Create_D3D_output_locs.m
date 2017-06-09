clearvars
S = kml2struct('skagit_transects.kml');

for n = 1:length(S)
    S(n).start_lat = S(n).Lat(1);
    S(n).end_lat = S(n).Lat(2);
    S(n).start_lon = S(n).Lon(1);
    S(n).end_lon = S(n).Lon(2);
    
    %Convert to UTM (Model Domain)
    [S(n).start_x, S(n).start_y] = deg2utm(S(n).start_lat', S(n).start_lon');
    [S(n).end_x, S(n).end_y] = deg2utm(S(n).end_lat', S(n).end_lon');
end



% Generate points at 50m spacing along transects
for n = 1:length(S)
    L = 50;
    x1 = S(n).start_x;
    y1 = S(n).start_y;
    x2 = S(n).end_x;
    y2 = S(n).end_y;
    [ S(n).line_x, S(n).line_y ] = createTransect( x1, y1, x2, y2, L );
end


% Write to a location file (lat, lon) (x,y)?

for n = 1:length(S)
    fname = sprintf('%s.loc',S(n).Name);
    fid = fopen(fname,'w');
    for m = 1:length(S(n).line_x)
        fprintf(fid,'%4.3f %4.3f \n',S(n).line_x(m),S(n).line_y(m));
    end
    fclose(fid);
end

