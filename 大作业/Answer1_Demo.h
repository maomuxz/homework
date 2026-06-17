/*
 * Answer1_Demo.h - 点菜管理系统头文件
 * 深圳大学鸿蒙南向设备基础课程期末考试 - 试题一
 */

#ifndef ANSWER1_DEMO_H
#define ANSWER1_DEMO_H

#include "los_task.h"
#include "los_event.h"
#include "los_compiler.h"

/* 学号 */
#define STUDENT_ID    "2023090041"

/* 菜品数量 */
#define DISH_COUNT    7

/* 事件标志位定义（每道菜对应一个标志位） */
#define DISH_EVENT_1  (1 << 0)
#define DISH_EVENT_2  (1 << 1)
#define DISH_EVENT_3  (1 << 2)
#define DISH_EVENT_4  (1 << 3)
#define DISH_EVENT_5  (1 << 4)
#define DISH_EVENT_6  (1 << 5)
#define DISH_EVENT_7  (1 << 6)

/* 厨师任务优先级 */
#define CHEF_TASK_PRIO    10

/* 厨师任务栈大小 */
#define CHEF_TASK_STACK_SIZE  2048

/* 菜品信息结构体 */
typedef struct {
    const char *name;
    UINT32 eventFlag;
} DishInfo;

/* 函数声明 */
extern VOID PrintMenu(VOID);
extern UINT32 MenuCmdHandler(UINT32 argc, const CHAR **argv);
extern UINT32 SystemInit(VOID);
extern UINT32 ShellRegisterTask(VOID);

#endif /* ANSWER1_DEMO_H */
