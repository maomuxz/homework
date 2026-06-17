#include <stdio.h>
#include <string.h>
#include "homework.h"
#include "los_task.h"
#include "shell.h"
#include "securec.h"

static UINT32 g_taskACount;
static UINT32 g_taskBCount;
static UINT32 g_taskDemoRun;

static VOID *Hw3TaskA(UINT32 arg)
{
    (VOID)arg;
    for (UINT32 i = 0; i < 3; i++) {
        g_taskACount++;
        printf("[hw3_task_a] count=%u student=%s\n", g_taskACount, STUDENT_ID);
        LOS_TaskDelay(20);
    }
    return NULL;
}

static VOID *Hw3TaskB(UINT32 arg)
{
    (VOID)arg;
    for (UINT32 i = 0; i < 3; i++) {
        g_taskBCount++;
        printf("[hw3_task_b] count=%u student=%s\n", g_taskBCount, STUDENT_ID);
        LOS_TaskDelay(30);
    }
    return NULL;
}

static UINT32 Hw3TaskCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    UINT32 taskIdA;
    UINT32 taskIdB;
    TSK_INIT_PARAM_S param;

    g_taskDemoRun++;
    g_taskACount = 0;
    g_taskBCount = 0;
    printf("[hw3_task] start task management case, run=%u, student=%s\n", g_taskDemoRun, STUDENT_ID);

    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = (TSK_ENTRY_FUNC)Hw3TaskA;
    param.uwStackSize = 0x800;
    param.pcName = "Hw3TaskA";
    param.usTaskPrio = 10;
    ret = LOS_TaskCreate(&taskIdA, &param);
    printf("[hw3_task] create task A ret=0x%X id=%u\n", ret, taskIdA);
    if (ret != LOS_OK) {
        return ret;
    }

    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = (TSK_ENTRY_FUNC)Hw3TaskB;
    param.uwStackSize = 0x800;
    param.pcName = "Hw3TaskB";
    param.usTaskPrio = 11;
    ret = LOS_TaskCreate(&taskIdB, &param);
    printf("[hw3_task] create task B ret=0x%X id=%u\n", ret, taskIdB);
    return ret;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 03 task management demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw3_task\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw3_task", 0, Hw3TaskCmd);
}
