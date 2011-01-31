gcc -D MATLAB_MEX_FILE -I "/opt/matlab/extern/include" -I "/opt/matlab/simulink/include" -L "/opt/matlab/bin/glnx86/" -lmex -lmat -lmx -lusb-1.0 -shared sfunecs.c -o sfunecs.mexglx

