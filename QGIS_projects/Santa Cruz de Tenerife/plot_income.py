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

def generate_1panel_plots(start_year=2011, base_year=2013):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "ISTAC"))
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Load data
    ren_raw = extract_indicator_series(os.path.join(data_dir, "renta.json"))
    
    # Base values for 2013
    ren_base = ren_raw.get(base_year)
    
    if not (ren_base):
        raise ValueError(f"Missing base year {base_year} in one or more datasets.")
        
    # Filter series
    years_ren = sorted([y for y in ren_raw if y >= start_year])
    
    
    
    ren_vals = [ ren_raw[y] for y in years_ren ]
    
    # Styling configuration
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    
    color_ren = "#2e7d32"  # Forest Green (Income)
    
    fig, ax1 = plt.subplots(figsize=(9.8, 4.8))
    fig.patch.set_facecolor("#ffffff")
    
    # -------------------------------------------------------------------------
    # PANEL: Evolución de la Renta Media (2013-2021)
    # -------------------------------------------------------------------------
    line1 = ax1.plot(years_ren, ren_vals, color=color_ren, linewidth=2.4, marker="o", markersize=5.5,
                     label="Renta Bruta Media (€ / declarante)")
    
    # Data labels on points
    for y, v in zip(years_ren, ren_vals):
        ax1.annotate(f"{int(round(v)):,} €".replace(",", "."),
                     xy=(y, v), xytext=(0, 8), textcoords="offset points",
                     ha="center", va="bottom", fontsize=8.6, fontweight="semibold", color="#222222")
    
    pct_ren_growth = ((ren_vals[-1] - ren_vals[0]) / ren_vals[0]) * 100
    ax1.text(0.98, 0.90, f"Crecimiento renta (2013-2021): +{pct_ren_growth:.1f}%",
             transform=ax1.transAxes, ha="right", va="top",
             fontsize=9.0, fontweight="bold", color=color_ren,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f5e9", edgecolor="#a5d6a7", alpha=0.9))
    
    ax1.set_ylabel("Renta Bruta Media (€)", fontsize=9.5, fontweight="bold", color="#333333", labelpad=8)
    ax1.tick_params(axis="y", labelsize=8.8)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,} €".replace(",", ".")))
    ax1.set_ylim(24500, 30500)
    ax1.grid(True, linestyle="--", alpha=0.35, zorder=0)

    ax1.set_xticks(years_ren)
    ax1.set_xticklabels([str(y) for y in years_ren], fontsize=9)
    ax1.set_xlabel("Año de Referencia", fontsize=9.5, fontweight="bold", color="#333333")

    ax1.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=8.8)
    
    ax1.set_title("Evolución de la Renta Bruta Media en Santa Cruz de Tenerife (2013–2021)",
                  fontsize=10.5, fontweight="bold", pad=10, color=color_ren)
    
    fig.subplots_adjust(left=0.12, right=0.94, top=0.90, bottom=0.14)
    
    # Save PDF and SVG
    out_pdf = os.path.join(figures_dir, "income_trend.pdf")
    out_svg = os.path.join(figures_dir, "income_trend.svg")
    
    plt.savefig(out_pdf, format="pdf")
    plt.savefig(out_svg, format="svg")
    plt.close()
    
    print(f"[OK] Generated income trend PDF: {out_pdf}")
    print(f"[OK] Generated income trend SVG: {out_svg}")

if __name__ == "__main__":
    generate_1panel_plots(start_year=2011, base_year=2013)
