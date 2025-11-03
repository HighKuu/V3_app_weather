import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import locale
import streamlit as st

API_KEY = st.secrets["API_KEY"]

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except:
        pass

#CSS
st.set_page_config(
    page_title="Météo App - Halim",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.title('''Météo en Temps Réel 🌤
''')

import requests

# Titre de l'application
st.header(":blue[La météo détaillée pour s'habiller convenablement]")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Formulaire pour entrer la ville
city = st.text_input("Entrez le nom de la ville :")

if city:
    # Appel à l'API météo
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Pour obtenir la température en Celsius
        "lang": "fr",  # Pour les descriptions en français
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        # Extraction des données météo
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        # Récupération des coordonnées géo
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        # Affichage des données
        st.subheader(f"Météo en direct à {city.capitalize()}")
        st.write(f"🌡️ Température : {temperature}°C")
        st.write(f"🌤️ Description : {description}")
        st.write(f"💧 Humidité : {humidity}%")
        st.write(f"🌬️ Vent : {wind_speed} m/s")
        # ICI code à revoir pour sh'abiller en fonction de la météo
        if 0. < temperature < 10.:
            st.write(f"Sors la doudoune, si tu ne veux pas mourrir d'hypothermie ! ☃️")
        elif 10 < temperature < 15:
            st.write(f"Prends de quoi te couvrir ! ⛅️⛅️")
        elif 15 < temperature < 25:
            st.write(f"Il fait bon mais fais attention 🌤️🌤️️")
        else:
            st.write(f"Sors la crème solaire ! 😎️")
    else:
        # Gestion des erreurs
        st.error("Ville introuvable. Veuillez vérifier l'orthographe.")

st.header("Prévisions à venir")

if city:
    BASE_URL_FORECAST = 'http://api.openweathermap.org/data/2.5/forecast'

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "fr",
    }
    response = requests.get(BASE_URL_FORECAST, params=params)
    data = response.json()

    if response.status_code == 200:
        # Liste pour stocker TOUTES les prévisions
        toutes_les_previsions = []

        for prevision in data["list"][:32]:
            dt = datetime.strptime(prevision["dt_txt"], "%Y-%m-%d %H:%M:%S")

            # Créer un dictionnaire pour CETTE prévision
            une_prevision = {
                "Jour": dt.strftime("%a %d"),
                "Heure": dt.strftime("%H:%M"),
                "Température": prevision["main"]["temp"],
                "Précipitation": prevision.get("rain", {}).get("3h", 0),
                "Humidité": prevision["main"]["humidity"],
                "Pression": prevision["main"]["pressure"],
                "Vent": prevision["wind"]["speed"],
                "Description": prevision["weather"][0]["description"]
            }

            # Ajouter cette prévision à la liste
            toutes_les_previsions.append(une_prevision)


        df = pd.DataFrame(toutes_les_previsions)

        # Préparer le DataFrame pour l'affichage avec couleurs
        df_display = df[["Jour", "Heure", "Température", "Précipitation", "Humidité", "Description"]].copy()


        # Fonction pour colorer les températures
        def style_rows(row):
            """Applique le style à chaque ligne"""
            styles = [''] * len(row)

            # Colorer la température selon la valeur
            temp_str = str(row['Température'])
            if '°C' in temp_str:
                try:
                    temp = float(temp_str.replace('°C', ''))
                    if temp < 0:
                        styles[2] = 'background-color: #1E88E5; color: white; font-weight: bold'
                    elif temp < 10:
                        styles[2] = 'background-color: #42A5F5; color: white; font-weight: bold'
                    elif temp < 15:
                        styles[2] = 'background-color: #42A5F5; color: white; font-weight: bold'
                    elif temp < 20:
                        styles[2] = 'background-color: #9CCC65; color: black; font-weight: bold'
                    elif temp < 25:
                        styles[2] = 'background-color: #FFEE58; color: black; font-weight: bold'
                    elif temp < 30:
                        styles[2] = 'background-color: #FFA726; color: black; font-weight: bold'
                    else:
                        styles[2] = 'background-color: #EF5350; color: white; font-weight: bold'
                except:
                    pass

            # Ajouter une bordure en haut si c'est un nouveau jour
            row_index = row.name
            if row_index > 0:
                jour_actuel = row['Jour']
                jour_precedent = df_display.iloc[row_index - 1]['Jour']
                if jour_actuel != jour_precedent:
                    # Bordure bleue épaisse au changement de jour
                    styles = [s + '; border-top: 3px solid #4FC3F7' for s in styles]

            return styles


        # Formater les valeurs
        df_display["Température"] = df_display["Température"].apply(lambda x: f"{x}°C")
        df_display["Précipitation"] = df_display["Précipitation"].apply(lambda x: f"{x} mm" if x > 0 else "--")
        df_display["Humidité"] = df_display["Humidité"].apply(lambda x: f"{x}%")

        # Appliquer le style
        styled_df = df_display.style.apply(style_rows, axis=1)

        # Créer les colonnes
        col1, col2 = st.columns(2)

        # Afficher dans chaque colonne
        with col1:
            st.subheader("📋 Tableau des prévisions")
            st.dataframe(
                styled_df,
                hide_index=True,
                use_container_width=True,
                height=1000
            )

        with col2:
            st.subheader("📈 Graphiques")

            # Configuration du style sombre pour matplotlib
            plt.style.use('dark_background')

            # Graphique 1 : Températures
            fig1, ax1 = plt.subplots(figsize=(8, 4), facecolor='#1A2332')
            ax1.set_facecolor('#1A2332')
            ax1.plot(df.index, df["Température"], marker='o', linewidth=2.5, markersize=5,
                     color='#4FC3F7', markerfacecolor='#29B6F6')
            ax1.set_xlabel("Prévisions (toutes les 3h)", color='#B0BEC5', fontsize=11)
            ax1.set_ylabel("Température (°C)", color='#B0BEC5', fontsize=11)
            ax1.set_title("Évolution des températures", color='#E8F4F8', fontsize=13, fontweight='bold')
            ax1.grid(True, alpha=0.2, color='#4FC3F7')
            ax1.tick_params(colors='#B0BEC5')
            plt.tight_layout()
            st.pyplot(fig1)

            # Graphique 2 : Pression
            fig2, ax2 = plt.subplots(figsize=(8, 4), facecolor='#1A2332')
            ax2.set_facecolor('#1A2332')
            ax2.plot(df.index, df["Pression"], marker='o', linewidth=2.5, markersize=5,
                     color='#81C784', markerfacecolor='#66BB6A')
            ax2.set_xlabel("Prévisions (toutes les 3h)", color='#B0BEC5', fontsize=11)
            ax2.set_ylabel("Pression (hPa)", color='#B0BEC5', fontsize=11)
            ax2.set_title("Évolution de la pression", color='#E8F4F8', fontsize=13, fontweight='bold')
            ax2.grid(True, alpha=0.2, color='#81C784')
            ax2.tick_params(colors='#B0BEC5')
            plt.tight_layout()
            st.pyplot(fig2)

            # Graphique 3 : Précipitations
            fig3, ax3 = plt.subplots(figsize=(8, 4), facecolor='#1A2332')
            ax3.set_facecolor('#1A2332')
            ax3.bar(df.index, df["Précipitation"], color='#64B5F6', edgecolor='#42A5F5', linewidth=1.5)
            ax3.set_xlabel("Prévisions (toutes les 3h)", color='#B0BEC5', fontsize=11)
            ax3.set_ylabel("Précipitations (mm)", color='#B0BEC5', fontsize=11)
            ax3.set_title("Précipitations sur 3h", color='#E8F4F8', fontsize=13, fontweight='bold')
            ax3.grid(True, alpha=0.2, axis='y', color='#64B5F6')
            ax3.tick_params(colors='#B0BEC5')
            plt.tight_layout()
            st.pyplot(fig3)

        # === SECTION ANALYSES ===
        st.header("📊 Analyses détaillées")

        # Calculer les statistiques globales
        temp_moyenne = df["Température"].mean()
        temp_min = df["Température"].min()
        temp_max = df["Température"].max()
        pluie_totale = df["Précipitation"].sum()
        humidite_moyenne = df["Humidité"].mean()

        # Afficher les stats en colonnes
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric("🌡️ Température moyenne", f"{temp_moyenne:.1f}°C")

        with col_stat2:
            st.metric("📉 Min / Max", f"{temp_min:.1f}°C / {temp_max:.1f}°C")

        with col_stat3:
            st.metric("🌧️ Pluie totale", f"{pluie_totale:.1f} mm")

        with col_stat4:
            st.metric("💧 Humidité moyenne", f"{humidite_moyenne:.0f}%")

        # Analyse intelligente
        st.subheader("🤖 Analyse automatique")

        # Déterminer s'il va pleuvoir
        jours_avec_pluie = df[df["Précipitation"] > 0]["Jour"].unique()

        if pluie_totale > 10:
            st.warning(
                f"⚠️ **Attention !** Il devrait pleuvoir pas mal sur les prochains jours (total : {pluie_totale:.1f} mm). Prévois un parapluie ! ☔")
        elif pluie_totale > 0:
            st.info(f"🌦️ Quelques averses attendues ({pluie_totale:.1f} mm au total), mais rien de méchant.")
        else:
            st.success("☀️ Pas de pluie prévue ! Parfait pour des activités en extérieur.")

        # Analyse des températures
        if temp_moyenne < 10:
            st.info("🧥 **Il va faire froid !** Pense à bien te couvrir, température moyenne de {:.1f}°C.".format(
                temp_moyenne))
        elif temp_moyenne < 15:
            st.info("🧥 **Temps frais.** Une veste sera nécessaire, température moyenne de {:.1f}°C.".format(
                temp_moyenne))
        elif temp_moyenne < 25:
            st.success("😊 **Températures agréables !** Autour de {:.1f}°C en moyenne.".format(temp_moyenne))
        else:
            st.success("☀️ **Il va faire chaud !** Crème solaire recommandée, température moyenne de {:.1f}°C.".format(
                temp_moyenne))



    # modif
    if 'lat' in locals() and 'lon' in locals():
        # Créer la carte centrée sur la ville
        carte = folium.Map(
            location=[lat, lon],
            zoom_start=12,
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google'
        )

        folium.TileLayer(
            tiles=f'http://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}',
            attr='OpenWeatherMap',
            name='Précipitations',
            overlay=True,
            control=True,
            opacity=0.7
        ).add_to(carte)

        folium.LayerControl().add_to(carte)

        folium.Marker(
            [lat, lon],
            popup=f"{city.capitalize()}<br>{temperature}°C<br>{description}",
            tooltip=f"Cliquez pour plus d'infos",
            icon=folium.Icon(color='blue', icon='cloud')
        ).add_to(carte)

        st_folium(carte, width=700, height=500,key="ma_carte_unique")

    else:
        st.error("Impossible de créer la carte : coordonnées manquantes")

    # Créer la carte centrée sur la ville
    carte = folium.Map(
        location=[lat, lon],
        zoom_start=12,
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google'
    )

    folium.TileLayer(
        tiles=f'http://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}',
        attr='OpenWeatherMap',
        name='Précipitations',
        overlay=True,
        control=True,
        opacity=0.7
    ).add_to(carte)

    # Ajouter contrôle des couches
    folium.LayerControl().add_to(carte)

    # Ajouter un marqueur pour la ville
    folium.Marker(
        [lat, lon],
        popup=f"{city.capitalize()}<br>{temperature}°C<br>{description}",
        tooltip=f"Cliquez pour plus d'infos",
        icon=folium.Icon(color='blue', icon='cloud')
    ).add_to(carte)

    # Afficher la carte dans Streamlit
    st_folium(carte, width=700, height=500)

