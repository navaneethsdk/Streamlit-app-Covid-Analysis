import numpy as np 
import pandas as pd
import streamlit as st
import urllib.request
import json
import plotly.graph_objects as go
import seaborn as sns
import pydeck as pdk
import matplotlib.pyplot as plt
import plotly.express as px

State_dict = {'ANDAMAN AND NICOBAR': 'an',
 'ANDHRA PRADESH': 'ap',
 'ARUNACHAL PRADESH': 'ar',
 'ASSAM': 'as',
 'BIHAR': 'br',
 'CHANDIGARH': 'ch',
 'CHHATTISGARH': 'ct',
 'DADRA AND NAGAR HAVELI': 'dn',
 'DAMAN AND DIU': 'dd',
 'DELHI': 'dl',
 'GOA': 'ga',
 'GUJARAT': 'gj',
 'HARYANA': 'hr',
 'HIMACHAL PRADESH': 'hp',
 'JAMMU AND KASHMIR': 'jk',
 'JHARKHAND': 'jh',
 'KARNATAKA': 'ka',
 'KERALA': 'kl',
 'LAKSHADWEEP': 'ld',
 'MADHYA PRADESH': 'mp',
 'MAHARASHTRA': 'mh',
 'MANIPUR': 'mn',
 'MEGHALAYA': 'ml',
 'MIZORAM': 'mz',
 'NAGALAND': 'nl',
 'ORISSA': 'or',
 'PUDUCHERRY': 'py',
 'PUNJAB': 'pb',
 'RAJASTHAN': 'rj',
 'SIKKIM': 'sk',
 'TAMIL NADU': 'tn',
 'TRIPURA': 'tr',
 'UTTAR PRADESH': 'up',
 'UTTARANCHAL': 'ut',
 'WEST BENGAL': 'wb'}
State_abb = {value : key for (key, value) in State_dict.items()}
url = 'https://api.covid19india.org/states_daily.json'
url_pos = 'datasets_1713_2991_poptable.csv'

def strip_state(nm):
    return nm.strip()

def abbreviate(nm):
    return State_dict.get(nm, "UNKNOWN")

def Abb(x):
  return State_abb[x]


@st.cache(persist=True)
def load_data(url):
    urllib.request.urlretrieve(url, 'data.json')
    covid_data = pd.read_json('data.json')
    with open('data.json') as f:
        data = json.load(f)
    data = data['states_daily']
    df = pd.json_normalize(data)
    df.date = pd.to_datetime(df.date)
    df.set_index('date',inplace=True)
    stat = df.status
    df.drop('status',axis=1, inplace=True)
    df = df.apply(pd.to_numeric)
    df['status'] = stat
    df.drop('un', axis=1, inplace=True)
    df.drop('tt', axis=1, inplace=True)
    return df

@st.cache(persist=True)
def load_pos_data(url_pos):
    pos = pd.read_csv(url_pos)
    pos = pos[['State.Name','latitude','longitude']]
    pos['State.Name'] = pos['State.Name'].apply(strip_state)
    pos['Abb'] = pos['State.Name'].apply(abbreviate)
    pos.set_index('Abb',inplace=True)
    pos.drop('State.Name',axis=1,inplace=True)
    return pos

st.title("Covid Data Analysis - India")
st.markdown("Raw Data")
data = load_data(url)
pos = load_pos_data(url_pos)
if st.checkbox("Show raw data", False):
    st.write(data)


def plot_stackedarea_by_state(df,state):
    df__=df.reset_index()
    df__ = df__[[state,'date','status']]
    # df__.date = pd.to_datetime(df__.date)
    # df__[state] = pd.to_numeric(df__[state])
    df__ = df__.pivot_table(values=state ,columns='status',index='date')
    fig = plt.gcf()
    fig.set_size_inches(15,5)
    plt.stackplot(df__.index, df__.Confirmed/df__.sum(axis=1), df__.Recovered/df__.sum(axis=1), df__.Deceased/df__.sum(axis=1),
                    colors=['Orange','Green','Red'],labels =['Confirmed','Recovered','Deceased'])
    plt.legend();
    st.pyplot()

def plot_stacked_status_by_state(df,state):
    df__=df.reset_index()
    df__ = df__[[state,'date','status']]
    # df__.date = pd.to_datetime(df__.date)
    # df__[state] = pd.to_numeric(df__[state])
    df__ = df__.pivot_table(values=state ,columns='status',index='date')
    fig = plt.gcf()
    fig.set_size_inches(15,5)
    plt.stackplot(df__.index, df__.Confirmed, df__.Recovered, df__.Deceased,
                colors=['Orange','Green','Red'],labels =['Confirmed','Recovered','Deceased'])
    plt.legend();
    st.pyplot()

def relative_plot(df):
    df_ = df.sort_values('ConfirmedPercent', ascending=False)
    fig1 = plt.gcf()
    fig1.set_size_inches(10,6)
    plt.bar(df_.index, df_.ConfirmedPercent, color='Orange')
    plt.bar(df_.index, df_.RecoveredPercent, bottom=df_.ConfirmedPercent, color='Green')
    plt.bar(df_.index, df_.DeceasedPercent, bottom=df_.ConfirmedPercent + df_.RecoveredPercent,color='Red')
    plt.xticks(rotation=90)
    plt.legend();
    st.pyplot()

def bar_plot_previous_day(df):
    df_ = df.sort_values('Confirmed', ascending=False)
    fig = plt.gcf()
    fig.set_size_inches(10,6)
    plt.bar(df_.index, df_.Confirmed, color='Orange')
    plt.bar(df_.index, df_.Recovered, bottom=df_.Confirmed,color='Green')
    plt.bar(df_.index, df_.Deceased, bottom=df_.Confirmed + df_.Recovered,color='Red')
    plt.xticks(rotation=90)
    
    for i, val in enumerate(df_.index):
        y = df_.loc[val,'Total'] + 1300
        x = i+0.3
        if y>1000:
            plt.text(x,y, str(y), ha='center',rotation=90, rotation_mode='anchor')
    plt.legend()
    st.pyplot()


st.header("Previous day cases")


df = data.tail(3)
df.set_index('status', inplace=True)
# df_.drop('date', axis=1, inplace=True)
df = df.T
df['Total'] = df.sum(axis=1)
df['ConfirmedPercent'] = df.Confirmed / df.Total
df['RecoveredPercent'] = df.Recovered / df.Total
df['DeceasedPercent'] = df.Deceased / df.Total

df_= df.join(pos, how="inner")
df_.reset_index(inplace=True)
df_.sort_values('Confirmed',ascending=False,inplace=True)
df_.reset_index(inplace=True)
df_.drop('level_0',axis=1,inplace=True)
df_['index'] = df_['index'].apply(Abb)

df_['text'] = df_['index'] + '<br>Confirmed ' + (df_['Confirmed']).astype(str)+' people'
limits = [(0,6),(7,12),(13,18),(19,24),(25,30)]
colors = ["crimson","royalblue","lightseagreen","orange","lightgrey"]
cities = []
scale = 15


fig = go.Figure()

for i in range(len(limits)):
    lim = limits[i]
    df__sub = df_[lim[0]:lim[1]]
    fig.add_trace(go.Scattergeo(
        locationmode = 'country names',
        lon = df__sub['longitude'],
        lat = df__sub['latitude'],
        text = df__sub['text'],
        marker = dict(
            size = df__sub['Confirmed']/scale,
            color = colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lim[0],lim[1])))

fig.update_layout(
        title_text = 'Confirmed Cases on ' + str(data.index[-1]),
        showlegend = True,
        geo = dict(
            scope = 'asia',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

st.write(fig)

# lat = []
# lng = [] 
# for i,val in enumerate(df_.Confirmed):
#   for j in range(int(val/5)):
#     lat.append(df_.loc[i]['latitude'])
#     lng.append(df_.loc[i]['longitude'])




# midpoint = (np.average(pos["latitude"]), np.average(pos["longitude"]))
# r = pdk.Deck(
#     map_style="mapbox://styles/mapbox/light-v9",
#     initial_view_state={
#         "latitude": midpoint[0],
#         "longitude": midpoint[1],
#         "zoom": 4,
#         "pitch": 50,
#     },
#     layers=[
#         pdk.Layer(
#         "HexagonLayer",
#         data=plot_data,
#         get_position=["longitude", "latitude"],
#         get_elevation="Confirmed",
#         auto_highlight=True,
#         radius=100,
#         extruded=True,
#         pickable=True,
#         elevation_scale=4,
#         elevation_range=[0, 3000],
#         ),
#     ],
# )
# r.to_html("hexagon_layer.html")
# st.write(r)


st.write(df)

st.subheader("States ordered by the number of Confirmed cases")

bar_plot_previous_day(df)


st.subheader("Relative bar plot to compare Confirmed, Recovered and Deceased people across states")
relative_plot(df)

st.subheader("Select the state to view state wise analysis")
selected_state = st.selectbox('Select State', list(State_dict.keys()))

st.subheader("Confirmed,Recovered and Deceased cases in "+selected_state)
plot_stacked_status_by_state(data,State_dict[selected_state])
st.subheader(" Relative Confirmed,Recovered and Deceased cases in "+selected_state)
plot_stackedarea_by_state(data,State_dict[selected_state])  

