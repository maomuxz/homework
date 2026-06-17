#include <stdio.h>
#include "homework.h"
#include "shell.h"
#include "shcmd.h"
#include "los_list.h"

static UINT32 Hw2StaticCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    printf("[hw2_static] static shell command, student id: %s\n", STUDENT_ID);
    return LOS_OK;
}

static UINT32 Hw2DynamicCmd(UINT32 argc, const CHAR **argv)
{
    printf("[hw2_dynamic] dynamic shell command, student id: %s\n", STUDENT_ID);
    printf("[hw2_dynamic] argc=%u\n", argc);
    if (argc > 0) {
        printf("[hw2_dynamic] first arg=%s\n", argv[0]);
    }
    return LOS_OK;
}

static CmdItem g_hw2StaticItem = {
    CMD_TYPE_EX,
    "hw2_static",
    0,
    (CmdCallBackFunc)Hw2StaticCmd
};
static CmdItemNode g_hw2StaticNode;
static UINT32 g_hw2StaticRegistered;

static UINT32 Hw2RegisterStaticCmd(VOID)
{
    CmdModInfo *cmdInfo;
    if (g_hw2StaticRegistered != 0) {
        return LOS_OK;
    }
    cmdInfo = OsCmdInfoGet();
    LOS_ListInit(&g_hw2StaticNode.list);
    g_hw2StaticNode.cmd = &g_hw2StaticItem;
    LOS_ListTailInsert(&(cmdInfo->cmdList.list), &(g_hw2StaticNode.list));
    cmdInfo->listNum++;
    g_hw2StaticRegistered = 1;
    printf("[hw2] static register by static CmdItem ret=0x0\n");
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 02 shell register demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("static command: hw2_static\n");
    printf("dynamic command: hw2_dynamic [arg]\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    UINT32 ret;
    (VOID)OsShellInit(0);
    (VOID)Hw2RegisterStaticCmd();
    ret = osCmdReg(CMD_TYPE_EX, "hw2_dynamic", 0, Hw2DynamicCmd);
    printf("[hw2] dynamic register ret=0x%X\n", ret);
    return ret;
}
