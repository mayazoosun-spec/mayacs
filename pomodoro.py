#!/usr/bin/env python3
"""
番茄闹钟 (Pomodoro Timer)
一个命令行番茄工作法计时器

番茄工作法：
- 工作25分钟
- 短休息5分钟
- 每完成4个番茄后，长休息15分钟
"""

import time
import threading
import sys
import os
from datetime import datetime


class PomodoroTimer:
    """番茄闹钟类"""

    # 阶段常量
    PHASE_IDLE = "idle"           # 空闲
    PHASE_WORK = "work"           # 工作
    PHASE_SHORT_BREAK = "short"   # 短休息
    PHASE_LONG_BREAK = "long"     # 长休息

    def __init__(self):
        # 默认时间配置（秒）
        self.work_duration = 25 * 60       # 25分钟工作
        self.short_break = 5 * 60          # 5分钟短休息
        self.long_break = 15 * 60          # 15分钟长休息
        self.pomodoros_for_long = 4        # 4个番茄后长休息

        # 状态变量
        self.current_phase = self.PHASE_IDLE
        self.time_remaining = 0
        self.is_running = False
        self.is_paused = False

        # 统计
        self.pomodoros_completed = 0
        self.pomodoros_today = 0
        self.session_start_date = datetime.now().date()

        # 线程控制
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def _format_time(self, seconds):
        """格式化时间显示"""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def _get_phase_name(self, phase=None):
        """获取阶段的中文名称"""
        if phase is None:
            phase = self.current_phase
        names = {
            self.PHASE_IDLE: "空闲",
            self.PHASE_WORK: "🍅 工作中",
            self.PHASE_SHORT_BREAK: "☕ 短休息",
            self.PHASE_LONG_BREAK: "🌴 长休息"
        }
        return names.get(phase, "未知")

    def _ring_alarm(self, message):
        """响铃提醒"""
        # 终端响铃
        print("\a" * 3, end="", flush=True)
        print(f"\n{'='*50}")
        print(f"⏰ {message}")
        print(f"{'='*50}\n")

    def _timer_loop(self):
        """计时器主循环"""
        while not self.stop_event.is_set():
            with self.lock:
                if self.is_running and not self.is_paused:
                    if self.time_remaining > 0:
                        self.time_remaining -= 1
                    else:
                        # 时间到，处理阶段切换
                        self._handle_phase_complete()
            time.sleep(1)

    def _handle_phase_complete(self):
        """处理阶段完成"""
        if self.current_phase == self.PHASE_WORK:
            self.pomodoros_completed += 1
            self._update_daily_stats()

            # 判断是长休息还是短休息
            if self.pomodoros_completed % self.pomodoros_for_long == 0:
                self._ring_alarm(f"太棒了！完成了 {self.pomodoros_completed} 个番茄 🍅\n   开始长休息（{self.long_break // 60}分钟）")
                self.current_phase = self.PHASE_LONG_BREAK
                self.time_remaining = self.long_break
            else:
                self._ring_alarm(f"完成一个番茄！今日第 {self.pomodoros_today} 个 🍅\n   开始短休息（{self.short_break // 60}分钟）")
                self.current_phase = self.PHASE_SHORT_BREAK
                self.time_remaining = self.short_break

        elif self.current_phase in (self.PHASE_SHORT_BREAK, self.PHASE_LONG_BREAK):
            self._ring_alarm("休息结束！准备开始下一个番茄 🍅\n   输入 'start' 开始工作")
            self.current_phase = self.PHASE_IDLE
            self.is_running = False

    def _update_daily_stats(self):
        """更新每日统计"""
        today = datetime.now().date()
        if today != self.session_start_date:
            # 新的一天，重置统计
            self.session_start_date = today
            self.pomodoros_today = 0
        self.pomodoros_today += 1

    def start(self):
        """开始番茄计时"""
        with self.lock:
            if self.is_running and not self.is_paused:
                print("⚠️  番茄钟已在运行中")
                return

            if self.is_paused:
                # 从暂停恢复
                self.is_paused = False
                print(f"▶️  继续 {self._get_phase_name()} - 剩余 {self._format_time(self.time_remaining)}")
                return

            # 开始新的番茄
            self.current_phase = self.PHASE_WORK
            self.time_remaining = self.work_duration
            self.is_running = True
            self.is_paused = False

            # 启动计时器线程（如果没有运行）
            if self.timer_thread is None or not self.timer_thread.is_alive():
                self.stop_event.clear()
                self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
                self.timer_thread.start()

            print(f"🍅 开始番茄！工作 {self.work_duration // 60} 分钟")
            print(f"   使用 'status' 查看进度，'pause' 暂停")

    def pause(self):
        """暂停计时"""
        with self.lock:
            if not self.is_running:
                print("⚠️  番茄钟未在运行")
                return
            if self.is_paused:
                print("⚠️  已经暂停了")
                return

            self.is_paused = True
            print(f"⏸️  已暂停 - {self._get_phase_name()} 剩余 {self._format_time(self.time_remaining)}")
            print("   使用 'resume' 或 'start' 继续")

    def resume(self):
        """继续计时"""
        with self.lock:
            if not self.is_paused:
                print("⚠️  番茄钟未暂停")
                return

            self.is_paused = False
            print(f"▶️  继续 {self._get_phase_name()} - 剩余 {self._format_time(self.time_remaining)}")

    def skip(self):
        """跳过当前阶段"""
        with self.lock:
            if not self.is_running:
                print("⚠️  番茄钟未在运行")
                return

            old_phase = self._get_phase_name()
            self.time_remaining = 0
            print(f"⏭️  跳过 {old_phase}")

    def stop(self):
        """停止并重置"""
        with self.lock:
            self.is_running = False
            self.is_paused = False
            self.current_phase = self.PHASE_IDLE
            self.time_remaining = 0
            print("⏹️  番茄钟已停止")

    def status(self):
        """显示当前状态"""
        with self.lock:
            print(f"\n{'─'*40}")
            print(f"状态: {self._get_phase_name()}")

            if self.is_running:
                status_text = "暂停中" if self.is_paused else "运行中"
                print(f"计时: {status_text}")
                print(f"剩余: {self._format_time(self.time_remaining)}")

                # 进度条
                if self.current_phase == self.PHASE_WORK:
                    total = self.work_duration
                elif self.current_phase == self.PHASE_SHORT_BREAK:
                    total = self.short_break
                else:
                    total = self.long_break

                progress = (total - self.time_remaining) / total
                bar_length = 20
                filled = int(bar_length * progress)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"进度: [{bar}] {progress*100:.0f}%")

            print(f"今日: {self.pomodoros_today} 个番茄 🍅")
            print(f"本轮: {self.pomodoros_completed % self.pomodoros_for_long}/{self.pomodoros_for_long} (完成{self.pomodoros_for_long}个后长休息)")
            print(f"{'─'*40}\n")

    def stats(self):
        """显示统计信息"""
        print(f"\n{'═'*40}")
        print("📊 番茄统计")
        print(f"{'═'*40}")
        print(f"今日完成: {self.pomodoros_today} 个番茄 🍅")
        print(f"本次会话: {self.pomodoros_completed} 个番茄")
        print(f"专注时间: {self.pomodoros_today * self.work_duration // 60} 分钟")
        print(f"{'═'*40}\n")

    def config(self, args):
        """配置时间参数"""
        if not args:
            print(f"\n当前配置:")
            print(f"  工作时间: {self.work_duration // 60} 分钟")
            print(f"  短休息:   {self.short_break // 60} 分钟")
            print(f"  长休息:   {self.long_break // 60} 分钟")
            print(f"  长休息周期: 每 {self.pomodoros_for_long} 个番茄")
            print(f"\n设置方法:")
            print(f"  config work <分钟>    - 设置工作时间")
            print(f"  config short <分钟>   - 设置短休息时间")
            print(f"  config long <分钟>    - 设置长休息时间")
            print(f"  config cycle <个数>   - 设置长休息周期")
            return

        if len(args) < 2:
            print("⚠️  请提供参数值，例如: config work 30")
            return

        try:
            value = int(args[1])
            if value <= 0:
                print("⚠️  请输入正整数")
                return

            param = args[0].lower()
            if param == "work":
                self.work_duration = value * 60
                print(f"✅ 工作时间设置为 {value} 分钟")
            elif param == "short":
                self.short_break = value * 60
                print(f"✅ 短休息设置为 {value} 分钟")
            elif param == "long":
                self.long_break = value * 60
                print(f"✅ 长休息设置为 {value} 分钟")
            elif param == "cycle":
                self.pomodoros_for_long = value
                print(f"✅ 长休息周期设置为 {value} 个番茄")
            else:
                print(f"⚠️  未知参数: {param}")
        except ValueError:
            print("⚠️  请输入有效的数字")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    🍅 番茄闹钟 帮助                          ║
╠══════════════════════════════════════════════════════════════╣
║  什么是番茄工作法？                                          ║
║  将工作分成25分钟的"番茄时间"，每个番茄后休息5分钟，         ║
║  完成4个番茄后休息15分钟。                                   ║
╠══════════════════════════════════════════════════════════════╣
║  命令列表:                                                   ║
║  ─────────────────────────────────────────────────────────── ║
║  start      开始一个番茄                                     ║
║  pause      暂停计时                                         ║
║  resume     继续计时                                         ║
║  skip       跳过当前阶段                                     ║
║  stop       停止并重置                                       ║
║  status     查看当前状态                                     ║
║  stats      查看统计信息                                     ║
║  config     查看/修改时间配置                                ║
║  help       显示此帮助                                       ║
║  quit/exit  退出程序                                         ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)

    def shutdown(self):
        """关闭计时器"""
        self.stop_event.set()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)


def main():
    """主函数"""
    timer = PomodoroTimer()

    print("""
╔══════════════════════════════════════════════════════════════╗
║              🍅 番茄闹钟 Pomodoro Timer 🍅                   ║
║──────────────────────────────────────────────────────────────║
║  输入 'start' 开始第一个番茄                                 ║
║  输入 'help' 查看所有命令                                    ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        while True:
            try:
                # 显示提示符（包含状态）
                with timer.lock:
                    if timer.is_running:
                        phase = timer._get_phase_name()
                        time_str = timer._format_time(timer.time_remaining)
                        status = "⏸" if timer.is_paused else "▶"
                        prompt = f"[{phase} {time_str} {status}] > "
                    else:
                        prompt = "[🍅 番茄钟] > "

                user_input = input(prompt).strip()

                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]

                if command in ("quit", "exit", "q"):
                    print("👋 再见！今天完成了 {} 个番茄 🍅".format(timer.pomodoros_today))
                    break
                elif command == "start":
                    timer.start()
                elif command == "pause":
                    timer.pause()
                elif command == "resume":
                    timer.resume()
                elif command == "skip":
                    timer.skip()
                elif command == "stop":
                    timer.stop()
                elif command == "status":
                    timer.status()
                elif command == "stats":
                    timer.stats()
                elif command == "config":
                    timer.config(args)
                elif command == "help":
                    timer.show_help()
                else:
                    print(f"⚠️  未知命令: {command}")
                    print("   输入 'help' 查看所有命令")

            except EOFError:
                break

    except KeyboardInterrupt:
        print("\n\n👋 再见！今天完成了 {} 个番茄 🍅".format(timer.pomodoros_today))
    finally:
        timer.shutdown()


if __name__ == "__main__":
    main()
