import os
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def extract_indicator_series(fpath, geo_code="38038", measure_code="ABSOLUTE"):
    """Extract time-series dictionary {year: value} for a given municipality code."""
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    dim = data["dimension"]
    geo_idx = dim["GEOGRAPHICAL"]["representation"]["index"][geo_code]
    meas_idx = dim["MEASURE"]["representation"]["index"][measure_code]
    
    n_time = dim["TIME"]["representation"]["size"]
    n_meas = dim["MEASURE"]["representation"]["size"]
    time_index = dim["TIME"]["representation"]["index"]
    obs = data["observation"]
    
    series = {}
    for time_str, t_idx in time_index.items():
        flat_idx = geo_idx * (n_time * n_meas) + t_idx * n_meas + meas_idx
        if flat_idx < len(obs):
            val = obs[flat_idx]
            if val is not None and val != ".":
                try:
                    series[int(time_str)] = float(val)
                except ValueError:
                    pass
    return series

def generate_2panel_plots(start_year=2011, base_year=2013):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "ISTAC"))
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Load data
    pop_raw = extract_indicator_series(os.path.join(data_dir, "population_all.json"))
    tur_raw = extract_indicator_series(os.path.join(data_dir, "alojatur_poblacion_tur_etc.json"))
    
    
    # Base values for 2013
    pop_base = pop_raw.get(base_year)
    tur_base = tur_raw.get(base_year)
    
    
    if not (pop_base and tur_base):
        raise ValueError(f"Missing base year {base_year} in one or more datasets.")
        
    # Filter series
    years_pop = sorted([y for y in pop_raw if y >= start_year])
    years_tur = sorted([y for y in tur_raw if y >= start_year])
    
    
    vals_pop = [ pop_raw[y] for y in years_pop ]
    vals_tur = [ tur_raw[y] for y in years_tur ]
    
    pop_norm = [ (pop_raw[y] / pop_base) * 100 for y in years_pop ]
    tur_norm = [ (tur_raw[y] / tur_base) * 100 for y in years_tur ]
    
    
    # Styling configuration
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    
    color_res = "#1f4e79"  # Slate Navy (Resident)
    color_tur = "#d9534f"  # Coral Amber (Tourist)
    
    
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.8, 7), sharex=True,
        gridspec_kw={"height_ratios": [1.1, 1.0]}
    )
    fig.patch.set_facecolor("#ffffff")
    
    # -------------------------------------------------------------------------
    # PANEL 1 (TOP): Dinámica Demográfica y Presión Turística (Valores Absolutos)
    # Double Y-Axis: Left = Resident (200k-225k), Right = Tourist (0-2k)
    # -------------------------------------------------------------------------
    line1 = ax1.plot(years_pop, vals_pop, color=color_res, linewidth=2.3, marker="o", markersize=4.5,
                     label="Población Residente (Padrón municipal)")
    ax1.set_ylabel("Población Residente\n(Habitantes)", fontsize=9.5, fontweight="bold", color=color_res, labelpad=8)
    ax1.tick_params(axis="y", labelcolor=color_res)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,} hab.".replace(",", ".")))
    ax1.set_ylim(198000, 226000)
    ax1.grid(True, linestyle="--", alpha=0.35, zorder=0)
    
    # Secondary Y-axis for Tourist Population
    ax1_twin = ax1.twinx()
    line2 = ax1_twin.plot(years_tur, vals_tur, color=color_tur, linewidth=2.3, marker="s", markersize=4.5,
                          linestyle="--", label="Población Turística equivalente (Alojatur)")
    ax1_twin.set_ylabel("Población Turística eq.\n(Habitantes)", fontsize=9.5, fontweight="bold", color=color_tur, labelpad=8)
    ax1_twin.tick_params(axis="y", labelcolor=color_tur)
    ax1_twin.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,} hab.".replace(",", ".")))
    ax1_twin.set_ylim(0, 2100)
    ax1_twin.spines["right"].set_color(color_tur)
    ax1_twin.spines["left"].set_color(color_res)
    
    # Combined legend for Panel 1
    lines_p1 = line1 + line2
    labels_p1 = [l.get_label() for l in lines_p1]
    ax1.legend(lines_p1, labels_p1, loc="lower left", frameon=True, framealpha=0.9, fontsize=8.8)
    
    # Annotate 2011-2012 adjustment
    diff_2012 = int(pop_raw[2012] - pop_raw[2011])
    ax1.annotate(f"Ajuste censal INE 2012\n({diff_2012:,} hab. depurados)".replace(",", "."),
                 xy=(2011.6, (pop_raw[2011] + pop_raw[2012]) / 2),
                 xytext=(2012.4, 218500),
                 arrowprops=dict(arrowstyle="->", color="#444444", lw=1.0),
                 fontsize=8.5, color="#333333", backgroundcolor="#ffffff")
    
    ax1.set_title("Dinámica Demográfica y Presión Turística en Valores Absolutos",
                  fontsize=10.5, fontweight="bold", pad=8, color="#1f4e79")
    
    # -------------------------------------------------------------------------
    # PANEL 2 (MIDDLE): Crecimiento Relativo Normalizado (Base 100 = 2013)
    # -------------------------------------------------------------------------
    ax2.axhline(100, color="#888888", linestyle=":", linewidth=1.2, zorder=1)
    
    ax2.plot(years_pop, pop_norm, color=color_res, linewidth=2.3, marker="o", markersize=4.5,
             label=f"Población Residente (Base 2013 = {int(pop_base):,} hab.)".replace(",", "."))
    ax2.plot(years_tur, tur_norm, color=color_tur, linewidth=2.3, marker="s", markersize=4.5, linestyle="--",
             label=f"Población Turística eq. (Base 2013 = {int(tur_base):,} hab.)".replace(",", "."))
    
    # Annotate end points
    ax2.annotate(f"{pop_norm[-1]:.1f} (+{pop_norm[-1]-100:.1f}%)",
                 xy=(years_pop[-1], pop_norm[-1]), xytext=(7, -2),
                 textcoords="offset points", color=color_res, fontweight="bold", fontsize=8.8)
    
    ax2.annotate(f"{tur_norm[-1]:.1f} (+{tur_norm[-1]-100:.1f}%)",
                 xy=(years_tur[-1], tur_norm[-1]), xytext=(7, -2),
                 textcoords="offset points", color=color_tur, fontweight="bold", fontsize=8.8)
    
    ax2.set_ylabel("Índice de Población\n(Base 100 = 2013)", fontsize=9.5, fontweight="bold", color="#333333", labelpad=8)
    ax2.set_title("Evolución Relativa Normalizada de la Presión Territorial (Base 100 = 2013)",
                  fontsize=10.5, fontweight="bold", pad=8, color="#333333")
    ax2.grid(True, linestyle="--", alpha=0.35, zorder=0)
    ax2.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=8.8)
    ax2.set_ylim(75, 165)
    
    
    
    # Adjust margins to leave ample room for two-line y-labels
    fig.subplots_adjust(left=0.13, right=0.87, top=0.95, bottom=0.06, hspace=0.28)
    
    # Save PDF and SVG
    out_pdf = os.path.join(figures_dir, "demographics_trend.pdf")
    out_svg = os.path.join(figures_dir, "demographics_trend.svg")
    
    plt.savefig(out_pdf, format="pdf")
    plt.savefig(out_svg, format="svg")
    plt.close()
    
    print(f"[OK] Generated 2-panel figure PDF: {out_pdf}")
    print(f"[OK] Generated 2-panel figure SVG: {out_svg}")

if __name__ == "__main__":
    generate_2panel_plots(start_year=2011, base_year=2013)
