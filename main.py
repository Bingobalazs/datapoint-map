import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

def koordinata_atalakito(koord_str):
    """Átalakítja a '47:02.06' formátumot tizedes törtté."""
    try:
        parts = str(koord_str).split(':')
        fok = float(parts[0])
        perc = float(parts[1])
        return fok + (perc / 60)
    except:
        return None

def letrehoz_terkepeket(adat_fajl, koord_fajl):
    if not os.path.exists(adat_fajl) or not os.path.exists(koord_fajl):
        print(f"Hiba: A fájlok nem találhatók!")
        return

    # 1. Adatok beolvasása
    df_iskolak = pd.read_csv(adat_fajl, quotechar='"')
    df_koordinatak = pd.read_csv(koord_fajl)

    # 2. Koordináták feldolgozása
    koordinata_map = {}
    for _, row in df_koordinatak.iterrows():
        lat_val = koordinata_atalakito(row['Lon']) 
        lon_val = koordinata_atalakito(row['Lat'])
        koordinata_map[str(row['Város']).strip()] = [lat_val, lon_val]

    # 3. Térképek beállításai
    terkep_modok = [
        {'id': '2024', 'fajlnev': 'terkep_2024.html', 'adat_oszlop': '2024_adat', 'cim': '2024-es adatok', 'szin': '#3498db'}, # Kék
        {'id': '2025', 'fajlnev': 'terkep_2025.html', 'adat_oszlop': '2025_adat', 'cim': '2025-ös adatok', 'szin': '#8e44ad'}, # Lila
        {'id': 'valtozas', 'fajlnev': 'terkep_valtozas.html', 'adat_oszlop': 'változás', 'cim': 'Változás (2024 -> 2025)', 'szin': '#f39c12'} # Narancs (de dinamikus lesz)
    ]

    for mod in terkep_modok:
        print(f"{mod['cim']} generálása...")
        terkep = folium.Map(location=[47.1625, 19.5033], zoom_start=7, tiles='CartoDB positron')
        # 4. Egyedi JavaScript a MarkerCluster számára (összeadja az adatokat a darabszám helyett)
        cluster_js = f"""
            function(cluster) {{
                var markers = cluster.getAllChildMarkers();
                var sum = 0;
                // Összeadjuk a markerekben elrejtett 'data-value' értékeket
                for (var i = 0; i < markers.length; i++) {{
                    var htmlStr = markers[i].options.icon.options.html;
                    var match = htmlStr.match(/data-value="(-?\\d+)"/);
                    if (match) {{ sum += parseInt(match[1]); }}
                }}
                
                // Színkódolás
                var bgColor = '{mod['szin']}';
                if ('{mod['id']}' === 'valtozas') {{
                    if (sum > 0) bgColor = '#27ae60';      // Zöld ha pozitív
                    else if (sum < 0) bgColor = '#e74c3c'; // Piros ha negatív
                    else bgColor = '#95a5a6';              // Szürke ha nincs változás
                }}
                
                var displaySum = (sum > 0 && '{mod['id']}' === 'valtozas') ? '+' + sum : sum;

                return L.divIcon({{
                    html: '<div style="background-color: ' + bgColor + '; color: white; border-radius: 50%; width: 45px; height: 45px; display: flex; justify-content: center; align-items: center; font-weight: bold; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.6); font-size: 15px;">' + displaySum + '</div>',
                    className: '',
                    iconSize: L.point(45, 45)
                }});
            }}
        """

        marker_cluster = MarkerCluster(
            name=mod['cim'],
            icon_create_function=cluster_js # A fenti JavaScript befecskendezése
        ).add_to(terkep)

        # 5. Adatok feldolgozása városonként
        for varos, group in df_iskolak.groupby('Város'):
            v_nev = str(varos).strip()
            if v_nev not in koordinata_map: continue
            coords = koordinata_map[v_nev]
            
            # Kerekített egész szám
            fokusz_osszesen = int(group[mod['adat_oszlop']].sum())
            
            # Dinamikus színezés és előjel a városi ikonhoz is
            bg_color = mod['szin']
            kijelzett_szam = str(fokusz_osszesen)

            if mod['id'] == 'valtozas':
                if fokusz_osszesen > 0: 
                    bg_color = '#27ae60'
                    kijelzett_szam = f"+{fokusz_osszesen}"
                elif fokusz_osszesen < 0: 
                    bg_color = '#e74c3c'
                else: 
                    bg_color = '#95a5a6'

            # --- EGYEDI VÁROSI IKON HTML ALAPON ---
            # Ide mentjük el a "data-value" attribútumba a számot, amit a fenti JS ki fog olvasni
            icon_html = f"""
            <div data-value="{fokusz_osszesen}" style="background-color: {bg_color}; color: white; border-radius: 50%; width: 35px; height: 35px; display: flex; justify-content: center; align-items: center; font-weight: bold; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.5); font-size: 13px;">
                {kijelzett_szam}
            </div>
            """

            # --- POPUP TÁBLÁZAT LÉTREHOZÁSA (ugyanaz marad) ---
            html = f"""
            <div style="font-family: Arial; min-width: 320px;">
                <h3 style="margin-bottom: 5px; color: #333;">{v_nev}</h3>
                <div style="background: #f4f4f4; padding: 5px; margin-bottom: 10px; border-radius: 4px;">
                    <b>{mod['cim']} összesen:</b> <span style="color: {bg_color}; font-size: 16px; font-weight: bold;">{kijelzett_szam}</span>
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <tr style="background: #e9ecef;">
                        <th style="padding: 4px; border: 1px solid #ccc; text-align: left;">Iskola</th>
                        <th style="padding: 4px; border: 1px solid #ccc;">'24</th>
                        <th style="padding: 4px; border: 1px solid #ccc;">'25</th>
                        <th style="padding: 4px; border: 1px solid #ccc;">Vált.</th>
                        <th style="padding: 4px; border: 1px solid #ccc;">Státusz</th>
                    </tr>
            """
            for _, row in group.iterrows():
                stat_szin = "black"
                if "nincs" in str(row['Státusz']): stat_szin = "#d9534f"
                elif "új" in str(row['Státusz']): stat_szin = "#5cb85c"
                html += f"""
                    <tr>
                        <td style="padding: 4px; border: 1px solid #ccc;">{row['Iskola']}</td>
                        <td style="padding: 4px; border: 1px solid #ccc; text-align: center;">{row['2024_adat']}</td>
                        <td style="padding: 4px; border: 1px solid #ccc; text-align: center;">{row['2025_adat']}</td>
                        <td style="padding: 4px; border: 1px solid #ccc; text-align: center; font-weight: bold;">{row['változás']}</td>
                        <td style="padding: 4px; border: 1px solid #ccc; color: {stat_szin}; font-weight: bold;">{row['Státusz']}</td>
                    </tr>
                """
            html += "</table></div>"
            
            # Marker hozzáadása a térképhez az egyedi HTML ikonnal
            folium.Marker(
                location=coords,
                popup=folium.Popup(html, max_width=450),
                tooltip=f"{v_nev}: {kijelzett_szam}",
                icon=folium.DivIcon(html=icon_html, icon_anchor=(17, 17)) # DivIcon használata
            ).add_to(marker_cluster)

        terkep.save(mod['fajlnev'])
        print(f"  -> Sikeresen elmentve: {mod['fajlnev']}")

if __name__ == "__main__":
    letrehoz_terkepeket('iskola_adatok.csv', 'koordinatak.csv')
    print("\nMinden térkép elkészült!")