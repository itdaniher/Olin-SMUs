%
% TAKE Callback function for SMU_TAKE.
%    TAKE is a callback function for the SMU_TAKE GUI.  You will probably
%    not want to call it directly in your own scripts.
function [ch1_meas, ch2_meas] = take(smu, ch1_src, ch2_src)

smu_name = inputname(1);

button_h = findobj('Tag', [smu_name, '_startbutton']);
set(button_h, 'String', 'Stop');
set(button_h, 'UserData', 'taking');
set(button_h, 'Callback', ['button_h=findobj(''Tag'', ''', smu_name, '_startbutton'');',...
    'set(button_h, ''UserData'', ''stop'');',...
    'clear button_h;']);

h = findobj('Tag', [smu_name, '_ch1function']);
smu.set_function(1, get(h, 'Value')-1);
h = findobj('Tag', [smu_name, '_ch2function']);
smu.set_function(2, get(h, 'Value')-1);

h = findobj('Tag', [smu_name, '_primsrc']);
prim_ch = get(h, 'Value');
sec_ch = 3-prim_ch;
if prim_ch==1,
    prim_vals = ch1_src;
    sec_vals = ch2_src;
else
    prim_vals = ch2_src;
    sec_vals = ch1_src;
end;
prim_fn = smu.get_function(prim_ch);
sec_fn = smu.get_function(sec_ch);

smu.set_source(prim_ch, prim_vals(1), prim_fn);
smu.set_source(sec_ch, sec_vals(1), sec_fn);

if prim_ch==1,
    h = findobj('Tag', [smu_name, '_ch1srcname']);
else
    h = findobj('Tag', [smu_name, '_ch2srcname']);
end;
xlab = deblank(get(h, 'String'));
if prim_fn==0,
    xlab = [xlab, ' (V)'];
else
    xlab = [xlab, ' (A)'];
end;

h = findobj('Tag', [smu_name, '_ch1measname']);
y1lab = deblank(get(h, 'String'));
if length(y1lab)==0,
    y1lab = 'none';
else
    if smu.get_function(1)==0,
        y1lab = [y1lab, ' (A)'];
    else
        y1lab = [y1lab, ' (V)'];
    end;
end;

h = findobj('Tag', [smu_name, '_ch2measname']);
y2lab = deblank(get(h, 'String'));
if length(y2lab)==0,
    y2lab = 'none';
else
    if smu.get_function(2)==0,
        y2lab = [y2lab, ' (A)'];
    else
        y2lab = [y2lab, ' (V)'];
    end;
end;

ch1_meas = zeros(length(sec_vals), length(prim_vals));
ch2_meas = ch1_meas;

ch1autorange_h = findobj('Tag', [smu_name, '_ch1autorange']);
ch2autorange_h = findobj('Tag', [smu_name, '_ch2autorange']);

ch1plot_h = findobj('Tag', [smu_name, '_ch1plot']);
ch2plot_h = findobj('Tag', [smu_name, '_ch2plot']);

xaxis_h = findobj('Tag', [smu_name, '_xaxis']);
y1axis_h = findobj('Tag', [smu_name, '_y1axis']);
y2axis_h = findobj('Tag', [smu_name, '_y2axis']);

smutakeplot_h = findobj('Tag', [smu_name, '_smutakeplot']);

accuracy_h = findobj('Tag', [smu_name, '_accuracy']);
%settling_h = findobj('Tag', [smu_name, '_settling']);

buffer_lengths = [1, 1, 1; 1, 1, 1; 1, 1, 1; 1, 1, 1; 5, 3, 1; 10, 5, 3];
%settle_tol = [0.5, 1, 2, 100];
%wait_times = [0, 0, 0, 0, 0.01, 0.1];

for i = 1:length(sec_vals)
    smu.set_source(sec_ch, sec_vals(i), sec_fn);
    for j = 1:length(prim_vals)
        smu.set_source(prim_ch, prim_vals(j), prim_fn);

        if get(ch1autorange_h, 'Value')==1,
            smu.autorange(1);
        end;
        if get(ch2autorange_h, 'Value')==1,
            smu.autorange(2);
        end;

        accuracy = get(accuracy_h, 'Value');
%        settling = get(settling_h, 'Value');

        if strcmp(y1lab, 'none')==0,
            buffer_length = buffer_lengths(smu.get_irange(1)+1, accuracy);
            if buffer_length==1,
                ch1_meas(i, j) = smu.get_meas(1);
            else
                buffer = zeros(1, length(buffer_length));
                for k = 1:buffer_length
                    buffer(k) = smu.get_meas(1);
                end;
                ch1_meas(i, j) = mean(buffer);
            end;
        end;

        if strcmp(y2lab, 'none')==0,
%            row = smu.get_irange(2)+1
%            col = accuracy
            buffer_length = buffer_lengths(smu.get_irange(2)+1, accuracy);
            if buffer_length==1,
                ch2_meas(i, j) = smu.get_meas(2);
            else
                buffer = zeros(1, length(buffer_length));
                for k = 1:buffer_length
                    buffer(k) = smu.get_meas(2);
                end;
                ch2_meas(i, j) = mean(buffer);
            end;
        end;
        
        if (strcmp(y1lab, 'none')==0)&(get(ch1plot_h, 'Value')==1)&(strcmp(y2lab, 'none')==0)&(get(ch2plot_h, 'Value')==1),
            [ax, h1, h2] = plotyy(prim_vals(1:j), ch1_meas(i, 1:j), prim_vals(1:j), ch2_meas(i, 1:j), 'plot');
            set(h1, 'Marker', '.');
            set(h2, 'Marker', '.');
            if get(xaxis_h, 'Value')==1,
                set(ax(1), 'Xscale', 'linear');
                set(ax(2), 'Xscale', 'linear');
            else
                set(ax(1), 'Xscale', 'log');
                set(ax(2), 'Xscale', 'log');
            end;
            if get(y1axis_h, 'Value')==1,
                set(ax(1), 'Yscale', 'linear');
            else
                set(ax(1), 'Yscale', 'log');
            end;
            if get(y2axis_h, 'Value')==1,
                set(ax(2), 'Yscale', 'linear');
            else
                set(ax(2), 'Yscale', 'log');
            end;
            xlabel(xlab);
            set(get(ax(1), 'Ylabel'), 'String', y1lab);
            set(get(ax(2), 'Ylabel'), 'String', y2lab);
        elseif (strcmp(y1lab, 'none')==0)&(get(ch1plot_h, 'Value')==1),
            plot(prim_vals(1:j), ch1_meas(i, 1:j), 'b-', prim_vals(1:j), ch1_meas(i, 1:j), 'b.');
            if get(xaxis_h, 'Value')==1,
                set(gca, 'Xscale', 'linear');
            else
                set(gca, 'Xscale', 'log');
            end;
            if get(y1axis_h, 'Value')==1,
                set(gca, 'Yscale', 'linear');
            else
                set(gca, 'Yscale', 'log');
            end;
            xlabel(xlab);
            ylabel(y1lab);
        elseif (strcmp(y2lab, 'none')==0)&(get(ch2plot_h, 'Value')==1),
            plot(prim_vals(1:j), ch2_meas(i, 1:j), 'b-', prim_vals(1:j), ch2_meas(i, 1:j), 'b.');
            if get(xaxis_h, 'Value')==1,
                set(gca, 'Xscale', 'linear');
            else
                set(gca, 'Xscale', 'log');
            end;
            if get(y1axis_h, 'Value')==1,
                set(gca, 'Yscale', 'linear');
            else
                set(gca, 'Yscale', 'log');
            end;
            xlabel(xlab);
            ylabel(y2lab);
        end;
        drawnow;
        if strcmp(get(button_h, 'UserData'), 'stop'),
           break;
        end;
    end;
    if strcmp(get(button_h, 'UserData'), 'stop'),
       break;
    end;
end;

smu.set_source(prim_ch, prim_vals(1), prim_fn);
smu.set_source(sec_ch, sec_vals(1), sec_fn);

set(button_h, 'String', 'Start');
set(button_h, 'UserData', 'idle');
set(button_h, 'Callback', ['ch1srcname_h = findobj(''Tag'', ''', smu_name, '_ch1srcname'');',...
        'ch1srcvalues_h = findobj(''Tag'', ''', smu_name, '_ch1srcvalues'');',...
        'ch1measname_h = findobj(''Tag'', ''', smu_name, '_ch1measname'');',...
        'ch2srcname_h = findobj(''Tag'', ''', smu_name, '_ch2srcname'');',...
        'ch2srcvalues_h = findobj(''Tag'', ''', smu_name, '_ch2srcvalues'');',...
        'ch2measname_h = findobj(''Tag'', ''', smu_name, '_ch2measname'');',...
        'if (length(deblank(get(ch1srcname_h, ''String'')))~=0)&(length(deblank(get(ch2srcname_h, ''String'')))~=0),',...
        '    eval([deblank(get(ch1srcname_h, ''String'')), ''=['', deblank(get(ch1srcvalues_h, ''String'')), ''];'']);',...
        '    eval([deblank(get(ch2srcname_h, ''String'')), ''=['', deblank(get(ch2srcvalues_h, ''String'')), ''];'']);',...
        '    if (length(deblank(get(ch1measname_h, ''String'')))~=0)&(length(deblank(get(ch2measname_h, ''String'')))~=0),',...
        '        eval([''['', deblank(get(ch1measname_h, ''String'')), '', '', deblank(get(ch2measname_h, ''String'')), ''] = take(', smu_name, ', '', deblank(get(ch1srcname_h, ''String'')), '', '', deblank(get(ch2srcname_h, ''String'')), '');'']);',...
        '    elseif length(deblank(get(ch1measname_h, ''String'')))~=0,',...
        '        eval([''['', deblank(get(ch1measname_h, ''String'')), '', ch2_temp] = take(', smu_name, ', '', deblank(get(ch1srcname_h, ''String'')), '', '', deblank(get(ch2srcname_h, ''String'')), '');'']);',...
        '        clear ch2_temp;',...
        '    elseif length(deblank(get(ch2measname_h, ''String'')))~=0,',...
        '        eval([''[ch1_temp, '', deblank(get(ch2measname_h, ''String'')), ''] = take(', smu_name, ', '', deblank(get(ch1srcname_h, ''String'')), '', '', deblank(get(ch2srcname_h, ''String'')), '');'']);',...
        '        clear ch1_temp;',...
        '    else',...
        '        beep;',...
        '        warning(''You must specify measurement names either for CH1 or for CH2.'');',...
        '    end;',...
        'else',...
        '    beep;',...
        '    warning(''You must specify source names and values both for CH1 and for CH2.'');',...
        'end;',...
        'clear ch1srcname_h ch1srcvalues_h ch1measname_h ch2srcname_h ch2srcvalues_h ch2measname_h;']);

