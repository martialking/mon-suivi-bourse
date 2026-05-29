import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page Streamlit
st.set_page_config(page_title="Tableau de Bord Boursier", layout="wide", page_icon="📈")

st.title("📈 Mon Algorithme de Suivi Boursier Interactive")
st.write("Bienvenue dans votre interface. Les données sont récupérées en direct des marchés financiers.")

# 1. Sélection de la Watchlist par l'utilisateur
watchlist_defaut = ["AAPL", "MSFT", "KO", "JNJ", "V"]
tickers_choisis = st.multiselect(
    "Personnalisez votre liste de surveillance (Ajoutez ou supprimez des actions) :",
    options=["AAPL", "MSFT", "KO", "JNJ", "V", "TSLA", "AMZN", "NFLX", "NVDA"],
    default=watchlist_defaut
)

if tickers_choisis:
    resultats = []
    historiques_actions = {} # Pour stocker les données de chaque action

    # Chargement invisible des données
    with st.spinner("Analyse du marché en cours..."):
        for ticker in tickers_choisis:
            try:
                df = yf.download(ticker, period="1y", progress=False)
                if not df.empty:
                    # Calcul des moyennes mobiles
                    df['MMS20'] = df['Close'].rolling(window=20).mean()
                    df['MMS50'] = df['Close'].rolling(window=50).mean()
                    
                    # Extraction des dernières valeurs
                    prix = df['Close'].iloc[-1].item()
                    mms20 = df['MMS20'].iloc[-1].item()
                    mms50 = df['MMS50'].iloc[-1].item()
                    
                    # Algorithme de signal
                    if prix > mms50 and mms20 > mms50:
                        statut = "🟢 Achat (Tendance Hausse)"
                    elif prix < mms50 and mms20 < mms50:
                        statut = "🔴 Attendre (Tendance Baisse)"
                    else:
                        statut = "🟡 Neutre (Consolidation)"
                    
                    resultats.append({
                        "Action": ticker,
                        "Prix Actuel ($)": round(prix, 2),
                        "MMS 20 (Court terme)": round(mms20, 2),
                        "MMS 50 (Moyen terme)": round(mms50, 2),
                        "Signal de l'Algorithme": statut
                    })
                    historiques_actions[ticker] = df
            except Exception as e:
                st.error(f"Erreur sur le ticker {ticker}")

    # 2. Affichage du Tableau de synthèse
    st.subheader("📊 Tableau de Synthèse des Signaux")
    tableau_df = pd.DataFrame(resultats)
    st.dataframe(tableau_df, use_container_width=True, hide_index=True)

    # 3. Section Graphique Dynamique
    st.markdown("---")
    st.subheader("🔍 Analyse Graphique Détaillée")
    
    action_visuelle = st.selectbox("Sélectionnez une action pour voir son graphique complet :", tickers_choisis)
    
    if action_visuelle in historiques_actions:
        df_graph = historiques_actions[action_visuelle]
        
        # Création du graphique Plotly
        fig = go.Figure()
        
        # Courbe des prix
        fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['Close'], name='Prix de Clôture', line=dict(color='#1f77b4', width=2)))
        # Courbe MMS 20
        fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['MMS20'], name='MMS 20 (Court terme)', line=dict(color='#ff7f0e', width=1.5, dash='dash')))
        # Courbe MMS 50
        fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['MMS50'], name='MMS 50 (Moyen terme)', line=dict(color='#d62728', width=1.5)))
        
        # Style du graphique
        fig.update_layout(
            title=f"Historique 1 an et indicateurs pour {action_visuelle}",
            xaxis_title="Date",
            yaxis_title="Prix ($)",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        # Affichage du graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Veuillez sélectionner au moins une action dans la liste pour générer le tableau de bord.")