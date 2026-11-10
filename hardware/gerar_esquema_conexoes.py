"""
Gera diagrama técnico/visual de alta definição (estilo Fritzing limpo)
para a montagem completa com Divisor de Tensão (10k + 10k), LM2596,
Bateria 9V Alcalina, ESP32 30 pinos (USB-C) e MQ-137 (placa verde 4 pinos),
numerado de 1 a 12 exatamente como na tabela de conexões.
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import matplotlib.patheffects as pe


def rbox(ax, x, y, w, h, r=0.15, fc="#ffffff", ec="#222222", lw=1.5, z=2, alpha=1.0):
    p = FancyBboxPatch(
        (x + r, y + r), w - 2 * r, h - 2 * r,
        boxstyle=f"round,pad={r},rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, alpha=alpha
    )
    ax.add_patch(p)
    return p


def badge(ax, x, y, num, bg="#1e293b", fg="#ffffff", r=0.22, z=30):
    c = Circle((x, y), r, facecolor=bg, edgecolor="#ffffff", linewidth=1.8, zorder=z)
    ax.add_patch(c)
    ax.text(x, y, str(num), color=fg, fontsize=9.5, fontweight="bold",
            ha="center", va="center", zorder=z + 1, family="sans-serif")


def wire(ax, pts, color="#ef4444", lw=3.6, outline="#111827", z=15, dashed=False):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ls = "--" if dashed else "-"
    line, = ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls,
                    solid_capstyle="round", solid_joinstyle="round", zorder=z)
    line.set_path_effects([
        pe.Stroke(linewidth=lw + 1.8, foreground=outline),
        pe.Normal()
    ])
    for px, py in (pts[0], pts[-1]):
        ax.add_patch(Circle((px, py), 0.09, facecolor=color, edgecolor=outline, linewidth=1.2, zorder=z + 1))


def draw_resistor_h(ax, x1, x2, y, label="10kΩ", z=18):
    ax.plot([x1, x2], [y, y], color="#94a3b8", lw=3.0, solid_capstyle="round", zorder=z)
    for px in (x1, x2):
        ax.add_patch(Circle((px, y), 0.085, facecolor="#64748b", edgecolor="#0f172a", lw=1.0, zorder=z + 1))
    cx = (x1 + x2) / 2
    bw, bh = min(1.05, abs(x2 - x1) * 0.58), 0.34
    rbox(ax, cx - bw / 2, y - bh / 2, bw, bh, r=0.10, fc="#dfc18d", ec="#78582b", lw=1.4, z=z + 2)
    bands = [(-0.30, "#6b3410"), (-0.12, "#111111"), (0.06, "#ea580c"), (0.28, "#ca8a04")]
    for off, col in bands:
        bx = cx + off * bw
        ax.add_patch(Rectangle((bx - 0.035, y - bh / 2 + 0.02), 0.07, bh - 0.04,
                               facecolor=col, edgecolor="none", zorder=z + 3))
    if label:
        ax.text(cx, y + bh / 2 + 0.16, label, fontsize=9, fontweight="bold",
                ha="center", va="bottom", color="#0f172a", zorder=z + 25,
                bbox=dict(boxstyle="round,pad=0.16", fc="#fffbeb", ec="#f59e0b", lw=1.0))


def draw_resistor_v(ax, x, y1, y2, label="10kΩ", z=18):
    ax.plot([x, x], [y1, y2], color="#94a3b8", lw=3.0, solid_capstyle="round", zorder=z)
    for py in (y1, y2):
        ax.add_patch(Circle((x, py), 0.085, facecolor="#64748b", edgecolor="#0f172a", lw=1.0, zorder=z + 1))
    cy = (y1 + y2) / 2
    bw, bh = 0.34, min(0.95, abs(y2 - y1) * 0.58)
    rbox(ax, x - bw / 2, cy - bh / 2, bw, bh, r=0.10, fc="#dfc18d", ec="#78582b", lw=1.4, z=z + 2)
    bands = [(0.28, "#6b3410"), (0.10, "#111111"), (-0.08, "#ea580c"), (-0.28, "#ca8a04")]
    for off, col in bands:
        by = cy + off * bh
        ax.add_patch(Rectangle((x - bw / 2 + 0.02, by - 0.032), bw - 0.04, 0.064,
                               facecolor=col, edgecolor="none", zorder=z + 3))
    if label:
        ax.text(x + bw / 2 + 0.16, cy, label, fontsize=9, fontweight="bold",
                ha="left", va="center", color="#0f172a", zorder=z + 25,
                bbox=dict(boxstyle="round,pad=0.16", fc="#fffbeb", ec="#f59e0b", lw=1.0))


def main(out_path):
    fig, ax = plt.subplots(figsize=(22, 14.0), dpi=130)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 14.0)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")

    # =========================================================================
    # TÍTULO
    # =========================================================================
    ax.text(11.0, 13.55, "Esquema Completo de Ligações — Versão com Divisor de Tensão (10kΩ + 10kΩ)",
            fontsize=17, fontweight="bold", ha="center", va="center", color="#0f172a")
    ax.text(11.0, 13.14,
            "ESP32 alimentado via USB-C  •  LM2596 regulado em 5,0V alimentando o MQ-137  •  Divisor reduz AOUT (5V → 2,5V máx no pino D34)  •  GND comum",
            fontsize=10.5, ha="center", va="center", color="#475569")

    # =========================================================================
    # 1. BATERIA 9V ALCALINA (canto superior esquerdo, bem separada do USB)
    # =========================================================================
    bx, by, bw, bh = 0.75, 8.65, 2.25, 3.25
    rbox(ax, bx, by, bw, bh, r=0.18, fc="#1f2937", ec="#0f172a", lw=2.0, z=4)
    rbox(ax, bx + 0.04, by + bh - 1.02, bw - 0.08, 0.98, r=0.14, fc="#c87d32", ec="none", lw=0, z=5)
    bat_plus = (bx + 0.62, by + bh + 0.18)
    bat_minus = (bx + 1.62, by + bh + 0.18)
    rbox(ax, bat_plus[0] - 0.18, by + bh - 0.02, 0.36, 0.22, r=0.04, fc="#94a3b8", ec="#334155", lw=1.2, z=5)
    rbox(ax, bat_minus[0] - 0.22, by + bh - 0.02, 0.44, 0.22, r=0.04, fc="#94a3b8", ec="#334155", lw=1.2, z=5)
    ax.text(bat_plus[0], by + bh - 0.42, "+", fontsize=16, fontweight="bold", color="#ffffff", ha="center", va="center", zorder=6)
    ax.text(bat_minus[0], by + bh - 0.42, "−", fontsize=16, fontweight="bold", color="#ffffff", ha="center", va="center", zorder=6)
    ax.text(bx + bw / 2, by + 1.45, "BATERIA 9V", fontsize=11, fontweight="bold", color="#f8fafc", ha="center", va="center", zorder=6)
    ax.text(bx + bw / 2, by + 1.03, "ALCALINA", fontsize=10, fontweight="bold", color="#fbbf24", ha="center", va="center", zorder=6)
    ax.text(bx + bw / 2, by + 0.60, "(Duracell / Energizer)", fontsize=8, color="#cbd5e1", ha="center", va="center", zorder=6)

    # =========================================================================
    # 2. MÓDULO LM2596 (ao lado da bateria, acima do bloco USB)
    # =========================================================================
    lx, ly, lw_m, lh_m = 4.0, 9.15, 3.25, 2.65
    rbox(ax, lx, ly, lw_m, lh_m, r=0.14, fc="#1d4ed8", ec="#1e3a8a", lw=2.0, z=4)
    lm_in_plus = (lx + 0.32, ly + lh_m - 0.42)
    lm_in_minus = (lx + 0.32, ly + 0.42)
    lm_out_plus = (lx + lw_m - 0.32, ly + lh_m - 0.42)
    lm_out_minus = (lx + lw_m - 0.32, ly + 0.42)
    for px, py, lbl, ha_off in [
        (*lm_in_plus, "IN+", 0.24),
        (*lm_in_minus, "IN−", 0.24),
        (*lm_out_plus, "OUT+", -0.24),
        (*lm_out_minus, "OUT−", -0.24),
    ]:
        ax.add_patch(Circle((px, py), 0.16, facecolor="#e2e8f0", edgecolor="#475569", lw=1.4, zorder=6))
        ax.text(px + ha_off, py, lbl, fontsize=8.5, fontweight="bold", color="#ffffff",
                ha="left" if ha_off > 0 else "right", va="center", zorder=6)

    rbox(ax, lx + 1.12, ly + 1.02, 1.0, 0.90, r=0.15, fc="#334155", ec="#0f172a", lw=1.3, z=5)
    ax.add_patch(Circle((lx + 1.62, ly + 1.47), 0.34, facecolor="#1e293b", edgecolor="#475569", lw=1.0, zorder=6))
    ax.add_patch(Circle((lx + 0.84, ly + 1.47), 0.24, facecolor="#cbd5e1", edgecolor="#334155", lw=1.2, zorder=6))
    ax.add_patch(Circle((lx + 2.42, ly + 1.47), 0.24, facecolor="#cbd5e1", edgecolor="#334155", lw=1.2, zorder=6))
    rbox(ax, lx + 1.15, ly + 0.32, 0.95, 0.50, r=0.05, fc="#0284c7", ec="#0c4a6e", lw=1.2, z=6)
    ax.add_patch(Circle((lx + 1.42, ly + 0.57), 0.12, facecolor="#facc15", edgecolor="#713f12", lw=1.0, zorder=7))
    ax.text(lx + lw_m / 2, ly + lh_m - 0.22, "LM2596 (Step-Down)", fontsize=9.5, fontweight="bold",
            color="#bfdbfe", ha="center", va="center", zorder=6)
    ax.text(lx + lw_m / 2, ly - 0.18, "ATENÇÃO: Regular trimpot p/ 5,0V!",
            fontsize=8.2, fontweight="bold", color="#b45309", ha="center", va="top", zorder=20,
            bbox=dict(boxstyle="round,pad=0.2", fc="#fef3c7", ec="#f59e0b", lw=1.0))

    # =========================================================================
    # 3. PROTOBOARD GRANDE (830 FUROS) — centro-direita
    # =========================================================================
    pb_x, pb_y = 8.35, 4.55
    pb_w, pb_h = 9.35, 7.25
    rbox(ax, pb_x, pb_y, pb_w, pb_h, r=0.18, fc="#f1f5f9", ec="#94a3b8", lw=2.0, z=2)
    ax.text(pb_x + pb_w / 2, pb_y + pb_h + 0.18,
            "PROTOBOARD GRANDE (830 furos — cada coluna vertical a–e / f–j é interligada)",
            fontsize=9.5, fontweight="bold", color="#334155", ha="center", va="bottom")

    n_cols = 28
    col_x0 = pb_x + 0.55
    col_dx = (pb_w - 1.05) / (n_cols - 1)
    cols_x = [col_x0 + i * col_dx for i in range(n_cols)]

    top_plus_y = pb_y + pb_h - 0.40
    top_gnd_y = pb_y + pb_h - 0.76
    rows_top_y = [pb_y + 4.28 + k * 0.33 for k in range(5)]  # f, g, h, i, j
    row_labels_top = ["f", "g", "h", "i", "j"]

    ravine_y = pb_y + 3.54
    rbox(ax, pb_x + 0.12, ravine_y - 0.21, pb_w - 0.24, 0.42, r=0.06, fc="#cbd5e1", ec="#94a3b8", lw=0.8, z=3)

    rows_bot_y = [pb_y + 1.54 + k * 0.33 for k in range(5)]  # a, b, c, d, e
    row_labels_bot = ["a", "b", "c", "d", "e"]
    bot_plus_y = pb_y + 0.78
    bot_gnd_y = pb_y + 0.42

    ax.plot([pb_x + 0.35, pb_x + pb_w - 0.35], [top_plus_y + 0.15, top_plus_y + 0.15], color="#ef4444", lw=1.8, zorder=3)
    ax.plot([pb_x + 0.35, pb_x + pb_w - 0.35], [top_gnd_y - 0.15, top_gnd_y - 0.15], color="#2563eb", lw=1.8, zorder=3)
    ax.plot([pb_x + 0.35, pb_x + pb_w - 0.35], [bot_plus_y + 0.15, bot_plus_y + 0.15], color="#ef4444", lw=1.8, zorder=3)
    ax.plot([pb_x + 0.35, pb_x + pb_w - 0.35], [bot_gnd_y - 0.15, bot_gnd_y - 0.15], color="#2563eb", lw=1.8, zorder=3)

    ax.text(pb_x + 0.22, top_plus_y, "+", color="#dc2626", fontsize=11, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(pb_x + 0.22, top_gnd_y, "−", color="#1d4ed8", fontsize=12, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(pb_x + 0.22, bot_plus_y, "+", color="#dc2626", fontsize=11, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(pb_x + 0.22, bot_gnd_y, "−", color="#1d4ed8", fontsize=12, fontweight="bold", ha="center", va="center", zorder=4)

    ax.text(pb_x + pb_w - 0.16, top_plus_y, "5V", color="#dc2626", fontsize=8, fontweight="bold", ha="right", va="center", zorder=4)
    ax.text(pb_x + pb_w - 0.16, bot_gnd_y - 0.22, "GND Comum", color="#1d4ed8", fontsize=7.8, fontweight="bold", ha="right", va="top", zorder=4)

    for lbl, ry in zip(row_labels_top, rows_top_y):
        ax.text(pb_x + 0.26, ry, lbl, color="#64748b", fontsize=7.5, fontweight="bold", ha="center", va="center", zorder=4)
    for lbl, ry in zip(row_labels_bot, rows_bot_y):
        ax.text(pb_x + 0.26, ry, lbl, color="#64748b", fontsize=7.5, fontweight="bold", ha="center", va="center", zorder=4)

    idx_aout = 17
    idx_junc = 22
    rbox(ax, cols_x[idx_junc] - 0.13, rows_bot_y[0] - 0.13, 0.26,
         rows_bot_y[-1] - rows_bot_y[0] + 0.26, r=0.06, fc="#fde047", ec="#ca8a04", lw=1.3, z=3, alpha=0.65)
    rbox(ax, cols_x[idx_aout] - 0.13, rows_bot_y[0] - 0.13, 0.26,
         rows_bot_y[-1] - rows_bot_y[0] + 0.26, r=0.06, fc="#fed7aa", ec="#ea580c", lw=1.1, z=3, alpha=0.50)

    hole_r = 0.055
    for i, cx in enumerate(cols_x):
        for ry in rows_top_y + rows_bot_y:
            ax.add_patch(Circle((cx, ry), hole_r, facecolor="#334155", edgecolor="#cbd5e1", lw=0.4, zorder=4))
        if i % 6 != 5:
            for py in (top_plus_y, top_gnd_y, bot_plus_y, bot_gnd_y):
                ax.add_patch(Circle((cx, py), hole_r, facecolor="#334155", edgecolor="#cbd5e1", lw=0.4, zorder=4))

    # =========================================================================
    # 4. ESP32 30 PINOS (colunas 1..15; linha 'a' embaixo fica LIVRE)
    # =========================================================================
    esp_cols = list(range(1, 16))
    esp_x0 = cols_x[esp_cols[0]] - 0.35
    esp_x1 = cols_x[esp_cols[-1]] + 0.32
    esp_y0 = rows_bot_y[1] - 0.17
    esp_y1 = rows_top_y[4] + 0.17
    rbox(ax, esp_x0, esp_y0, esp_x1 - esp_x0, esp_y1 - esp_y0, r=0.14, fc="#111827", ec="#374151", lw=2.0, z=8)

    # Blindagem metálica Wi-Fi mais compacta verticalmente p/ não encostar nos rótulos dos pinos!
    rbox(ax, esp_x1 - 2.35, esp_y0 + 0.78, 1.75, esp_y1 - esp_y0 - 1.56, r=0.06, fc="#9ca3af", ec="#4b5563", lw=1.2, z=9)
    ax.text(esp_x1 - 1.48, (esp_y0 + esp_y1) / 2, "ESP32\n30 Pinos", fontsize=9.5, fontweight="bold",
            color="#111827", ha="center", va="center", zorder=10)

    usb_y = (esp_y0 + esp_y1) / 2
    rbox(ax, esp_x0 - 0.32, usb_y - 0.42, 0.52, 0.84, r=0.07, fc="#cbd5e1", ec="#475569", lw=1.4, z=10)
    ax.text(esp_x0 + 0.50, usb_y, "USB-C", fontsize=7.8, fontweight="bold", color="#94a3b8", ha="left", va="center", zorder=10)

    top_pins = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
    bot_pins = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19", "D21", "RX0", "TX0", "D22", "D23"]

    for idx_p, col_i in enumerate(esp_cols):
        px = cols_x[col_i]
        t_lbl = top_pins[idx_p]
        b_lbl = bot_pins[idx_p]
        is_d34 = (t_lbl == "D34")
        is_gnd = (b_lbl == "GND")
        ax.add_patch(Circle((px, esp_y1 - 0.15), 0.09 if is_d34 else 0.058,
                            facecolor="#facc15" if is_d34 else "#d1d5db", edgecolor="#000000", lw=0.8, zorder=12))
        ax.add_patch(Circle((px, esp_y0 + 0.15), 0.09 if is_gnd else 0.058,
                            facecolor="#facc15" if is_gnd else "#d1d5db", edgecolor="#000000", lw=0.8, zorder=12))
        if t_lbl in ("VIN", "GND", "D34", "VN"):
            ax.text(px, esp_y1 - 0.30, t_lbl, fontsize=7.5 if is_d34 else 6.2,
                    fontweight="bold", color="#fde047" if is_d34 else "#cbd5e1",
                    ha="center", va="top", rotation=90, zorder=13)
        if b_lbl in ("3V3", "GND", "D15"):
            ax.text(px, esp_y0 + 0.30, b_lbl, fontsize=7.5 if is_gnd else 6.2,
                    fontweight="bold", color="#fde047" if is_gnd else "#cbd5e1",
                    ha="center", va="bottom", rotation=90, zorder=13)

    esp_d34_pt = (cols_x[esp_cols[11]], esp_y1 - 0.15)
    esp_gnd_hole = (cols_x[esp_cols[1]], rows_bot_y[0])

    # =========================================================================
    # 5. CABO USB-C (#12) -> NOTEBOOK / POWERBANK (posicionado abaixo da bateria/LM2596!)
    # =========================================================================
    rbox(ax, esp_x0 - 1.05, usb_y - 0.34, 0.75, 0.68, r=0.08, fc="#334155", ec="#0f172a", lw=1.5, z=11)
    nb_x, nb_y, nb_w, nb_h = 0.85, 5.20, 4.35, 1.55
    wire(ax, [(esp_x0 - 1.05, usb_y), (6.35, usb_y), (6.35, nb_y + nb_h / 2), (nb_x + nb_w, nb_y + nb_h / 2)],
         color="#475569", lw=5.5, z=9)
    rbox(ax, nb_x, nb_y, nb_w, nb_h, r=0.16, fc="#e2e8f0", ec="#475569", lw=1.8, z=10)
    ax.text(nb_x + nb_w / 2, nb_y + 0.98, "NOTEBOOK / POWERBANK", fontsize=10, fontweight="bold",
            color="#0f172a", ha="center", va="center", zorder=11)
    ax.text(nb_x + nb_w / 2, nb_y + 0.50, "Alimenta o ESP32 pelo cabo USB-C", fontsize=8.6,
            color="#334155", ha="center", va="center", zorder=11)
    badge(ax, 6.35, 6.95, 12, bg="#334155")

    # =========================================================================
    # 6. SENSOR MQ-137 (PLACA VERDE 4 PINOS, direita da protoboard)
    # =========================================================================
    mq_x, mq_y, mq_w, mq_h = 18.45, 6.3, 2.95, 2.55
    rbox(ax, mq_x, mq_y, mq_w, mq_h, r=0.14, fc="#15803d", ec="#14532d", lw=2.0, z=4)
    ax.add_patch(Circle((mq_x + 1.98, mq_y + mq_h / 2), 0.76, facecolor="#94a3b8", edgecolor="#334155", lw=1.8, zorder=6))
    ax.add_patch(Circle((mq_x + 1.98, mq_y + mq_h / 2), 0.54, facecolor="#cbd5e1", edgecolor="#475569", lw=1.2, zorder=7))
    ax.text(mq_x + 1.98, mq_y + mq_h / 2, "MQ-137", fontsize=8.5, fontweight="bold", color="#0f172a", ha="center", va="center", zorder=8)
    ax.text(mq_x + mq_w / 2, mq_y + mq_h + 0.2, "Sensor MQ-137 (Placa Verde)", fontsize=10, fontweight="bold",
            color="#14532d", ha="center", va="bottom")

    mq_pins_y = [mq_y + 2.08, mq_y + 1.54, mq_y + 1.00, mq_y + 0.46]
    mq_labels = ["VCC", "AOUT (1º OUT)", "DOUT (2º OUT)", "GND"]
    mq_px = mq_x + 0.24
    for py, lbl in zip(mq_pins_y, mq_labels):
        ax.add_patch(Circle((mq_px, py), 0.10, facecolor="#fde047" if "DOUT" not in lbl else "#94a3b8",
                            edgecolor="#0f172a", lw=1.1, zorder=7))
        ax.text(mq_px + 0.18, py, lbl, fontsize=7.6, fontweight="bold",
                color="#ffffff" if "DOUT" not in lbl else "#bbf7d0", ha="left", va="center", zorder=7)

    ax.text(mq_px - 0.26, mq_pins_y[2], "X", fontsize=11, fontweight="bold", color="#dc2626", ha="center", va="center", zorder=20)

    # =========================================================================
    # 7. RESISTORES DO DIVISOR DE TENSÃO NA PROTOBOARD
    # =========================================================================
    r1_p1 = (cols_x[idx_aout], rows_bot_y[2])  # c35
    r1_p2 = (cols_x[idx_junc], rows_bot_y[2])  # c42 (JUNÇÃO!)
    draw_resistor_h(ax, r1_p1[0], r1_p2[0], r1_p1[1], label="R1 = 10kΩ")
    badge(ax, (r1_p1[0] + r1_p2[0]) / 2, r1_p1[1] - 0.38, 8, bg="#b45309")

    r2_p1 = (cols_x[idx_junc], rows_bot_y[0])  # a42 (mesma coluna!)
    r2_p2 = (cols_x[idx_junc], bot_gnd_y)      # trilha azul GND (-)
    draw_resistor_v(ax, r2_p1[0], r2_p1[1], r2_p2[1], label="R2 = 10kΩ")
    badge(ax, r2_p1[0] - 0.38, (r2_p1[1] + r2_p2[1]) / 2, 9, bg="#1e293b")

    # =========================================================================
    # 8. FIOS NUMERADOS (1 a 11)
    # =========================================================================
    # #1 Bateria (+) -> LM2596 IN+
    wire(ax, [bat_plus, (bat_plus[0], 12.45), (lm_in_plus[0], 12.45), lm_in_plus], color="#ef4444")
    badge(ax, 2.85, 12.45, 1, bg="#dc2626")

    # #2 Bateria (-) -> LM2596 IN-
    wire(ax, [bat_minus, (bat_minus[0], 12.12), (3.45, 12.12), (3.45, lm_in_minus[1]), lm_in_minus], color="#1f2937")
    badge(ax, 3.45, 10.75, 2, bg="#111827")

    # #3 LM2596 OUT+ -> Trilha 5V (+) superior da protoboard
    p_5v_in = (cols_x[2], top_plus_y)
    wire(ax, [lm_out_plus, (7.85, lm_out_plus[1]), (7.85, top_plus_y), p_5v_in], color="#ef4444")
    badge(ax, 7.85, 11.40, 3, bg="#dc2626")

    # #4 LM2596 OUT- -> Trilha GND (-) inferior da protoboard
    p_gnd_lm = (cols_x[0], bot_gnd_y)
    wire(ax, [lm_out_minus, (7.75, lm_out_minus[1]), (7.75, bot_gnd_y), p_gnd_lm], color="#1f2937")
    badge(ax, 7.75, 6.20, 4, bg="#111827")

    # Ponte tracejada opcional entre GND superior e GND inferior
    wire(ax, [(cols_x[26], top_gnd_y), (pb_x + pb_w - 0.20, top_gnd_y),
              (pb_x + pb_w - 0.20, bot_gnd_y), (cols_x[26], bot_gnd_y)], color="#1f2937", lw=2.4, dashed=True)

    # #5 Trilha 5V (+) -> MQ-137 VCC
    p_5v_out = (cols_x[24], top_plus_y)
    wire(ax, [p_5v_out, (cols_x[24], 12.35), (18.02, 12.35), (18.02, mq_pins_y[0]), (mq_px, mq_pins_y[0])], color="#ef4444")
    badge(ax, 17.0, 12.35, 5, bg="#dc2626")

    # #6 MQ-137 GND -> Trilha GND (-) inferior
    p_gnd_mq = (cols_x[25], bot_gnd_y)
    wire(ax, [(mq_px, mq_pins_y[3]), (18.02, mq_pins_y[3]), (18.02, bot_gnd_y), p_gnd_mq], color="#1f2937")
    badge(ax, 18.02, 5.75, 6, bg="#111827")

    # #7 MQ-137 AOUT -> Coluna de entrada do R1 (furo e da coluna idx_aout)
    p_aout_hole = (cols_x[idx_aout], rows_bot_y[4])  # e35
    wire(ax, [(mq_px, mq_pins_y[1]), (17.85, mq_pins_y[1]), (17.85, 7.75),
              (p_aout_hole[0], 7.75), p_aout_hole], color="#f97316")
    badge(ax, 16.85, 7.75, 7, bg="#ea580c")

    # #10 Ponto do meio (furo e da coluna idx_junc) -> sobe acima do ESP32 (y=10.55) -> pino D34
    p_junc_hole = (cols_x[idx_junc], rows_bot_y[4])  # e42
    y_route_d34 = 10.52  # entre o topo do ESP32 e a trilha azul superior!
    wire(ax, [p_junc_hole, (p_junc_hole[0], y_route_d34), (esp_d34_pt[0], y_route_d34), esp_d34_pt],
         color="#facc15", lw=4.0, z=20)
    badge(ax, (p_junc_hole[0] + esp_d34_pt[0]) / 2, y_route_d34, 10, bg="#ca8a04", z=32)
    ax.text(p_junc_hole[0] + 0.18, 9.35, "Junção (~2,5V máx)\nvai para D34",
            fontsize=8.3, fontweight="bold", color="#854d0e", ha="left", va="center", zorder=26,
            bbox=dict(boxstyle="round,pad=0.2", fc="#fef9c3", ec="#eab308", lw=1.0))

    # #11 ESP32 GND (furo 'a' livre na coluna do GND inferior) -> Trilha GND (-)
    p_gnd_esp_rail = (esp_gnd_hole[0], bot_gnd_y)
    wire(ax, [esp_gnd_hole, p_gnd_esp_rail], color="#1f2937")
    badge(ax, esp_gnd_hole[0] - 0.36, (esp_gnd_hole[1] + bot_gnd_y) / 2, 11, bg="#111827")

    # =========================================================================
    # 9. LEGENDA RESUMIDA + DETALHE DO DIVISOR (RODAPÉ)
    # =========================================================================
    rbox(ax, 0.75, 0.42, 12.65, 3.62, r=0.16, fc="#ffffff", ec="#cbd5e1", lw=1.6, z=2)
    ax.text(1.05, 3.72, "Guia Rápido das Ligações (mesma numeração da tabela):",
            fontsize=10.5, fontweight="bold", color="#0f172a", ha="left", va="center")

    items_left = [
        ("1", "#dc2626", "Bateria 9V (+)  →  LM2596 IN+"),
        ("2", "#111827", "Bateria 9V (−)  →  LM2596 IN−"),
        ("3", "#dc2626", "LM2596 OUT+ (5V)  →  Trilha + (5V) da protoboard"),
        ("4", "#111827", "LM2596 OUT−  →  Trilha − (GND) da protoboard"),
        ("5", "#dc2626", "Trilha + (5V)  →  MQ-137 VCC (1º pino)"),
        ("6", "#111827", "MQ-137 GND (4º pino)  →  Trilha − (GND)"),
    ]
    items_right = [
        ("7", "#ea580c", "MQ-137 AOUT (2º pino)  →  Coluna do R1 (perna 1)"),
        ("8", "#b45309", "R1 (10kΩ) liga a coluna do AOUT até a Coluna do Meio"),
        ("9", "#1e293b", "R2 (10kΩ) sai da MESMA Coluna do Meio  →  Trilha − (GND)"),
        ("10", "#ca8a04", "Fio Amarelo sai da MESMA Coluna do Meio  →  ESP32 D34"),
        ("11", "#111827", "ESP32 GND (furo 'a' livre)  →  Trilha − (GND)"),
        ("12", "#334155", "Cabo USB-C do ESP32  →  Notebook ou Powerbank"),
    ]

    for k, (num, col, txt) in enumerate(items_left):
        yy = 3.22 - k * 0.44
        badge(ax, 1.18, yy, num, bg=col, r=0.16)
        ax.text(1.48, yy, txt, fontsize=8.8, color="#1e293b", ha="left", va="center")

    for k, (num, col, txt) in enumerate(items_right):
        yy = 3.22 - k * 0.44
        badge(ax, 6.95, yy, num, bg=col, r=0.16)
        ax.text(7.25, yy, txt, fontsize=8.8, color="#1e293b", ha="left", va="center")

    rbox(ax, 13.75, 0.42, 7.50, 3.62, r=0.16, fc="#fffbeb", ec="#f59e0b", lw=1.6, z=2)
    ax.text(14.05, 3.72, "3 Detalhes Críticos na Montagem:", fontsize=10.5, fontweight="bold", color="#92400e", ha="left", va="center")
    tips = [
        "1. Coluna do Meio (destacada em amarelo): Os 5 furos verticais (a, b, c, d, e) da mesma\n"
        "    coluna são interligados! Encaixe ali: Perna 2 do R1 (c) + Perna 1 do R2 (a) + Fio Amarelo (e).",
        "2. Pino D34 coberto pelo ESP32: Como a borda de cima do ESP32 cobre os furos f–j, enrole\n"
        "    um pequeno laço com a ponta do fio amarelo (#10) direto no pino D34 antes de apertar.",
        "3. GND Comum: Todos os terras (#4, #6, #9 e #11) chegam na MESMA trilha azul (−) de baixo.\n"
        "    O 3º pino do sensor (DOUT, marcado com X vermelho) fica solto, sem fio."
    ]
    for idx_t, t_str in enumerate(tips):
        ax.text(14.05, 3.05 - idx_t * 0.92, t_str, fontsize=8.4, color="#451a03", ha="left", va="center", linespacing=1.35)

    plt.tight_layout(pad=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Salvo em: {out_path}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "esquema_divisor_tensao.png"
    main(target)
