%
% SMU_UPDATE_DISPLAY Callback function for SMU_DISPLAY.
%    SMU_UPDATE_DISPLAY is a callback function for the SMU_DISPLAY GUI.  
%    You will probably not want to call it directly in your own scripts.
function smu_update_display(smu)

smu_name = inputname(1);

[src1str, meas1str, auto1str, src2str, meas2str, auto2str]=smu.get_display();
ans = findobj('tag', [smu_name, '_gui_ch1_auto']);
set(ans, 'string', auto1str);
ans = findobj('tag', [smu_name, '_gui_ch1_meas']);
set(ans, 'string', meas1str);
ans = findobj('tag', [smu_name, '_gui_ch1_src']);
set(ans, 'string', src1str);
ans = findobj('tag', [smu_name, '_gui_ch2_auto']);
set(ans, 'string', auto2str);
ans = findobj('tag', [smu_name, '_gui_ch2_meas']);
set(ans, 'string', meas2str);
ans = findobj('tag', [smu_name, '_gui_ch2_src']);
set(ans, 'string', src2str);
