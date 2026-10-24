import os
import psycopg2
import matplotlib.pyplot as plt

def format_es(num):
    """Format number with dot as thousands separator (Spanish standard)."""
    if num is None:
        return "-"
    return f"{int(round(num)):,}".replace(",", ".")

def generate_report_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tables_dir = os.path.join(base_dir, "tables")
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("Connecting to PostgreSQL database 'fip_pgo'...")
    conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
    cur = conn.cursor()

    # =========================================================================
    # TABLE 1: Summary by Land Classification
    # =========================================================================
    print("Generating Table 1: Land Classification Summary...")
    cur.execute("""
        SELECT 
            COALESCE(subclase_suelo, clase_suelo) AS categoria_suelo,
            COUNT(*) AS total_uas,
            ROUND(SUM(edificabilidad_m2c)::numeric, 0) AS total_edificabilidad_m2c,
            ROUND(SUM(ST_Area(geom))::numeric, 0) AS total_superficie_suelo_m2
        FROM v_unidades_actuacion
        GROUP BY COALESCE(subclase_suelo, clase_suelo)
        ORDER BY total_edificabilidad_m2c DESC NULLS LAST;
    """)
    rows = cur.fetchall()

    tot_uas = sum(r[1] for r in rows)
    tot_edif = sum(r[2] for r in rows if r[2] is not None)
    tot_surf = sum(r[3] for r in rows if r[3] is not None)

    tex_table1 = [
        r"\begin{tabular}{lrrr}",
        r"  \toprule",
        r"  \textbf{Categoría del Suelo} & \textbf{Nº UAs} & \textbf{Edificabilidad ($m^2c$)} & \textbf{Superficie ($m^2$)} \\",
        r"  \midrule"
    ]
    for r in rows:
        cat = r[0]
        uas = format_es(r[1])
        edif = format_es(r[2])
        surf = format_es(r[3])
        tex_table1.append(f"  {cat} & {uas} & {edif} & {surf} \\\\")

    tex_table1.extend([
        r"  \midrule",
        f"  \\textbf{{Total}} & \\textbf{{{format_es(tot_uas)}}} & \\textbf{{{format_es(tot_edif)}}} & \\textbf{{{format_es(tot_surf)}}} \\\\",
        r"  \bottomrule",
        r"\end{tabular}"
    ])

    tbl1_path = os.path.join(tables_dir, "table_land_classes.tex")
    with open(tbl1_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_table1) + "\n")
    print(f" -> Wrote {tbl1_path}")

    # =========================================================================
    # TABLE 2: Summary by Execution System
    # =========================================================================
    print("Generating Table 2: Execution Systems Summary...")
    cur.execute("""
        SELECT 
            COALESCE(sistema_ejecucion, 'No especificado') AS sistema_ejecucion,
            COUNT(*) AS num_uas,
            ROUND(SUM(edificabilidad_m2c)::numeric, 0) AS total_edificabilidad_m2c,
            ROUND((COUNT(*)::numeric / 128.0 * 100), 1) AS pct_uas
        FROM v_unidades_actuacion
        GROUP BY sistema_ejecucion
        ORDER BY num_uas DESC;
    """)
    sys_rows = cur.fetchall()

    tex_table2 = [
        r"\begin{tabular}{p{6.8cm}rrr}",
        r"  \toprule",
        r"  \textbf{Sistema de Ejecución} & \textbf{Nº UAs} & \textbf{\% UAs} & \textbf{Edificabilidad ($m^2c$)} \\",
        r"  \midrule"
    ]
    for sr in sys_rows:
        sys_name = sr[0]
        nu = format_es(sr[1])
        pct = f"{sr[3]:.1f}\\%"
        ed = format_es(sr[2])
        tex_table2.append(f"  {sys_name} & {nu} & {pct} & {ed} \\\\")

    tex_table2.extend([
        r"  \midrule",
        f"  \\textbf{{Total}} & \\textbf{{{format_es(tot_uas)}}} & \\textbf{{100.0\\%}} & \\textbf{{{format_es(tot_edif)}}} \\\\",
        r"  \bottomrule",
        r"\end{tabular}"
    ])

    tbl2_path = os.path.join(tables_dir, "table_execution_systems.tex")
    with open(tbl2_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_table2) + "\n")
    print(f" -> Wrote {tbl2_path}")

    # =========================================================================
    # FIGURE 1: Vector PDF Chart (Matplotlib)
    # =========================================================================
    print("Generating Figure 1: Vector Chart...")
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
    plt.rcParams["font.family"] = "sans-serif"

    fig, ax1 = plt.subplots(figsize=(7.5, 3.2), dpi=300)

    categories = [r[0] for r in rows]
    edif_values = [float(r[2]) / 1e6 for r in rows]  # in Millions of m2c
    uas_counts = [int(r[1]) for r in rows]

    x = range(len(categories))
    width = 0.45

    # Colors: dark slate blue and warm amber
    color_bar = "#1f4e79"
    bars = ax1.bar(x, edif_values, width=width, color=color_bar, alpha=0.9, edgecolor="none", zorder=3)

    ax1.set_ylabel("Edificabilidad (Millones $m^2c$)", color=color_bar, fontsize=10, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_bar)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)

    # Annotate bars with values and number of UAs
    for i, bar in enumerate(bars):
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.04,
            f"{h:.2f} M $m^2c$\n({uas_counts[i]} UAs)",
            ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1f4e79"
        )

    ax1.set_ylim(0, max(edif_values) * 1.25)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#888888")
    ax1.spines["bottom"].set_color("#888888")

    plt.title("Capacidad Edificatoria por Categoría de Suelo (PGO Santa Cruz de Tenerife)", fontsize=11, fontweight="bold", pad=14)
    plt.tight_layout()

    fig_path = os.path.join(figures_dir, "chart_land_classes.pdf")
    plt.savefig(fig_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f" -> Wrote {fig_path}")

    cur.close()
    conn.close()
    print("[SUCCESS] All report tables and figures generated successfully!")

if __name__ == "__main__":
    generate_report_data()
