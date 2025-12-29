#!/usr/bin/env python3
"""
简单的命令行闹钟程序
支持设置多个闹钟、显示闹钟列表、取消闹钟等功能
"""

import time
import threading
import datetime
import sys
import os


class AlarmClock:
    """闹钟类"""

    def __init__(self):
        self.alarms = {}  # {id: {"time": datetime, "message": str, "active": bool}}
        self.alarm_id_counter = 1
        self.lock = threading.Lock()
        self.running = True

        # 启动闹钟检查线程
        self.check_thread = threading.Thread(target=self._check_alarms, daemon=True)
        self.check_thread.start()

    def add_alarm(self, alarm_time: datetime.datetime, message: str = "闹钟响了!") -> int:
        """添加一个闹钟"""
        with self.lock:
            alarm_id = self.alarm_id_counter
            self.alarms[alarm_id] = {
                "time": alarm_time,
                "message": message,
                "active": True
            }
            self.alarm_id_counter += 1
            return alarm_id

    def cancel_alarm(self, alarm_id: int) -> bool:
        """取消一个闹钟"""
        with self.lock:
            if alarm_id in self.alarms:
                del self.alarms[alarm_id]
                return True
            return False

    def list_alarms(self) -> list:
        """列出所有活动的闹钟"""
        with self.lock:
            result = []
            for alarm_id, alarm in self.alarms.items():
                if alarm["active"]:
                    result.append({
                        "id": alarm_id,
                        "time": alarm["time"],
                        "message": alarm["message"]
                    })
            return result

    def _check_alarms(self):
        """检查闹钟是否到时间"""
        while self.running:
            now = datetime.datetime.now()
            triggered = []

            with self.lock:
                for alarm_id, alarm in list(self.alarms.items()):
                    if alarm["active"] and alarm["time"] <= now:
                        triggered.append((alarm_id, alarm))
                        alarm["active"] = False

            for alarm_id, alarm in triggered:
                self._trigger_alarm(alarm_id, alarm)

            time.sleep(1)

    def _trigger_alarm(self, alarm_id: int, alarm: dict):
        """触发闹钟"""
        print("\n" + "=" * 50)
        print(f"🔔 闹钟 #{alarm_id} 响了!")
        print(f"⏰ 时间: {alarm['time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 消息: {alarm['message']}")
        print("=" * 50)

        # 播放提示音 (使用终端响铃)
        self._play_sound()

        # 从列表中删除已触发的闹钟
        with self.lock:
            if alarm_id in self.alarms:
                del self.alarms[alarm_id]

    def _play_sound(self):
        """播放提示音"""
        # 终端响铃
        for _ in range(3):
            print("\a", end="", flush=True)
            time.sleep(0.5)

    def stop(self):
        """停止闹钟服务"""
        self.running = False


def parse_time(time_str: str) -> datetime.datetime:
    """解析时间字符串"""
    now = datetime.datetime.now()

    # 尝试解析 HH:MM 格式
    try:
        parsed = datetime.datetime.strptime(time_str, "%H:%M")
        alarm_time = now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=0,
            microsecond=0
        )
        # 如果时间已过，设置为明天
        if alarm_time <= now:
            alarm_time += datetime.timedelta(days=1)
        return alarm_time
    except ValueError:
        pass

    # 尝试解析 HH:MM:SS 格式
    try:
        parsed = datetime.datetime.strptime(time_str, "%H:%M:%S")
        alarm_time = now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=parsed.second,
            microsecond=0
        )
        if alarm_time <= now:
            alarm_time += datetime.timedelta(days=1)
        return alarm_time
    except ValueError:
        pass

    # 尝试解析 +Nm (N分钟后) 格式
    if time_str.startswith("+") and time_str.endswith("m"):
        try:
            minutes = int(time_str[1:-1])
            return now + datetime.timedelta(minutes=minutes)
        except ValueError:
            pass

    # 尝试解析 +Ns (N秒后) 格式
    if time_str.startswith("+") and time_str.endswith("s"):
        try:
            seconds = int(time_str[1:-1])
            return now + datetime.timedelta(seconds=seconds)
        except ValueError:
            pass

    # 尝试解析 +Nh (N小时后) 格式
    if time_str.startswith("+") and time_str.endswith("h"):
        try:
            hours = int(time_str[1:-1])
            return now + datetime.timedelta(hours=hours)
        except ValueError:
            pass

    raise ValueError(f"无法解析时间: {time_str}")


def print_help():
    """打印帮助信息"""
    print("""
闹钟程序使用帮助
================

命令:
  add <时间> [消息]  - 添加闹钟
  list              - 显示所有闹钟
  cancel <ID>       - 取消指定ID的闹钟
  help              - 显示此帮助
  quit / exit       - 退出程序

时间格式:
  HH:MM      - 指定时间 (例: 08:30)
  HH:MM:SS   - 指定时间 (例: 08:30:00)
  +Nm        - N分钟后 (例: +5m)
  +Ns        - N秒后 (例: +30s)
  +Nh        - N小时后 (例: +1h)

示例:
  add 08:30 起床了!
  add +5m 该休息了
  add +30s 测试闹钟
  cancel 1
  list
""")


def main():
    """主函数"""
    print("=" * 50)
    print("      欢迎使用命令行闹钟程序")
    print("=" * 50)
    print(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("输入 'help' 查看帮助, 'quit' 退出程序")
    print()

    clock = AlarmClock()

    try:
        while True:
            try:
                cmd = input("闹钟> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split(maxsplit=2)
            command = parts[0].lower()

            if command in ("quit", "exit", "q"):
                print("再见!")
                break

            elif command == "help":
                print_help()

            elif command == "add":
                if len(parts) < 2:
                    print("错误: 请指定时间. 例: add 08:30 起床")
                    continue

                try:
                    alarm_time = parse_time(parts[1])
                    message = parts[2] if len(parts) > 2 else "闹钟响了!"
                    alarm_id = clock.add_alarm(alarm_time, message)
                    print(f"✓ 闹钟 #{alarm_id} 已设置: {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  消息: {message}")
                except ValueError as e:
                    print(f"错误: {e}")

            elif command == "list":
                alarms = clock.list_alarms()
                if not alarms:
                    print("没有活动的闹钟")
                else:
                    print("\n活动的闹钟:")
                    print("-" * 40)
                    for alarm in alarms:
                        print(f"  #{alarm['id']}: {alarm['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"       消息: {alarm['message']}")
                    print("-" * 40)
                    print()

            elif command == "cancel":
                if len(parts) < 2:
                    print("错误: 请指定闹钟ID. 例: cancel 1")
                    continue

                try:
                    alarm_id = int(parts[1])
                    if clock.cancel_alarm(alarm_id):
                        print(f"✓ 闹钟 #{alarm_id} 已取消")
                    else:
                        print(f"错误: 找不到闹钟 #{alarm_id}")
                except ValueError:
                    print("错误: 无效的闹钟ID")

            else:
                print(f"未知命令: {command}. 输入 'help' 查看帮助")

    except KeyboardInterrupt:
        print("\n程序被中断")
    finally:
        clock.stop()
        print("闹钟程序已退出")


if __name__ == "__main__":
    main()
