// 番茄时钟应用
class PomodoroTimer {
    constructor() {
        // 默认设置
        this.settings = {
            workDuration: 25,
            shortBreakDuration: 5,
            longBreakDuration: 15,
            dailyGoal: 4,
            soundEnabled: true,
            notificationEnabled: false
        };

        // 状态
        this.currentMode = 'work';
        this.timeLeft = this.settings.workDuration * 60;
        this.totalTime = this.settings.workDuration * 60;
        this.isRunning = false;
        this.intervalId = null;
        this.completedPomodoros = 0;
        this.totalFocusMinutes = 0;

        // 缓存DOM元素
        this.cacheElements();

        // 加载保存的数据
        this.loadData();

        // 绑定事件
        this.bindEvents();

        // 初始化显示
        this.updateDisplay();
        this.updateProgress();
        this.updateStats();

        // 请求通知权限
        this.requestNotificationPermission();
    }

    cacheElements() {
        // 计时器显示
        this.minutesEl = document.getElementById('minutes');
        this.secondsEl = document.getElementById('seconds');
        this.progressCircle = document.querySelector('.progress-ring-circle');
        this.timerRing = document.querySelector('.timer-ring');

        // 控制按钮
        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.resetBtn = document.getElementById('reset-btn');

        // 模式按钮
        this.modeBtns = document.querySelectorAll('.mode-btn');

        // 统计显示
        this.completedCountEl = document.getElementById('completed-count');
        this.dailyGoalEl = document.getElementById('daily-goal');
        this.totalTimeEl = document.getElementById('total-time');

        // 设置面板
        this.settingsBtn = document.getElementById('settings-btn');
        this.settingsPanel = document.getElementById('settings-panel');
        this.saveSettingsBtn = document.getElementById('save-settings');

        // 设置输入
        this.workDurationInput = document.getElementById('work-duration');
        this.shortBreakDurationInput = document.getElementById('short-break-duration');
        this.longBreakDurationInput = document.getElementById('long-break-duration');
        this.dailyGoalInput = document.getElementById('daily-goal-input');
        this.soundEnabledInput = document.getElementById('sound-enabled');
        this.notificationEnabledInput = document.getElementById('notification-enabled');

        // 模态框
        this.modal = document.getElementById('modal');
        this.modalIcon = document.getElementById('modal-icon');
        this.modalTitle = document.getElementById('modal-title');
        this.modalMessage = document.getElementById('modal-message');
        this.modalBtn = document.getElementById('modal-btn');

        // 计算进度条周长
        const radius = 90;
        this.circumference = 2 * Math.PI * radius;
        this.progressCircle.style.strokeDasharray = this.circumference;
    }

    bindEvents() {
        // 开始按钮
        this.startBtn.addEventListener('click', () => this.start());

        // 暂停按钮
        this.pauseBtn.addEventListener('click', () => this.pause());

        // 重置按钮
        this.resetBtn.addEventListener('click', () => this.reset());

        // 模式选择
        this.modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (this.isRunning) {
                    if (!confirm('计时器正在运行，确定要切换模式吗？')) {
                        return;
                    }
                    this.pause();
                }
                this.setMode(btn.dataset.mode);
            });
        });

        // 设置面板切换
        this.settingsBtn.addEventListener('click', () => {
            this.settingsPanel.classList.toggle('hidden');
            this.loadSettingsToForm();
        });

        // 保存设置
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());

        // 模态框按钮
        this.modalBtn.addEventListener('click', () => this.closeModal());

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isSettingsPanelOpen()) {
                e.preventDefault();
                if (this.isRunning) {
                    this.pause();
                } else {
                    this.start();
                }
            }
            if (e.code === 'KeyR' && !this.isSettingsPanelOpen()) {
                this.reset();
            }
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && this.isRunning) {
                this.updateDisplay();
            }
        });
    }

    isSettingsPanelOpen() {
        return !this.settingsPanel.classList.contains('hidden');
    }

    start() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.startBtn.classList.add('hidden');
        this.pauseBtn.classList.remove('hidden');
        this.timerRing.classList.add('running');

        this.intervalId = setInterval(() => {
            this.timeLeft--;

            if (this.timeLeft <= 0) {
                this.complete();
            } else {
                this.updateDisplay();
                this.updateProgress();
            }
        }, 1000);

        // 更新页面标题
        this.updatePageTitle();
    }

    pause() {
        if (!this.isRunning) return;

        this.isRunning = false;
        this.startBtn.classList.remove('hidden');
        this.pauseBtn.classList.add('hidden');
        this.timerRing.classList.remove('running');

        clearInterval(this.intervalId);
        this.intervalId = null;

        // 恢复页面标题
        document.title = '番茄时钟 - Pomodoro Timer';
    }

    reset() {
        this.pause();
        this.timeLeft = this.totalTime;
        this.updateDisplay();
        this.updateProgress();
        document.title = '番茄时钟 - Pomodoro Timer';
    }

    complete() {
        this.pause();
        this.playSound();

        if (this.currentMode === 'work') {
            this.completedPomodoros++;
            this.totalFocusMinutes += this.settings.workDuration;
            this.saveData();
            this.updateStats();

            // 显示完成模态框
            this.showModal(
                '🎉',
                '太棒了！',
                `你已完成第 ${this.completedPomodoros} 个番茄！`
            );

            // 发送通知
            this.sendNotification('番茄完成！', '休息一下吧 ☕');

            // 自动切换到休息模式
            if (this.completedPomodoros % 4 === 0) {
                this.setMode('long-break');
            } else {
                this.setMode('short-break');
            }
        } else {
            // 休息完成
            this.showModal(
                '💪',
                '休息结束！',
                '准备好继续工作了吗？'
            );

            this.sendNotification('休息结束！', '准备好继续工作了吗？');
            this.setMode('work');
        }
    }

    setMode(mode) {
        this.currentMode = mode;

        // 更新按钮状态
        this.modeBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // 更新进度条颜色
        this.progressCircle.classList.remove('work-mode', 'short-break-mode', 'long-break-mode');
        this.progressCircle.classList.add(`${mode}-mode`);

        // 设置时间
        let duration;
        switch (mode) {
            case 'work':
                duration = this.settings.workDuration;
                break;
            case 'short-break':
                duration = this.settings.shortBreakDuration;
                break;
            case 'long-break':
                duration = this.settings.longBreakDuration;
                break;
        }

        this.totalTime = duration * 60;
        this.timeLeft = this.totalTime;
        this.updateDisplay();
        this.updateProgress();
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;

        this.minutesEl.textContent = minutes.toString().padStart(2, '0');
        this.secondsEl.textContent = seconds.toString().padStart(2, '0');

        if (this.isRunning) {
            this.updatePageTitle();
        }
    }

    updateProgress() {
        const progress = this.timeLeft / this.totalTime;
        const offset = this.circumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
    }

    updatePageTitle() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        const modeEmoji = this.currentMode === 'work' ? '🍅' : '☕';
        document.title = `${timeString} ${modeEmoji} 番茄时钟`;
    }

    updateStats() {
        this.completedCountEl.textContent = this.completedPomodoros;
        this.dailyGoalEl.textContent = this.settings.dailyGoal;
        this.totalTimeEl.textContent = this.totalFocusMinutes;
    }

    playSound() {
        if (!this.settings.soundEnabled) return;

        // 创建音频上下文播放提示音
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();

            const playNote = (frequency, startTime, duration) => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                oscillator.frequency.value = frequency;
                oscillator.type = 'sine';

                gainNode.gain.setValueAtTime(0.3, startTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);

                oscillator.start(startTime);
                oscillator.stop(startTime + duration);
            };

            const now = audioContext.currentTime;
            playNote(523.25, now, 0.15);        // C5
            playNote(659.25, now + 0.15, 0.15); // E5
            playNote(783.99, now + 0.3, 0.15);  // G5
            playNote(1046.50, now + 0.45, 0.3); // C6
        } catch (e) {
            console.log('无法播放声音:', e);
        }
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            // 稍后请求权限
        }
    }

    sendNotification(title, body) {
        if (!this.settings.notificationEnabled) return;
        if (!('Notification' in window)) return;

        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '🍅',
                badge: '🍅'
            });
        } else if (Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(title, {
                        body: body,
                        icon: '🍅',
                        badge: '🍅'
                    });
                }
            });
        }
    }

    showModal(icon, title, message) {
        this.modalIcon.textContent = icon;
        this.modalTitle.textContent = title;
        this.modalMessage.textContent = message;
        this.modal.classList.remove('hidden');
    }

    closeModal() {
        this.modal.classList.add('hidden');
    }

    loadSettingsToForm() {
        this.workDurationInput.value = this.settings.workDuration;
        this.shortBreakDurationInput.value = this.settings.shortBreakDuration;
        this.longBreakDurationInput.value = this.settings.longBreakDuration;
        this.dailyGoalInput.value = this.settings.dailyGoal;
        this.soundEnabledInput.checked = this.settings.soundEnabled;
        this.notificationEnabledInput.checked = this.settings.notificationEnabled;
    }

    saveSettings() {
        this.settings.workDuration = parseInt(this.workDurationInput.value) || 25;
        this.settings.shortBreakDuration = parseInt(this.shortBreakDurationInput.value) || 5;
        this.settings.longBreakDuration = parseInt(this.longBreakDurationInput.value) || 15;
        this.settings.dailyGoal = parseInt(this.dailyGoalInput.value) || 4;
        this.settings.soundEnabled = this.soundEnabledInput.checked;
        this.settings.notificationEnabled = this.notificationEnabledInput.checked;

        // 请求通知权限
        if (this.settings.notificationEnabled && 'Notification' in window) {
            Notification.requestPermission();
        }

        // 更新模式按钮显示
        this.modeBtns.forEach(btn => {
            const mode = btn.dataset.mode;
            const timeSpan = btn.querySelector('.mode-time');
            switch (mode) {
                case 'work':
                    timeSpan.textContent = `${this.settings.workDuration}分钟`;
                    break;
                case 'short-break':
                    timeSpan.textContent = `${this.settings.shortBreakDuration}分钟`;
                    break;
                case 'long-break':
                    timeSpan.textContent = `${this.settings.longBreakDuration}分钟`;
                    break;
            }
        });

        // 保存到本地存储
        this.saveData();

        // 重置当前模式
        this.setMode(this.currentMode);
        this.updateStats();

        // 隐藏设置面板
        this.settingsPanel.classList.add('hidden');

        // 显示保存成功提示
        this.showModal('✅', '设置已保存', '新的设置将在下次计时时生效');
    }

    saveData() {
        const data = {
            settings: this.settings,
            completedPomodoros: this.completedPomodoros,
            totalFocusMinutes: this.totalFocusMinutes,
            lastDate: new Date().toDateString()
        };
        localStorage.setItem('pomodoroData', JSON.stringify(data));
    }

    loadData() {
        try {
            const saved = localStorage.getItem('pomodoroData');
            if (saved) {
                const data = JSON.parse(saved);

                // 加载设置
                if (data.settings) {
                    this.settings = { ...this.settings, ...data.settings };
                }

                // 检查是否是同一天
                if (data.lastDate === new Date().toDateString()) {
                    this.completedPomodoros = data.completedPomodoros || 0;
                    this.totalFocusMinutes = data.totalFocusMinutes || 0;
                } else {
                    // 新的一天，重置统计
                    this.completedPomodoros = 0;
                    this.totalFocusMinutes = 0;
                }

                // 更新模式按钮显示
                this.modeBtns.forEach(btn => {
                    const mode = btn.dataset.mode;
                    const timeSpan = btn.querySelector('.mode-time');
                    switch (mode) {
                        case 'work':
                            timeSpan.textContent = `${this.settings.workDuration}分钟`;
                            break;
                        case 'short-break':
                            timeSpan.textContent = `${this.settings.shortBreakDuration}分钟`;
                            break;
                        case 'long-break':
                            timeSpan.textContent = `${this.settings.longBreakDuration}分钟`;
                            break;
                    }
                });

                // 更新时间
                this.totalTime = this.settings.workDuration * 60;
                this.timeLeft = this.totalTime;
            }
        } catch (e) {
            console.log('加载数据失败:', e);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.pomodoro = new PomodoroTimer();
});
