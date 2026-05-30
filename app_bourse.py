import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page Streamlit
st.set_page_config(page_title="Tableau de Bord & Portefeuille", layout="wide", page_icon="📈")

# --- INITIALISATION DU PORTEFEUILLE VIRTUEL ---
# Si le portefeuille n'existe pas dans la session, on le crée avec des exemples de simulation
if 'portefeuille' not in st.session_state:
    st.session_state.portefeuille = [
        {"Ticker": "AAPL", "Prix_Achat": 175.0, "Quantite": 10},
        {"Ticker": "MSFT", "Prix_Achat": 395.0, "Quantite": 5}
    ]

st.title("📈 Mon Espace Boursier Intelligent")
st.write("Suivez les signaux algorithmiques et gérez votre portefeuille virtuel en temps réel.")

# Création des deux onglets
onglet_analyse, onglet_portefeuille = st.tabs(["📊 Analyse & Signaux", "💼 Mon Portefeuille Virtuel"])

# ==============================================================================
# ONGLET 1 : ANALYSE & SIGNAUX
# ==============================================================================
with onglet_analyse:
    st.subheader("📊 Tableau de Synthèse des Signaux")
    
    watchlist_defaut = ["AAPL", "MSFT", "KO", "JNJ", "V"]
    tickers_choisis = st.multiselect(
        "Personnalisez votre liste de surveillance :",
        options=["AAPL", "MSFT", "KO", "JNJ", "V", "TSLA", "AMZN", "NFLX", "NVDA"],
        default=watchlist_defaut,
        key="watchlist_analyser"
    )

    if tickers_choisis:
        resultats = []
        historiques_actions = {}

        with st.spinner("Analyse du marché en cours..."):
            for ticker in tickers_choisis:
                try:
                    df = yf.download(ticker, period="1y", progress=False)
                    if not df.empty:
                        df['MMS20'] = df['Close'].rolling(window=20).mean()
                        df['MMS50'] = df['Close'].rolling(window=50).mean()
                        
                        prix = df['Close'].iloc[-1].item()
                        mms20 = df['MMS20'].iloc[-1].item()
                        mms50 = df['MMS50'].iloc[-1].item()
                        
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
                            "Signal": statut
                        })
                        historiques_actions[ticker] = df
                except Exception as e:
                    st.error(f"Erreur sur le ticker {ticker}")

        tableau_df = pd.DataFrame(resultats)
        st.dataframe(tableau_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Analyse Graphique Détaillée")
        action_visuelle = st.selectbox("Sélectionnez une action pour voir son graphique :", tickers_choisis)
        
        if action_visuelle in historiques_actions:
            df_graph = historiques_actions[action_visuelle]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['Close'], name='Prix de Clôture', line=dict(color='#1f77b4', width=2)))
            fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['MMS20'], name='MMS 20', line=dict(color='#ff7f0e', width=1.5, dash='dash')))
            fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph['MMS50'], name='MMS 50', line=dict(color='#d62728', width=1.5)))
            
            fig.update_layout(
                title=f"Historique 1 an et indicateurs pour {action_visuelle}",
                xaxis_title="Date", yaxis_title="Prix ($)",
                template="plotly_white", hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Veuillez sélectionner au moins une action.")

# ==============================================================================
# ONGLET 2 : SIMULATEUR DE PORTEFEUILLE VIRTUEL
# ==============================================================================
with onglet_portefeuille:
    st.subheader("💼 Suivi de mes Investissements Virtuels (Paper Trading)")
    
    # 1. Formulaire pour ajouter une ligne d'achat fictive
    with st.expander("📥 Enregistrer un nouvel achat virtuel", expanded=True):
        col_t, col_p, col_q = st.columns(3)
        with col_t:
            nouveau_ticker = st.text_input("Symbole de l'action (Ex: TSLA, KO, NVDA)", value="KO").upper().strip()
        with col_p:
            prix_achat = st.number_input("Prix d'achat unitaire ($)", min_value=0.01, value=65.0, step=0.5)
        with col_q:
            quantite = st.number_input("Nombre d'actions achetées", min_value=1, value=10, step=1)
        
        if st.button("Ajouter au portefeuille", use_container_width=True):
            if nouveau_ticker:
                st.session_state.portefeuille.append({
                    "Ticker": nouveau_ticker,
                    "Prix_Achat": prix_achat,
                    "Quantite": quantite
                })
                st.success(f"Achat virtuel enregistré : {quantite} actions de {nouveau_ticker} à {prix_achat} $")
                st.rerun()
            else:
                st.error("Veuillez entrer un symbole valide.")

    # 2. Calculs et Affichage du Portefeuille
    if st.session_state.portefeuille:
        # Extraire tous les tickers uniques du portefeuille pour récupérer leurs prix en une fois
        liste_tickers_p = list(set([position["Ticker"] for position in st.session_state.portefeuille]))
        
        prix_actuels = {}
        with st.spinner("Actualisation des cours en direct..."):
            for t in liste_tickers_p:
                try:
                    ticker_data = yf.Ticker(t).history(period="1d")
                    if not ticker_data.empty:
                        prix_actuels[t] = ticker_data['Close'].iloc[-1].item()
                    else:
                        prix_actuels[t] = 0.0
                except:
                    prix_actuels[t] = 0.0

        # Construction du tableau de bord du portefeuille
        lignes_portefeuille = []
        total_investi_global = 0.0
        total_valeur_globale = 0.0

        for position in st.session_state.portefeuille:
            t = position["Ticker"]
            p_achat = position["Prix_Achat"]
            q = position["Quantite"]
            p_actuel = prix_actuels.get(t, 0.0)

            cout_total = p_achat * q
            valeur_actuelle = p_actuel * q
            gain_perte = valeur_actuelle - cout_total
            gain_perte_pct = (gain_perte / cout_total) * 100 if cout_total > 0 else 0.0

            total_investi_global += cout_total
            total_valeur_globale += valeur_actuelle

            lignes_portefeuille.append({
                "Action": t,
                "Quantité": q,
                "Prix d'Achat ($)": round(p_achat, 2),
                "Coût Total ($)": round(cout_total, 2),
                "Prix Actuel ($)": round(p_actuel, 2) if p_actuel > 0 else "Erreur Ticker",
                "Valeur Actuelle ($)": round(valeur_actuelle, 2),
                "Gain / Perte ($)": round(gain_perte, 2),
                "Performance": f"{gain_perte_pct:+.2f}%"
            })

        df_portefeuille = pd.DataFrame(lignes_portefeuille)

        # Calcul des performances globales
        gain_global = total_valeur_globale - total_investi_global
        gain_global_pct = (gain_global / total_investi_global) * 100 if total_investi_global > 0 else 0.0

        # Affichage des indicateurs clés (Metrics)
        st.markdown("### 📈 Résumé de la Performance")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Capital Total Investi", f"{total_investi_global:,.2f} $")
        m_col2.metric("Valeur Actuelle du Portefeuille", f"{total_valeur_globale:,.2f} $")
        m_col3.metric("Plus / Moins-value Globale", f"{gain_global:,.2f} $", f"{gain_global_pct:+.2f}%")

        # Affichage du tableau détaillé
        st.markdown("### 📋 Détail des Positions")
        st.dataframe(df_portefeuille, use_container_width=True, hide_index=True)

        # Bouton de réinitialisation
        st.markdown("")
        if st.button("🗑️ Vider le portefeuille (Réinitialiser)", type="secondary"):
            st.session_state.portefeuille = []
            st.success("Le portefeuille virtuel a été réinitialisé.")
            st.rerun()
    else:
        st.info("Votre portefeuille virtuel est vide. Utilisez le formulaire ci-dessus pour simuler vos premiers achats.")
