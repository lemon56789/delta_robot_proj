%% Delta Robot Simscape Parameters
% Units: m, rad

clearvars -except ans
clc

% Geometry
L  = 125.0e-3;      % upper arm length [m]
l  = 300.0e-3;      % lower link length [m]
wB = 46.0e-3;       % base center to motor/upper-arm joint reference [m]
uP = 27.177e-3;     % platform center to vertex/connection [m]

% Arm direction vectors in base frame
e1 = [0, -1, 0];
e2 = [sqrt(3)/2, 1/2, 0];
e3 = [-sqrt(3)/2, 1/2, 0];

% Base joint positions
B1 = wB * e1;
B2 = wB * e2;
B3 = wB * e3;

% Upper arm solid dimensions
upper_arm_dims = [L, 0.01, 0.01];   % [length, width, height] [m]
upper_arm_center = [L/2, 0, 0];
upper_arm_tip = [L/2, 0, 0];

% Joint frame rotation used in current skeleton model
% local x -> world +x
% local y -> world -z
% local z -> world +y
R_joint = [1 0 0;
           0 0 1;
           0 -1 0];

R_joint_axisfix = R_joint * [1 0 0;
                             0 -1 0;
                             0 0 -1];


% Test angles
theta0 = 0;
theta45 = pi/4;
theta90 = pi/2;

% Lower link and platform
lower_link_length = l;         % 0.300 m
platform_radius = uP;          % 0.027177 m

P1_offset = uP * e1;
P2_offset = uP * e2;
P3_offset = uP * e3;

platform_dims = [0.06, 0.06, 0.01];  % temporary visual block [m]
