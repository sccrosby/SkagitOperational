function [ line_x, line_y ] = createTransect( x1, y1, x2, y2, L )
%[ line_x, line_y ] = createTransect( x1, y1, x2, y2, L )
%   Creates transect spaced evenly by L

L2 = L^2;
m = (y2-y1)/(x2-x1);
dx = sqrt(L2/(1+m^2));

if x2 < x1
    dx = -dx;
end

line_x = x1:dx:x2;
line_y = m*(line_x-x1)+y1;

% clf
% hold on
% plot([x1 x2],[y1 y2],'*')
% plot(line_x,line_y,'k.')

end

