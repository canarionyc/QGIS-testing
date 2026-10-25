import os
import json
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_migration_plot():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Fetch municipal data from INE & ISTAC
    # ISTAC Municipal Saldo Migratorio 2002-2021
    istac_url = 'https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicatorsSystems/C00067A/indicatorsInstances/c8747bfa-2967-499b-81fb-9b58557f1322/data'
    req = urllib.request.Request(istac_url, headers={'User-Agent': 'Mozilla/5.0'})
    saldo_mun = {}
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            dim = data['dimension']
            geo_idx = dim['GEOGRAPHICAL']['representation']['index'].get('38038')
            time_idx = dim['TIME']['representation']['index']
            n_time = dim['TIME']['representation']['size']
            n_meas = dim['MEASURE']['representation']['size']
            meas_idx = dim['MEASURE']['representation']['index'].get('ABSOLUTE', 0)
            obs = data['observation']
            for year_str, t_idx in time_idx.items():
                flat = geo_idx * (n_time * n_meas) + t_idx * n_meas + meas_idx
                if flat < len(obs) and obs[flat] is not None and obs[flat] != '.':
                    saldo_mun[int(year_str)] = float(obs[flat])
    except Exception as e:
        print("Error fetching ISTAC:", e)
        
    # INE Municipal recent data (2021-2024) from Operation 455
    # EM1841733: Inmigración exterior Santa Cruz de Tenerife
    # EM1919934: Emigración exterior Santa Cruz de Tenerife
    # EM2399873: Saldo exterior Santa Cruz de Tenerife
    # EM2399872: Saldo total Santa Cruz de Tenerife
    ine_series = {
        'inm_mun': 'EM1841733',
        'emi_mun': 'EM1919934',
        'saldo_ext_mun': 'EM2399873',
        'saldo_tot_mun': 'EM2399872'
    }
    ine_data = {}
    for name, cod in ine_series.items():
        url = f'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{cod}?nult=10'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                d = json.loads(resp.read().decode('utf-8'))
                ine_data[name] = {pt['Anyo']: pt['Valor'] for pt in d.get('Data', [])}
        except Exception as e:
            print(f"Error fetching {name}:", e)
            
    # Also fetch Provincial International Flows (2008-2024) to show the macro-trend
    # Op 71: Inm EM1280417, Emi EM1505659 (2008-2021)
    # Op 455: Inm EM1782437, Emi EM1860638 (2021-2024)
    prov_inm = {}
    prov_emi = {}
    for cod in ['EM1280417', 'EM1782437']:
        url = f'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{cod}?nult=20'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                d = json.loads(resp.read().decode('utf-8'))
                for pt in d.get('Data', []):
                    prov_inm[pt['Anyo']] = pt['Valor']
        except Exception as e:
            print("Error prov inm:", e)
            
    for cod in ['EM1505659', 'EM1860638']:
        url = f'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{cod}?nult=20'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                d = json.loads(resp.read().decode('utf-8'))
                for pt in d.get('Data', []):
                    prov_emi[pt['Anyo']] = pt['Valor']
        except Exception as e:
            print("Error prov emi:", e)

    # Merge municipal saldo: extend with 2022-2024 from INE
    for y in [2022, 2023, 2024]:
        if y in ine_data.get('saldo_tot_mun', {}):
            saldo_mun[y] = ine_data['saldo_tot_mun'][y]
            
    years_saldo = sorted([y for y in saldo_mun.keys() if y >= 2008])
    vals_saldo = [saldo_mun[y] for y in years_saldo]
    
    years_prov = sorted(list(set(prov_inm.keys()).intersection(set(prov_emi.keys()))))
    years_prov = [y for y in years_prov if y >= 2008]
    vals_prov_inm = [prov_inm[y] for y in years_prov]
    vals_prov_emi = [prov_emi[y] for y in years_prov]
    vals_prov_saldo = [prov_inm[y] - prov_emi[y] for y in years_prov]
    
    # -------------------------------------------------------------
    # Plotting: 2-Panel figure
    # Top Panel: Flujos Exteriores (Inmigración vs Emigración)
    # Bottom Panel: Saldo Migratorio Neto (Inversión radical del flujo)
    # -------------------------------------------------------------
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#CCCCCC'
    plt.rcParams['axes.linewidth'] = 0.8
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    
    # Upper Plot: Flujos
    ax1.plot(years_prov, vals_prov_inm, color='#1E88E5', marker='o', linewidth=2.4, markersize=5, label='Inmigración procedente del extranjero (Entradas)')
    ax1.plot(years_prov, vals_prov_emi, color='#D81B60', marker='s', linewidth=2.0, linestyle='--', markersize=5, label='Emigración con destino al extranjero (Salidas)')
    
    ax1.set_title('Dinámica de Flujos Migratorios Exteriores (Santa Cruz de Tenerife, 2008–2024)\nInversión Histórica del Flujo Transatlántico', fontsize=12, fontweight='bold', pad=12)
    ax1.set_ylabel('Personas / año', fontsize=10)
    ax1.set_ylim(0, 38000)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', frameon=True, facecolor='#FAFAFA', edgecolor='#E0E0E0', fontsize=9.5)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
    
    # Annotations Upper
    ax1.annotate('Crisis financiera española:\nCae inmigración y repunta éxodo', 
                 xy=(2012, 11825), xytext=(2009.2, 17500),
                 arrowprops=dict(arrowstyle='->', color='#555555', lw=1),
                 fontsize=8.5, bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFDE7', edgecolor='#FFF59D'))
                 
    ax1.annotate('Inversión y crisis en América Latina:\nFuerte ola de retorno e inmigración', 
                 xy=(2018, 24897), xytext=(2013.2, 27500),
                 arrowprops=dict(arrowstyle='->', color='#1E88E5', lw=1.2),
                 fontsize=8.5, fontweight='bold', color='#0D47A1',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD', edgecolor='#90CAF9'))
                 
    ax1.annotate('Impacto COVID-19', xy=(2020, 13105), xytext=(2019.2, 8500),
                 arrowprops=dict(arrowstyle='->', color='#777777', lw=1),
                 fontsize=8, bbox=dict(boxstyle='round,pad=0.2', facecolor='#EEEEEE', edgecolor='#CCCCCC'))
                 
    # Lower Plot: Saldo Migratorio Neto
    colors = ['#2E7D32' if v >= 0 else '#C62828' for v in vals_saldo]
    bars = ax2.bar(years_saldo, vals_saldo, color=colors, width=0.6, alpha=0.85, edgecolor='#333333', linewidth=0.5, label='Saldo Migratorio Neto Municipal')
    ax2.axhline(0, color='#333333', linewidth=1)
    
    ax2.set_title('Saldo Migratorio Neto Anual en el Municipio de Santa Cruz de Tenerife', fontsize=11, fontweight='bold', pad=8)
    ax2.set_xlabel('Año', fontsize=10)
    ax2.set_ylabel('Saldo Neto (hab.)', fontsize=10)
    ax2.set_ylim(-2600, 3200)
    ax2.grid(True, linestyle=':', alpha=0.6, axis='y')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
    ax2.set_xticks(years_saldo)
    ax2.set_xticklabels(years_saldo, rotation=45, ha='right', fontsize=9)
    
    # Annotate negative vs positive regime
    ax2.annotate('Saldo negativo (2009-2015):\nPérdida de población por crisis', 
                 xy=(2010, -2168), xytext=(2008.2, -1800),
                 arrowprops=dict(arrowstyle='->', color='#C62828', lw=1),
                 fontsize=8, color='#B71C1C',
                 bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFEBEE', edgecolor='#FFCDD2'))
                 
    ax2.annotate('Saldo fuertemente positivo (+2.000 a +2.600 hab./año):\nPresión directa sobre la demanda residencial', 
                 xy=(2018, 2545), xytext=(2014.2, 2500),
                 fontsize=8.5, fontweight='bold', color='#1B5E20',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F5E9', edgecolor='#A5D6A7'))
    
    plt.tight_layout()
    
    pdf_path = os.path.join(figures_dir, "migration_trend.pdf")
    png_path = os.path.join(figures_dir, "migration_trend.png")
    plt.savefig(pdf_path, dpi=300)
    plt.savefig(png_path, dpi=200)
    plt.close()
    print(f"Migration charts successfully saved to {pdf_path} and {png_path}")

if __name__ == '__main__':
    generate_migration_plot()
