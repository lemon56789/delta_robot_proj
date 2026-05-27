%% Run fake pipeline theta_cmd through Simscape delta robot model

%clearvars -except ans
clc

%% Load parameters
run("init_delta_params.m");

%% Load fake pipeline theta trajectory
run("load_fake_pipeline_theta.m");

%% User settings - 모델명 확인
model_name = "simscape_delta_robot_trajectory";
%% model_name = "simscape_delta_robot_trajectory_axisfix";
sim_output_name = "sim_xyz";   % To Workspace variable name
sim_output_is_mm = true;       % true if Gain 1000 exists before To Workspace

%% Check required variables
required_vars = ["theta1_ts", "theta2_ts", "theta3_ts", "t_end"];
for v = required_vars
    if ~exist(v, "var")
        error("Required variable missing: %s", v);
    end
end

%% Load model if needed
model_file = fullfile(pwd, model_name + ".slx");

if ~isfile(model_file)
    error("Model file not found: %s", model_file);
end

if ~bdIsLoaded(model_name)
    load_system(model_file);
end

%% Set stop time from CSV
set_param(model_name, "StopTime", "t_end");

%% Run simulation
fprintf("\nRunning Simscape model: %s\n", model_name);
out = sim(model_name);

%% Read platform output
sim_ts = out.(sim_output_name);

sim_data = squeeze(sim_ts.Data);

if size(sim_data, 1) == 3
    sim_pos = sim_data.';
else
    sim_pos = sim_data;
end

if sim_output_is_mm
    sim_mm = sim_pos;
else
    sim_mm = 1000 * sim_pos;
end

time = sim_ts.Time;

%% Print summary
fprintf("\nSimulation complete.\n");
fprintf("Time range: %.3f s ~ %.3f s\n", time(1), time(end));

fprintf("Initial platform = [%.3f, %.3f, %.3f] mm\n", ...
    sim_mm(1,1), sim_mm(1,2), sim_mm(1,3));

fprintf("Final platform   = [%.3f, %.3f, %.3f] mm\n", ...
    sim_mm(end,1), sim_mm(end,2), sim_mm(end,3));

fprintf("x range = %.3f ~ %.3f mm\n", min(sim_mm(:,1)), max(sim_mm(:,1)));
fprintf("y range = %.3f ~ %.3f mm\n", min(sim_mm(:,2)), max(sim_mm(:,2)));
fprintf("z range = %.3f ~ %.3f mm\n", min(sim_mm(:,3)), max(sim_mm(:,3)));

%% Plot result
figure;
plot(time, sim_mm(:,1), time, sim_mm(:,2), time, sim_mm(:,3));
grid on;
xlabel("Time [s]");
ylabel("Platform position [mm]");
legend("sim_x", "sim_y", "sim_z");
title("Simscape platform trajectory from fake pipeline theta_cmd");

%% Export merged CSV with Simscape sim_x/sim_y/sim_z

% Check original table from load_fake_pipeline_theta.m
if ~exist("T", "var")
    error("Original CSV table T not found. Make sure load_fake_pipeline_theta.m keeps T in workspace.");
end

% Original CSV time in seconds, same as used for theta timeseries
csv_time_s = t;

% Simscape output time and position
sim_time_s = time;
sim_x = sim_mm(:,1);
sim_y = sim_mm(:,2);
sim_z = sim_mm(:,3);

% Interpolate Simscape output onto original CSV timestamps
sim_x_csv = interp1(sim_time_s, sim_x, csv_time_s, "linear", "extrap");
sim_y_csv = interp1(sim_time_s, sim_y, csv_time_s, "linear", "extrap");
sim_z_csv = interp1(sim_time_s, sim_z, csv_time_s, "linear", "extrap");

% Replace or create sim_x/sim_y/sim_z columns
T.sim_x = sim_x_csv;
T.sim_y = sim_y_csv;
T.sim_z = sim_z_csv;

% Optional: recompute error columns if target columns exist
if all(ismember(["target_x", "target_y", "target_z"], string(T.Properties.VariableNames)))
    T.error_x = T.target_x - T.sim_x;
    T.error_y = T.target_y - T.sim_y;
    T.error_z = T.target_z - T.sim_z;
end

% Build output path
[input_folder, input_name, ~] = fileparts(csv_path);
output_csv_path = fullfile(input_folder, input_name + "_simscape.csv");

% Write CSV
writetable(T, output_csv_path);

fprintf("\nMerged Simscape CSV exported:\n%s\n", output_csv_path);