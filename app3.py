import pandas as pd
import dash
import plotly.express as px
from dash import dcc, html, Input, Output
import folium

# Lecture des données à partir du fichier CSV
data_ratp = pd.read_csv('trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv', delimiter=';')

# Trier les données en fonction du trafic entrant
sorted_data_ratp = data_ratp.sort_values('Trafic', ascending=False)

# Obtenir les 10 premières stations avec le plus grand trafic
top_10_stations = sorted_data_ratp.head(10)

# Grouper les données par ville et sommer le trafic entrant pour chaque ville
trafic_par_ville = data_ratp.groupby('Ville')['Trafic'].sum().reset_index()

# Trier les données en fonction du trafic
sorted_data_ratp = trafic_par_ville.sort_values('Trafic', ascending=False)

# Obtenir les 5 premières villes avec le plus grand trafic
top_5_villes = sorted_data_ratp.head(5)

# Créer un graphique à barres pour représenter le trafic entrant pour chaque station
fig1 = px.bar(top_10_stations, x='Station', y='Trafic', title='Top 10 stations avec le plus grand trafic')
fig1.update_layout(xaxis_tickangle=-90)

# Créer un graphique circulaire pour représenter le trafic pour chaque ville
fig2 = px.pie(top_5_villes, values='Trafic', names='Ville', title='Répartition du trafic par ville')


# Chargement des données depuis le fichier CSV
data_idf = pd.read_csv('emplacement-des-gares-idf.csv', delimiter=';')

# Compter le nombre de stations par exploitant
exploitant_counts = data_idf['exploitant'].value_counts()

# Créer un graphique à barres pour représenter le nombre de stations par exploitant
fig3 = px.bar(exploitant_counts, x=exploitant_counts.index, y=exploitant_counts.values, color=exploitant_counts.index,
              labels={'x':'Exploitant', 'y':'Nombre de stations'}, title='Nombre de stations par exploitant')

# Compter le nombre de stations par ligne
ligne_counts = data_idf['ligne'].value_counts()

# Créer un graphique à barres pour représenter le nombre de stations par ligne
fig4 = px.bar(ligne_counts, x=ligne_counts.index, y=ligne_counts.values, color=ligne_counts.index,
              labels={'x':'Ligne', 'y':'Nombre de stations'}, title='Nombre de stations par ligne')


# Chargement des données
data_ratp = pd.read_csv('trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv', delimiter=';')
data = pd.read_csv('emplacement-des-gares-idf.csv', delimiter=';')

# Création des options pour le menu déroulant "Réseau"
network_options = [{'label': i, 'value': i} for i in data_ratp['Réseau'].unique()]
# Création du widget de sélection pour le mode
mode_filter = dcc.Dropdown(
    id='mode-filter',
    options=[{'label': mode, 'value': mode} for mode in data['mode'].unique()],
    value='RER',
    clearable=False
)


# Création des colonnes lat et lon à partir de la colonne geo_point
data[['lat', 'lon']] = data['Geo Point'].str.split(',', expand=True)
data['lat'] = data['lat'].str.strip().astype(float)
data['lon'] = data['lon'].str.strip().astype(float)

# Sélection des colonnes qui nous intéressent pour la carte
locations = data[['lat', 'lon', 'nom_long']]

# Création de la carte centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

# Ajout des markers pour chaque gare
for idx, row in locations.iterrows():
    folium.Marker(location=[row['lat'], row['lon']], tooltip=row['nom_long']).add_to(m)

# Affichage de la carte
m.save('map.html')



# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Création du graphique initial
def create_graph(mode):
    # Filtrer les données en fonction du mode sélectionné
    filtered_data = data[data['mode'] == mode]

    # Compter le nombre de lignes pour chaque exploitant
    ligne_count = filtered_data['ligne'].value_counts()

    # Trier les lignes par ordre décroissant du nombre de gares
    sorted_lignes = ligne_count.sort_values(ascending=False)

    # Créer le graphique
    graph = dcc.Graph(
        id='line-graph',
        figure={
            'data': [{
                'x': sorted_lignes.index,
                'y': sorted_lignes.values,
                'type': 'bar'
            }],
            'layout': {
                'title': f"Nombre de gares par ligne ({mode})",
                'xaxis': {'title': 'Ligne'},
                'yaxis': {'title': 'Nombre de gares'}
            }
        }
    )

    return graph


# Définition de la mise en page
app.layout = html.Div(children=[
    html.H1(children='Nombre de gares par ligne'),

    html.Div(children='''
        Sélectionner le mode de transport:
    '''),

    # Ajout du widget de sélection
    mode_filter,

    # Ajout du graphique initial
    html.Div(id='graph-container', children=create_graph('RER'))
])


# Définition de la fonction de rappel pour mettre à jour le graphique en fonction du mode sélectionné
@app.callback(Output('graph-container', 'children'), [Input('mode-filter', 'value')])
def update_graph(mode):
    graph = create_graph(mode)
    return graph


# Mise en forme de la page
app.layout = html.Div([
    html.Div([
        html.H2("Top 10 stations avec le plus grand trafic et Répartition du trafic par ville"),
        html.Div([
            dcc.Graph(figure=fig1),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure=fig2),
        ], style={'width': '48%', 'display': 'inline-block'}),
    html.H1(children='Statistiques sur les gares d\'IDF'),
    html.Div(children='Nombre de stations par exploitant et par ligne.'),
        dcc.Graph(id='graph1',figure=fig3),
        dcc.Graph(id='graph2',figure=fig4),]),


    # Titre de la page
    html.H1('Top 10 des stations avec le plus grand trafic'),
    # Menu déroulant pour filtrer les données par réseau
    dcc.Dropdown(
        id='network-filter',
        options=network_options,
        value='Métro',
        clearable=False
    ),
    # Graphique pour afficher les données
    dcc.Graph(
        id='traffic-graph',
        figure={}
    ),
     html.Div(children=[
    html.H1(children='Nombre de gares par ligne'),

    html.Div(children='''
        Sélectionner le mode de transport:
    '''),

    # Ajout du widget de sélection
    mode_filter,

    # Ajout du graphique initial
    html.Div(id='graph-container', children=create_graph('RER')),

         html.Div(children=[
             html.H1(children='Carte des gares en Ile-de-France'),
             html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width='100%', height='500')
         ])

     ])


])


# Fonction de rappel pour la mise à jour du graphique en fonction du réseau sélectionné
@app.callback(
    Output(component_id='traffic-graph', component_property='figure'),
    Input(component_id='network-filter', component_property='value')
)

def update_graph(selected_network):
    filtered_data_ratp = data_ratp[data_ratp['Réseau'] == selected_network]
    traffic_per_station = filtered_data_ratp.groupby('Station')['Trafic'].sum().reset_index()
    sorted_data_ratp = traffic_per_station.sort_values('Trafic', ascending=False)
    top_10_stations = sorted_data_ratp.head(10)
    fig = {
        'data': [
            {'x': top_10_stations['Station'], 'y': top_10_stations['Trafic'], 'type': 'bar'}
        ],
        'layout': {
            'title': f'Top 10 des stations avec le plus grand trafic ({selected_network})',
            'xaxis': {'title': 'Stations', 'tickangle': 90},
            'yaxis': {'title': 'Trafic en dizaine de millions'}
        }
    }
    return fig

# Exécution de l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)


