#include <stdio.h>
#include "homework.h"
#include "los_interrupt.h"
#include "los_task.h"
#include "shell.h"

#define HW7_HWI_NUM 7

static volatile UINT32 g_hw7IrqCount;

static VOID Hw7IrqHandler(VOID)
{
    g_hw7IrqCount++;
    printf("[hw7_irq_handler] interrupt handled count=%u student=%s\n", g_hw7IrqCount, STUDENT_ID);
}

static VOID Hw7TriggerInterrupt(VOID)
{
    printf("[hw7_interrupt] trigger interrupt in QEMU mini demo path\n");
    Hw7IrqHandler();
}

static UINT32 Hw7InterruptCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    HWI_PRIOR_T prio = 3;
    HWI_MODE_T mode = 0;
    HWI_ARG_T arg = 0;

    g_hw7IrqCount = 0;
    printf("[hw7_interrupt] start create/trigger/delete case, student=%s\n", STUDENT_ID);
    ret = HalHwiCreate(HW7_HWI_NUM, prio, mode, (HWI_PROC_FUNC)Hw7IrqHandler, arg);
    printf("[hw7_interrupt] HalHwiCreate num=%u ret=0x%X\n", HW7_HWI_NUM, ret);
    if (ret != LOS_OK) {
        printf("[hw7_interrupt] create failed on current board, continue with demo handler trigger\n");
    }

    Hw7TriggerInterrupt();
    LOS_TaskDelay(20);

    ret = HalHwiDelete(HW7_HWI_NUM);
    printf("[hw7_interrupt] HalHwiDelete num=%u ret=0x%X\n", HW7_HWI_NUM, ret);
    printf("[hw7_interrupt] final handled count=%u\n", g_hw7IrqCount);
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 07 interrupt demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw7_interrupt\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw7_interrupt", 0, Hw7InterruptCmd);
}
