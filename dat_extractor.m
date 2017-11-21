addpath '/home/crosby/Documents/openearthtools/matlab/applications/delft3d_matlab'


% File to extrac
fol = '../ModelRuns/skagit_LUT_50m';
file = 'wavm-skagit_50m.dat';

fid = vs_use([fol '/' file]);
%fid = vs_use([file]);

[DataFields, Dims, NVal] = qpread(fid); %Exploring the data
Hsig = qpread(fid,'hsig wave height','griddata',0,0,0);
Water_Depth = qpread(fid,'water depth','griddata',0,0,0);
Wave_induced_force = qpread(fid,'wave induced force','griddata',0,0,0);
Near_bot_vel = qpread(fid,'orbital velocity near bottom','griddata',0,0,0);
Setup = qpread(fid,'set-up due to waves','griddata',0,0,0);
Tp = qpread(fid,'smoothed peak period','griddata',0,0,0);
Tm = qpread(fid,'mean wave period T_{m01}','griddata',0,0,0);
Dir = qpread(fid,'hsig wave vector (mean direction)','griddata',0,0,0); 
WaveLength = qpread(fid,'mean wave length','griddata',0,0,0); 
Dissip = qpread(fid,'dissipation','griddata',0,0,0); 

% Extract
O.X = Hsig.X;
O.Y = Hsig.Y;
O.depth = Water_Depth.Val;
O.hs = Hsig.Val;
O.hs_x = Dir.XComp;
O.hs_y = Dir.YComp;
O.tp = Tp.Val;
O.tm = Tm.Val;
O.setup = Setup.Val;
O.near_bot_vel = Near_bot_vel.Val;
O.wave_length = WaveLength.Val;
O.dissip = Dissip.Val;
O.induced_force_x = Wave_induced_force.XComp;
O.induced_force_y = Wave_induced_force.YComp;

save('temp.mat','-struct','O')








