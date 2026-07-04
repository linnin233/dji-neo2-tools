#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DJI Neo 2 一键调参脚本
用法：
    1. Neo 2 开机 → USB 连电脑
    2. python neo2_tune.py
    3. 重启 Neo 2，起飞

如需恢复出厂：重置飞机，或手动改回默认值。
"""

import subprocess
import sys
import os

# ─── 工作目录切换到脚本所在目录 ───
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─── 颜色输出 ───
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

total = 0
passed = 0
failed = 0


def set_param(name: str, value: str, desc: str):
    """设置单个飞控参数"""
    global total, passed, failed
    total += 1

    # 参数名中若含 | 符，命令行的引号已处理
    cmd = [
        "python", "comm_og_service_tool.py",
        "--bulk", "NEO2", "FlycParam", "set", "--alt",
        name, value,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    # 从输出中提取结果
    ok = False
    out_line = ""
    for line in result.stdout.splitlines():
        if "=" in line and "Response on parameter" not in line:
            out_line = line.strip()
            ok = True
            break

    if result.returncode != 0 or not ok:
        failed += 1
        print(f"  {RED}[FAIL]{RESET} {desc}")
        if result.stderr.strip():
            for line in result.stderr.splitlines():
                if "Error" in line:
                    print(f"       {line}")
        return False
    else:
        passed += 1
        # 精简输出：只显示 参数名 = 值
        parts = out_line.split("=")
        val_str = parts[1].strip().split()[0] if len(parts) > 1 else "?"
        print(f"  {GREEN}[OK]{RESET}  {desc:20s} → {val_str}")
        return True


# ============================================================================
#  一、避障全关
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"{YELLOW}  一、避障全关 — 近地保护 + 所有避障{RESET}")
print(f"{YELLOW}{'='*50}{RESET}")

set_param(
    "g_config.flying_limit.avoid_ground_and_smart_landing_enable", "0",
    "近地保护+智能降落",
)
set_param(
    "enable_avoid_ground_protection", "0",
    "近地保护(底层)",
)
set_param(
    "enable_horizontal_obstacle_avoidance", "0",
    "水平避障",
)
set_param(
    "enable_downward_vision_position_and_avoidance", "0",
    "下视定位+避障",
)
set_param(
    "g_config.avoid_obstacle_limit_cfg.avoid_obstacle_enable", "0",
    "避障引擎总开关",
)
set_param(
    "user_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_avoid_enable", "0",
    "用户前避障",
)
set_param(
    "user_down_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_down_avoid_enable", "0",
    "用户下避障",
)
set_param(
    "user_back_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_back_avoid_enable", "0",
    "用户后避障",
)
set_param(
    "user_all_avoid_enable", "0",
    "全部避障(用户)",
)
# 备选方案（取消注释以启用）：
# set_param("user_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_avoid_enable", "2", "前避障=自动")
# set_param("user_down_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_down_avoid_enable", "2", "下避障=自动")
# set_param("enable_horizontal_obstacle_avoidance", "1", "水平避障=开（保留）")
# set_param("enable_downward_vision_position_and_avoidance", "1", "下视定位=开（保留）")


# ============================================================================
#  二、姿态 + 速度全开
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"{YELLOW}  二、姿态 + 速度全开{RESET}")
print(f"{YELLOW}{'='*50}{RESET}")

# ── 姿态 ──
set_param("avoid_atti_range", "60",
    "最大倾斜角 20→60°",
)
set_param("quick_spin_tors_rate_limit", "300",
    "最大旋转 200→300°/s",
)
set_param("near_gnd_vert_acc_limit_amp", "10",
    "近地加速倍率 3→10",
)

# ── 速度 ──
set_param(
    "ffg_speed_ctrl_perc|g_config.control.ffg_speed_ctrl_perc", "100",
    "Normal档前馈增益 40→100%",
)
set_param(
    "sport_ffg_speed_ctrl_perc|g_config.control.sport_ffg_speed_ctrl_perc", "100",
    "Sport档前馈增益 40→100%",
)
set_param(
    "trip_ffg_speed_ctrl_perc|g_config.control.trip_ffg_speed_ctrl_perc", "50",
    "Cine档前馈增益 8→50%",
)


# ============================================================================
#  三、限制解除
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"{YELLOW}  三、限制解除{RESET}")
print(f"{YELLOW}{'='*50}{RESET}")

set_param(
    "g_config.flying_limit.max_radius", "8000",
    "最大距离 5000→8000m",
)
set_param(
    "g_config.flying_limit.roof_limit_enable", "0",
    "屋顶限制 开→关",
)
set_param(
    "vert_vel_down_adding|g_config.control.vert_vel_down_adding", "5",
    "下降加速 0→5 m/s",
)
set_param(
    "vert_vel_down_adding_max", "-20",
    "最大下降 -6→-20 m/s",
)

# 注意：min_height_user 固件锁定最低 3m，写 0 也会被钳位回 3
# set_param("min_height_user", "0", "最低高度 3→0（固件可能拒绝）")


# ============================================================================
#  四、档位模式配置（自调区）
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"{YELLOW}  四、档位模式配置 — 根据需要取消注释{RESET}")
print(f"{YELLOW}{'='*50}{RESET}")

print(f"""
  遥控器三档开关 → 飞控 mode 编号:

    switch 上 → control_mode[0]  默认 12 (Cine平稳)
    switch 中 → control_mode[1]  默认 8  (Sport运动)
    switch 下 → control_mode[2]  默认 7  (Normal普通)

  mode 编号对照:
    3  = ATTI   (纯姿态，无GPS，隐藏模式)
    7  = Normal (GPS+视觉定位)
    8  = Sport  (高速，避障自动关)
    12 = Cine   (慢速平稳，拍视频用)

  档位专属 FFG 前馈增益:
    trip_ffg_speed_ctrl_perc   Cine档   范围 0~100, 默认 8
    ffg_speed_ctrl_perc        Normal档 范围 0~100, 默认 40
    sport_ffg_speed_ctrl_perc  Sport档  范围 0~100, 默认 40
    atti_normal_ffg_speed_ctrl_perc  ATTI档 范围 0~100, 默认 0

  注意: C→ATTI(3) 在部分固件版本上可能被忽略，建议飞行中通过实际行为验证
""")

# ── 示例：把 Cine 改成 ATTI ──
# set_param("fswitch_selection|g_config.control.control_mode[0]", "3", "档位0(Cine→ATTI)")

# ── 示例：颠倒 Normal/Sport ──
# set_param("fswitch_selection_1|g_config.control.control_mode[1]", "7", "档位1→Normal")
# set_param("fswitch_selection_2|g_config.control.control_mode[2]", "8", "档位2→Sport")

# ── 示例：ATTI 档前馈增益调到跟手 ──
# set_param("atti_normal_ffg_speed_ctrl_perc", "60", "ATTI档增益 0→60%")


# ============================================================================
#  五、刹车手感（自调区）
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"{YELLOW}  五、刹车手感 — 根据需要取消注释{RESET}")
print(f"{YELLOW}{'='*50}{RESET}")

print(f"""
  brake_sensitive_fc    飞控刹车灵敏度   范围 0~80,  默认 0.6
  brake_sensitivity     刹车增益         范围 0~150, 默认 80

  手感对照:
    0.1  = 松杆后丝滑滑行，穿越机风格，需要手动停
    0.4  = 有滑行但不会太久，偏运动
    0.6  = DJI 原厂手感，松杆干脆停住（默认）
    80   = 刹车增益默认值，越低越软
""")

# ── 取消下面注释即可启用 ──
# set_param("brake_sensitive_fc|g_config.control.brake_sensitivity_fc", "0.25", "刹车灵敏度=0.25(丝滑)")
# set_param("brake_sensitive_gain|g_config.control.brake_sensitivity", "20",  "刹车增益=20(低)")


# ============================================================================
#  六、结果汇总
# ============================================================================
print(f"\n{YELLOW}{'='*50}{RESET}")
print(f"  完成: {GREEN}{passed}{RESET} 成功 / {RED}{failed}{RESET} 失败 / {total} 总计")
print(f"{YELLOW}{'='*50}{RESET}")

if failed > 0:
    print(f"\n{RED}部分失败，请检查：{RESET}")
    print("  1. Neo 2 是否开机并 USB 连接")
    print("  2. 驱动是否已用 Zadig 替换为 libusb-win32")
    print("  3. 重试 python neo2_tune.py")
    sys.exit(1)
else:
    print(f"\n{GREEN}全部成功！重启 Neo 2 后生效。{RESET}")
    print("  避障全关 → 注意安全，飞行时不会自动刹车")
    print("  姿态激進 → 倾斜角 60°，满杆转弯很猛")
    print("  速度全开 → 前馈 100%，推杆响应最直接")
