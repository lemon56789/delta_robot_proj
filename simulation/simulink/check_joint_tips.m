J_mm = [
    squeeze(out.J1_xyz.Data(:,:,end)).';
    squeeze(out.J2_xyz.Data(:,:,end)).';
    squeeze(out.J3_xyz.Data(:,:,end)).'
];

array2table(J_mm, ...
    'VariableNames', {'x_mm','y_mm','z_mm'}, ...
    'RowNames', {'J1','J2','J3'})