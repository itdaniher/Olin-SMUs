/*  S-Function for Olin ModCon SMU Board *****************************************************/
/*  Giampiero Campa 13-March-09 **************************************************************/

#define NUDEV 20

#define S_FUNCTION_NAME sfunecs_test
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include <time.h>

/* Vendor requests */
#define UPDATE          1
#define SET_DIGOUT      2
#define GET_DAC_VALS    3
#define SET_DAC_VALS    4
#define GET_VADC_VALS   5
#define SET_VADC_VALS   6
#define GET_IADC_VALS   7
#define SET_IADC_VALS   8
#define GET_RES_VAL     9
#define SET_RES_VAL     10
#define GET_NAME        11
#define SET_NAME        12

/* mdlCheckParameters, check parameters, this routine is called later from mdlInitializeSizes*/
#define MDL_CHECK_PARAMETERS

/* define number of detected devices as a global variable, -1 means unknown */
int nudev=-1;

/* define calibration values as global variables */
double dac0[NUDEV];
double dacgain[NUDEV];
double vadc0[NUDEV];
double vadcgain[NUDEV];
double iadc0[NUDEV];
double iadcgain[NUDEV];
double res[NUDEV];

/* start time of simulation*/
struct timespec ts_start;

static void mdlCheckParameters(SimStruct *S)
{
    /* Basic check : All parameters must be real positive vectors                            */
    real_T *pr;                            

    int_T  i, el, nEls;
    for (i = 0; i < 1; i++) {
        if (mxIsEmpty(    ssGetSFcnParam(S,i)) || mxIsSparse(   ssGetSFcnParam(S,i)) ||
            mxIsComplex(  ssGetSFcnParam(S,i)) || !mxIsNumeric( ssGetSFcnParam(S,i))  )
                  { ssSetErrorStatus(S,"Parameters must be real finite vectors"); return; } 
        pr   = mxGetPr(ssGetSFcnParam(S,i));
        nEls = mxGetNumberOfElements(ssGetSFcnParam(S,i));
        for (el = 0; el < nEls; el++) {
            if (!mxIsFinite(pr[el])) 
                  { ssSetErrorStatus(S,"Parameters must be real finite vectors"); return; }
        }
    }

	/* Check first parameter                                                                 */
    if ( mxGetNumberOfElements(ssGetSFcnParam(S,0)) != 1 )
    { ssSetErrorStatus(S,"The board index must be a scalar"); return; }
    pr=mxGetPr(ssGetSFcnParam(S,0));
    if ( (pr[0] < 0) || (pr[0] > NUDEV-1) )
    { ssSetErrorStatus(S,"The board index must be between 0 and NUDEV-1 (NUDEV=20 by default)"); return; }

    /* Check second parameter                                                                */
    if ( mxGetNumberOfElements(ssGetSFcnParam(S,1)) != 1 )
    { ssSetErrorStatus(S,"The mode parameter must be scalar"); return; }
    pr=mxGetPr(ssGetSFcnParam(S,1));
    if ( (pr[0] != 0) && (pr[0] != 1) )
    { ssSetErrorStatus(S,"The mode parameter must be either 0 or 1"); return; }

    /* Check third parameter                                                                 */
    if ( mxGetNumberOfElements(ssGetSFcnParam(S,2)) != 2 )
    { ssSetErrorStatus(S,"The scaling parameter must be a two elements vector"); return; }
    pr=mxGetPr(ssGetSFcnParam(S,2));
    if ( pr[0] == 0 )
    { ssSetErrorStatus(S,"The first element of the scaling vector must be different from zero"); return; }
}

/* mdlInitializeSizes - initialize the sizes array ********************************************/
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumSFcnParams(S,4);                          /* number of expected parameters        */

    /* Check the number of parameters and then calls mdlCheckParameters to see if they are ok */
    if (ssGetNumSFcnParams(S) == ssGetSFcnParamsCount(S))
    { mdlCheckParameters(S); if (ssGetErrorStatus(S) != NULL) return; } else return;

    ssSetNumContStates(S,0);                          /* number of continuous states          */
    ssSetNumDiscStates(S,0);                          /* number of discrete states            */

    if (!ssSetNumInputPorts(S,1)) return;             /* number of input ports                */
    ssSetInputPortWidth(S,0,1);		                  /* first input port width               */
    ssSetInputPortDirectFeedThrough(S,0,1);           /* first port direct feedthrough flag   */

    if (!ssSetNumOutputPorts(S,2)) return;            /* number of output ports               */
    ssSetOutputPortWidth(S,0,1);                      /* first output port width              */
    ssSetOutputPortWidth(S,1,1);                      /* second output port width             */
   
    ssSetNumSampleTimes(S,0);                         /* number of sample times               */

    ssSetNumRWork(S,0);                               /* number real work vector elements     */
    ssSetNumIWork(S,0);                               /* number int_T work vector elements    */
    ssSetNumPWork(S,1);                               /* number ptr work vector elements      */
    ssSetNumModes(S,0);                               /* number mode work vector elements     */
    ssSetNumNonsampledZCs(S,0);                       /* number of nonsampled zero crossing   */
}

/* mdlInitializeSampleTimes - initialize the sample times array *******************************/
static void mdlInitializeSampleTimes(SimStruct *S)
{
	double *T=mxGetPr(ssGetSFcnParam(S,3));
    
	/* Set things up to run with inherited sample time                                        */
    ssSetSampleTime(S, 0, T[0]);
    ssSetOffsetTime(S, 0, 0);
}

/* mdlStart - initialize work vectors *********************************************************/
#define MDL_START
static void mdlStart(SimStruct *S)
{
	
    ssize_t cnt;
    int err, i=0, digout=0;
    long value;

	/* retrieve pointer from pointers work vector */
	void **PWork = ssGetPWork(S);

	/* allocate buffer of 12 char */
	unsigned char *buffer;
    buffer = malloc(12*sizeof(unsigned char));

	/* check if memory allocation was ok */
	if (buffer==NULL) 
		{ ssSetErrorStatus(S,"Error in mdlStart : could not allocate buffer"); return; }

	/* if no other instance has created a list of attached devices then it must be done now */
	if (nudev < 0) {

		/* initialize count to 0 */
		nudev=0;

		/* tell how many devices are found */
		printf("ECS: %d devices found \n", nudev);
	}

	/* Save real time at start, so we can use offsets later*/
	clock_gettime (CLOCK_REALTIME, &ts_start);
}

/* mdlOutputs - compute the outputs ***********************************************************/
static void mdlOutputs(SimStruct *S, int_T tid)
{
	/* local variables */
	int                      DACA;
	real_T                   vref;
	real_T            *y1  = ssGetOutputPortRealSignal(S,0);
	real_T            *y2  = ssGetOutputPortRealSignal(S,1);
	InputRealPtrsType up1  = ssGetInputPortRealSignalPtrs(S,0);
	
	time_T				simulationTime = ssGetT(S) - ssGetTStart(S);
	struct timespec ts;
	
	time_T realTime;
	
	while (1){
		clock_gettime (CLOCK_REALTIME, &ts);
		realTime = (ts.tv_sec + ts.tv_nsec / 1e9) - (ts_start.tv_sec + ts_start.tv_nsec / 1e9);
		double aheadOfSchedule = simulationTime - realTime;
		if (aheadOfSchedule > 0){
			int sleepTime = (int) (aheadOfSchedule * 1e6);
			if (sleepTime > 5000) sleepTime = 5000;
			//printf("Ahead of schedule by %f. time = %f %f. sleep = %d\n", aheadOfSchedule, realTime, simulationTime, sleepTime);
			//fflush(stdout);
			usleep(sleepTime);
		}else{
			//printf("Behind schedule by %f. time = %f %f\n", -aheadOfSchedule, realTime, simulationTime);
			break;
		}
	}
	

	/* get index parameter */
	int i = (int) (*mxGetPr(ssGetSFcnParam(S,0))+0.3);

	/* get scaling parameters */
    real_T             *ab = mxGetPr(ssGetSFcnParam(S,2)), a = ab[0], b = ab[1];

	/* get set current (a.k.a. digital output) parameter */
    int digout = (int) (*mxGetPr(ssGetSFcnParam(S,1))+0.3);

	/* retrieve pointer from pointers work vector */
	void **PWork = ssGetPWork(S);

	/* pointer to buffer */
	unsigned char *buffer = (unsigned char*) PWork[0];

    if (digout)
        DACA = (int)(dac0[i]-dacgain[i]*res[i]*(double)(*up1[0]));
    else
        DACA = (int)(dac0[i]+dacgain[i]*(double)(*up1[0]));



    /* voltage */
    y1[0] = (real_T)realTime;

    /* current */
    y2[0] = (real_T)0;
}

/* mdlTerminate - called when the simulation is terminated ***********************************/
static void mdlTerminate(SimStruct *S) {

	/* get index parameter */
	int i = (int) (*mxGetPr(ssGetSFcnParam(S,0))+0.3);

	/* retrieve pointer from pointers work vector */
	void **PWork = ssGetPWork(S);

	/* pointer to buffer */
	unsigned char *buffer = (unsigned char*) PWork[0];

	/* reset number of devices */
	nudev=-1;

	/* deallocate structure and buffer */
	free(PWork[0]);
}

/* Trailer information to set everything up for simulink usage *******************************/
#ifdef  MATLAB_MEX_FILE                      /* Is this file being compiled as a MEX-file?   */
#include "simulink.c"                        /* MEX-file interface mechanism                 */
#else
#include "cg_sfun.h"                         /* Code generation registration function        */
#endif
