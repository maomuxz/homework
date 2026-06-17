/*
 * Answer1_Demo.c - 点菜管理系统
 * 深圳大学鸿蒙南向设备基础课程期末考试 - 试题一
 * 功能：基于Task + Event IPC的点菜管理系统
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "los_task.h"
#include "los_event.h"
#include "los_compiler.h"
#include "Answer1_Demo.h"
#include "shell.h"
#include "show.h"
#include "securec.h"

/* ==================== 全局变量 ==================== */

/* 事件控制块 */
static EVENT_CB_S g_orderEvent;

/* 菜品信息数组：名称与事件标志位绑定 */
static const DishInfo g_dishList[DISH_COUNT] = {
    { "宫保鸡丁",  DISH_EVENT_1 },
    { "鱼香肉丝",  DISH_EVENT_2 },
    { "麻婆豆腐",  DISH_EVENT_3 },
    { "红烧排骨",  DISH_EVENT_4 },
    { "清蒸鲈鱼",  DISH_EVENT_5 },
    { "蒜蓉西兰花", DISH_EVENT_6 },
    { "番茄蛋汤",  DISH_EVENT_7 }
};

/* 1号厨师负责的事件掩码（前4道菜） */
#define CHEF1_EVENT_MASK  (DISH_EVENT_1 | DISH_EVENT_2 | DISH_EVENT_3 | DISH_EVENT_4)

/* 2号厨师负责的事件掩码（后3道菜） */
#define CHEF2_EVENT_MASK  (DISH_EVENT_5 | DISH_EVENT_6 | DISH_EVENT_7)

/* ==================== 厨师任务 ==================== */

/*
 * 1号厨师任务：响应前4种菜品的点单事件
 */
static VOID *ChefTask1(UINT32 arg)
{
    (VOID)arg;
    UINT32 eventRet;
    const char *chefName = "1号厨师";

    printf("[%s] 已就位，等待点单...\n", chefName);

    while (1) {
        eventRet = LOS_EventRead(&g_orderEvent, CHEF1_EVENT_MASK,
                                  LOS_WAITMODE_OR | LOS_WAITMODE_CLR, LOS_WAIT_FOREVER);
        if (eventRet == 0) {
            continue;
        }

        for (int i = 0; i < 4; i++) {
            if (eventRet & g_dishList[i].eventFlag) {
                printf("[%s] 收到点单，正在制作【%s】...\n", chefName, g_dishList[i].name);
                LOS_TaskDelay(100);
                printf("[%s] 【%s】已上菜！\n", chefName, g_dishList[i].name);
            }
        }
    }
    return NULL;
}

/*
 * 2号厨师任务：响应后3种菜品的点单事件
 */
static VOID *ChefTask2(UINT32 arg)
{
    (VOID)arg;
    UINT32 eventRet;
    const char *chefName = "2号厨师";

    printf("[%s] 已就位，等待点单...\n", chefName);

    while (1) {
        eventRet = LOS_EventRead(&g_orderEvent, CHEF2_EVENT_MASK,
                                  LOS_WAITMODE_OR | LOS_WAITMODE_CLR, LOS_WAIT_FOREVER);
        if (eventRet == 0) {
            continue;
        }

        for (int i = 4; i < DISH_COUNT; i++) {
            if (eventRet & g_dishList[i].eventFlag) {
                printf("[%s] 收到点单，正在制作【%s】...\n", chefName, g_dishList[i].name);
                LOS_TaskDelay(100);
                printf("[%s] 【%s】已上菜！\n", chefName, g_dishList[i].name);
            }
        }
    }
    return NULL;
}

/* ==================== 菜单功能 ==================== */

VOID PrintMenu(VOID)
{
    printf("\n");
    printf("========================================\n");
    printf("         欢迎光临！今日菜单\n");
    printf("========================================\n");
    for (int i = 0; i < DISH_COUNT; i++) {
        printf("  %d. %s\n", i + 1, g_dishList[i].name);
    }
    printf("========================================\n");
    printf("使用方法: menu <菜品编号>\n");
    printf("例如: menu 2 表示点第2道菜\n\n");
}

/* ==================== Shell命令处理 ==================== */

UINT32 MenuCmdHandler(UINT32 argc, const CHAR **argv)
{
    UINT32 dishIndex;
    UINT32 ret;

    /* CMD_TYPE_EX: 第一个参数(argv[0])是命令名，被parser跳过;
     * 所以argc=0表示无参数，argc>=1时argv[0]是第一个参数 */
    if (argc < 1) {
        printf("用法: menu <菜品编号>\n");
        printf("例如: menu 2 表示点第2道菜\n");
        PrintMenu();
        return 0;
    }

    dishIndex = (UINT32)atoi(argv[0]);

    if (dishIndex < 1 || dishIndex > DISH_COUNT) {
        printf("错误：菜品编号 %u 不合法！请输入 1-%d 之间的数字。\n", dishIndex, DISH_COUNT);
        return 1;
    }

    UINT32 eventFlag = g_dishList[dishIndex - 1].eventFlag;

    printf("已下单：【%s】，请稍候...\n", g_dishList[dishIndex - 1].name);

    ret = LOS_EventWrite(&g_orderEvent, eventFlag);
    if (ret != LOS_OK) {
        printf("错误：下单失败！(错误码: 0x%X)\n", ret);
        return 1;
    }

    return 0;
}

/* ==================== 系统初始化 ==================== */

UINT32 SystemInit(VOID)
{
    UINT32 ret;
    UINT32 taskId1, taskId2;
    TSK_INIT_PARAM_S taskParam;

    printf("============================================\n");
    printf("  点菜管理系统 v1.0\n");
    printf("  学号: %s\n", STUDENT_ID);
    printf("============================================\n\n");

    /* 1. 事件机制初始化 */
    ret = LOS_EventInit(&g_orderEvent);
    if (ret != LOS_OK) {
        printf("错误：事件初始化失败！(错误码: 0x%X)\n", ret);
        return ret;
    }
    printf("[系统] 事件机制初始化完成\n");

    /* 2. 创建1号厨师任务 */
    (VOID)memset_s(&taskParam, sizeof(TSK_INIT_PARAM_S), 0, sizeof(TSK_INIT_PARAM_S));
    taskParam.pfnTaskEntry    = (TSK_ENTRY_FUNC)ChefTask1;
    taskParam.uwStackSize     = CHEF_TASK_STACK_SIZE;
    taskParam.pcName           = "ChefTask1";
    taskParam.usTaskPrio       = CHEF_TASK_PRIO;
    taskParam.uwResved         = 0;

    ret = LOS_TaskCreate(&taskId1, &taskParam);
    if (ret != LOS_OK) {
        printf("错误：创建1号厨师任务失败！(错误码: 0x%X)\n", ret);
        return ret;
    }
    printf("[系统] 1号厨师任务创建成功 (ID: %u)\n", taskId1);

    /* 3. 创建2号厨师任务 */
    (VOID)memset_s(&taskParam, sizeof(TSK_INIT_PARAM_S), 0, sizeof(TSK_INIT_PARAM_S));
    taskParam.pfnTaskEntry    = (TSK_ENTRY_FUNC)ChefTask2;
    taskParam.uwStackSize     = CHEF_TASK_STACK_SIZE;
    taskParam.pcName           = "ChefTask2";
    taskParam.usTaskPrio       = CHEF_TASK_PRIO;
    taskParam.uwResved         = 0;

    ret = LOS_TaskCreate(&taskId2, &taskParam);
    if (ret != LOS_OK) {
        printf("错误：创建2号厨师任务失败！(错误码: 0x%X)\n", ret);
        return ret;
    }
    printf("[系统] 2号厨师任务创建成功 (ID: %u)\n", taskId2);

    printf("[系统] 点菜系统初始化完成！\n\n");

    return LOS_OK;
}

/* ==================== Shell命令注册（在调度器启动后执行） ==================== */

/* 在系统启动后注册shell命令并打印菜单 */
UINT32 ShellRegisterTask(VOID)
{
    UINT32 ret;

    /* 等待shell初始化完成 */
    LOS_TaskDelay(50);

    /* 触发shell命令系统延迟初始化 */
    (VOID)OsShellInit(0);

    /* 注册menu命令 */
    ret = osCmdReg(CMD_TYPE_EX, "menu", 0, MenuCmdHandler);
    if (ret != LOS_OK) {
        printf("错误：注册menu命令失败！(错误码: 0x%X)\n", ret);
    } else {
        printf("[系统] menu命令注册成功\n");
    }

    /* 打印菜单 */
    PrintMenu();

    return ret;
}
