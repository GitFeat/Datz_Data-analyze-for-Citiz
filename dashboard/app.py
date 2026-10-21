"""Lanceur léger : l'explorateur visuel est fourni par PyGWalker."""
import streamlit as st
from pygwalker.services.global_var import GlobalVarManager

GlobalVarManager.set_privacy("offline")
from pygwalker.api.streamlit import StreamlitRenderer

from data import ROOT, TABLES, load_table

st.set_page_config(page_title="Explorer les données Citiz", layout="wide")
st.title("Explorer les données Citiz")
st.caption("Choisis une table, découvre ses colonnes puis crée tes graphiques par glisser-déposer.")
label = st.sidebar.selectbox("Données à explorer", list(TABLES))
path = ROOT / TABLES[label]
st.sidebar.caption(TABLES[label])
if not path.exists():
    st.warning("Ce fichier n’a pas encore été généré. Exécute les notebooks indiqués dans regional-data/README.md.")
    st.stop()


@st.cache_data(max_entries=4)
def read_table(label, signature):
    return load_table(label)


try:
    signature = path.stat().st_mtime_ns
    df = read_table(label, signature)
except (OSError, ValueError) as error:
    st.error(f"Impossible de préparer les données : {error}")
    st.stop()

st.write(f"**{len(df):,} lignes · {len(df.columns)} colonnes**")
st.info("Les valeurs vides restent inconnues. Un zéro OSM signifie qu’aucun objet correspondant n’a été recensé. La disponibilité Citiz est un instantané, pas une mesure de demande.")
with st.expander("Premiers croisements : mode d’emploi", expanded=True):
    st.markdown("""
1. Commence par **Stations et équipements croisés (AURA)** : une ligne représente une station, jointe par `station_uid`.
2. Dans l’explorateur, glisse `departement` sur **X**, puis `amenities_count_500m` sur **Y**. Choisis **moyenne / mean** pour comparer l’environnement moyen des stations.
3. Pour un nuage de points, utilise `capacity` en X et `amenities_count_500m` en Y, avec `station_uid` dans **Détails / Details** pour conserver un point par station. Désactive l’agrégation si nécessaire.
4. Ajoute `reseau` en couleur ou `departement` dans les filtres. Compare aussi les colonnes suffixées `_straight_line` avec les distances piétonnes.

Une association est une piste d’analyse, pas une preuve de causalité. Les équipements autour de plusieurs stations peuvent se recouper : leur somme n’est pas un total régional unique.
""")
with st.expander("Aperçu et qualité des colonnes"):
    st.dataframe(df.head(100), hide_index=True)
    quality = df.isna().sum().rename("Valeurs manquantes").to_frame()
    quality["Type"] = df.dtypes.astype(str)
    st.dataframe(quality, use_container_width=True)
    st.caption("Aperçu limité à 100 lignes ; l’explorateur utilise la table complète.")
    dictionary = ROOT / "regional-data/DATA_DICTIONARY.md"
    if dictionary.exists():
        st.markdown(dictionary.read_text())

# Le cache est propre à chaque session pour isoler les configurations des utilisateurs.
key = (label, signature)
if st.session_state.get("renderer_key") != key:
    with st.spinner("Préparation de l’explorateur…"):
        st.session_state.renderer = StreamlitRenderer(df, kernel_computation=True)
        st.session_state.renderer_key = key
st.session_state.renderer.explorer()
