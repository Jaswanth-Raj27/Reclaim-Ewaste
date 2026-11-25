"""Reclaim: an e-waste forecasting, traceability and device assessment prototype."""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from assessment_engine import PROFILES, BATTERY_DEVICES, evaluate
device_scene_component = components.declare_component("reclaim_device_scene", path=str(Path(__file__).parent / "device_scene_component"))
import pandas as pd
import numpy as np
import hashlib
import json
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import os

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Reclaim | E-waste intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DARK THEME CSS - HIGH CONTRAST
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;450;500;600&display=swap');
:root{--ink:#232323;--muted:#6E6A65;--paper:#F6F5F2;--line:#DFDCD7;--green:#B74936}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif}
[data-testid="stHeader"]{background:var(--paper)}
[data-testid="stSidebar"]{background:#EEECE7;border-right:1px solid #DFDCD7;min-width:240px!important;max-width:240px!important}
[data-testid="stSidebar"]>div{padding-top:32px}
.block-container{padding:2.4rem 3.2rem 3rem;max-width:1550px}
h1{font-size:30px!important;font-weight:450!important;letter-spacing:-1px;line-height:1.2!important;padding-bottom:8px!important}
h2,h3{font-size:17px!important;font-weight:500!important;letter-spacing:-.2px}
p,label,[data-testid="stMarkdownContainer"]{color:var(--ink);font-family:'IBM Plex Sans',sans-serif}
.intro{color:var(--muted);font-size:15px;margin-bottom:28px;max-width:650px;line-height:1.6}
.brand{font-size:28px;letter-spacing:-1.3px;font-weight:500;line-height:1.2;margin-bottom:12px}
.brand svg{display:none}
.scope{color:var(--muted);font-size:12px;margin-bottom:38px;line-height:1.6;max-width:160px}
[data-testid="stSidebar"] [role="radiogroup"]{gap:8px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:9px 10px!important;border-radius:3px;width:100%;margin:0!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#E5E1DA}
[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none}
[data-testid="stSidebar"] [role="radiogroup"] p{font-size:14px!important}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-size:12px;color:#6E6A65}
[data-testid="stMetric"]{background:transparent;padding:16px 0 18px;border-top:1px solid var(--line);border-radius:0;font-variant-numeric:tabular-nums}
[data-testid="stMetricLabel"] p{font-size:13px!important;font-weight:400;color:var(--muted)!important}
[data-testid="stMetricValue"]{font-size:36px!important;font-weight:400!important;letter-spacing:-1.4px;color:var(--ink)}
[data-testid="stMetricDelta"]{background:none!important;color:var(--muted)!important;padding:0!important;font-size:12px}
[data-testid="stMetricDelta"] svg{display:none}
[data-testid="stVerticalBlockBorderWrapper"]>div{border:0!important;border-radius:0!important;padding:16px 0!important;background:transparent}
[data-testid="stExpander"]{background:transparent;border-color:var(--line);border-radius:3px}
[data-baseweb="input"],[data-baseweb="select"]>div{background:#EEECE7!important;color:var(--ink)!important;border-radius:3px!important}
.stButton button,.stDownloadButton button{background:#B74936;color:white;border:1px solid #B74936;border-radius:3px;min-height:38px;transition:background .15s}
.stButton button p,.stDownloadButton button p{color:white!important;font-size:13px}
.stButton button:hover,.stDownloadButton button:hover{background:#983B2C;border-color:#983B2C;color:white}
button:focus-visible{outline:2px solid #B74936!important;outline-offset:3px}
.info-box,.success-box,.warning-box,.danger-box{padding:16px;background:#EEECE7;border-radius:3px;margin:12px 0;line-height:1.6}
.status-badge{display:inline-block;padding:4px 10px;background:#E6E8E1;color:#394D37;border-radius:3px;font-size:13px}
.status-disposal{background:#f3e5e0;color:#793a2c}.status-recyclable{background:#eee9da;color:#665626}
.footer{font-size:12px;color:var(--muted);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}
hr{border-color:var(--line);margin:24px 0}
[data-testid="stCaptionContainer"] p{color:var(--muted);font-size:12px;line-height:1.6}
@media(max-width:700px){.block-container{padding:1.5rem 1.1rem}h1{font-size:26px!important}[data-testid="stMetricValue"]{font-size:30px!important}}
[data-baseweb="tab-list"]{gap:24px;background:transparent;margin-bottom:24px}
[data-baseweb="tab"]{padding:0 0 12px;font-size:14px;height:40px}
[data-baseweb="tab-panel"]{padding-top:0}
[data-baseweb="tab-panel"]:not([hidden]){animation:workspace-in 140ms ease-out}
@keyframes workspace-in{from{opacity:.7}to{opacity:1}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>
""",unsafe_allow_html=True)

class EWasteConditionAssessment:

    DEVICE_VALUES = {
        'Smartphone':        {'excellent': 180, 'good': 120, 'fair': 60,  'poor': 20},
        'Laptop':            {'excellent': 350, 'good': 220, 'fair': 100, 'poor': 30},
        'Television':        {'excellent': 150, 'good': 90,  'fair': 40,  'poor': 10},
        'Lithium-ion Battery':{'excellent': 80, 'good': 50,  'fair': 25,  'poor': 5},
        'Desktop Computer':  {'excellent': 250, 'good': 150, 'fair': 70,  'poor': 20},
        'Printer':           {'excellent': 100, 'good': 60,  'fair': 30,  'poor': 10},
        'Monitor':           {'excellent': 120, 'good': 70,  'fair': 35,  'poor': 10},
        'Keyboard':          {'excellent': 40,  'good': 25,  'fair': 12,  'poor': 3}
    }

    @staticmethod
    def assess_condition(ewaste_type, condition_score, battery_health=None, functionality=None):
        overall_score = condition_score
        if battery_health is not None:
            overall_score = (overall_score + battery_health) / 2
        if functionality is not None:
            overall_score = (overall_score + functionality) / 2

        if overall_score >= 75:
            status = 'Reusable'
            condition_level = 'excellent'
            reuse_components = ['CPU', 'RAM', 'Storage', 'Display', 'Battery', 'Motherboard']
            hazard_level = 'Low'
        elif overall_score >= 50:
            status = 'Recyclable'
            condition_level = 'good'
            reuse_components = ['Precious Metals', 'Copper', 'Aluminum', 'Plastics']
            hazard_level = 'Medium'
        else:
            status = 'Disposal'
            condition_level = 'poor'
            reuse_components = []
            hazard_level = 'High'

        device_values = EWasteConditionAssessment.DEVICE_VALUES.get(ewaste_type, {})
        recovery_value = device_values.get(condition_level, 0)

        if status == 'Reusable':
            recommendation = f"Device is in excellent condition. Suitable for refurbishment and resale. Estimated value: ${recovery_value}"
        elif status == 'Recyclable':
            recommendation = f"Device can be recycled. Components can be recovered for material recycling. Estimated material value: ${recovery_value}"
        else:
            recommendation = "Device requires safe disposal due to hazardous materials. Must be handled by certified recyclers."

        return {
            'status': status,
            'score': round(overall_score, 1),
            'recommendation': recommendation,
            'reuse_components': reuse_components,
            'hazard_level': hazard_level
        }

    @staticmethod
    def get_reuse_components_by_type(ewaste_type):
        components = {
            'Smartphone':        ['CPU', 'RAM', 'Storage', 'Display', 'Battery', 'Camera Module', 'Sensors'],
            'Laptop':            ['CPU', 'RAM', 'SSD', 'Display', 'Battery', 'Keyboard', 'Motherboard', 'Cooling System'],
            'Television':        ['Display Panel', 'Power Supply', 'Tuner', 'Audio Components', 'Control Board'],
            'Lithium-ion Battery':['Battery Cells', 'BMS (Battery Management System)', 'Connectors'],
            'Desktop Computer':  ['CPU', 'GPU', 'RAM', 'Power Supply', 'Motherboard', 'Storage Drives'],
            'Printer':           ['Print Head', 'Motor', 'Power Supply', 'Rollers', 'Toner Cartridge'],
            'Monitor':           ['Display Panel', 'Power Supply', 'Control Board', 'Backlight'],
            'Keyboard':          ['Keycaps', 'Switches', 'PCB', 'Controller']
        }
        return components.get(ewaste_type, ['Various Components'])

# ============================================================================
# LOAD AND TRAIN MODEL WITH ACTUAL DATASET
# ============================================================================

@st.cache_resource
def load_and_train_model():
    try:
        df = pd.read_csv('training_data_full_ewaste.csv')
    except FileNotFoundError:
        from io import StringIO
        data_string = """Year,Population_Billion,GDP_TrillionUSD,Internet_Users_Billion,Generated_Mt,Recycled_Mt,Unrecycled_Mt,Cumulative_Unrecycled_Mt
2010,6.92,65.6,2.03,34.0,2.72,31.28,31.28
2011,7.0,68.0,2.2,35.8,3.04,32.76,64.04
2012,7.08,70.4,2.4,37.8,3.4,34.4,98.44
2013,7.16,72.9,2.6,39.8,3.9,35.9,134.34
2014,7.24,75.4,2.8,41.8,4.39,37.41,171.75
2015,7.32,78.0,3.0,44.4,5.24,39.16,210.91
2016,7.4,80.7,3.3,46.8,6.08,40.72,251.63
2017,7.48,83.4,3.6,48.9,6.85,42.05,293.68
2018,7.56,86.2,3.9,50.8,7.62,43.18,336.86
2019,7.64,89.0,4.1,53.6,9.33,44.27,381.13
2020,7.72,87.5,4.3,55.5,9.99,45.51,426.64
2021,7.8,91.2,4.6,57.4,11.48,45.92,472.56
2022,7.88,95.1,4.9,62.0,13.83,48.17,520.73
2023,7.95,98.0,5.2,64.2,14.64,49.56,570.29
2024,8.02,101.0,5.4,66.5,15.63,50.87,621.16
2025,8.1,104.0,5.6,68.0,16.32,51.68,672.84"""
        df = pd.read_csv(StringIO(data_string))

    historical_df = df[df['Year'] <= 2023].copy()
    X = historical_df[['Population_Billion', 'GDP_TrillionUSD', 'Internet_Users_Billion']]
    y = historical_df['Generated_Mt']
    model = LinearRegression()
    model.fit(X, y)
    return model, df

def forecast_ewaste_with_dataset(model, df, years=[2026, 2027, 2028, 2029, 2030]):
    actual_df = df[df['Year'] <= 2025].copy()
    future_data = {
        'Year': years,
        'Population_Billion': [8.18, 8.26, 8.34, 8.42, 8.50],
        'GDP_TrillionUSD': [107.0, 110.0, 113.0, 116.0, 119.0],
        'Internet_Users_Billion': [5.8, 6.0, 6.2, 6.4, 6.6]
    }
    df_future = pd.DataFrame(future_data)
    X_future = df_future[['Population_Billion', 'GDP_TrillionUSD', 'Internet_Users_Billion']]
    generated = model.predict(X_future)
    recycled_rate = [0.235, 0.245, 0.255, 0.265, 0.275]
    recycled = generated * np.array(recycled_rate)
    unrecycled = generated - recycled
    df_future['Generated_Mt'] = generated
    df_future['Recycled_Mt'] = recycled
    df_future['Unrecycled_Mt'] = unrecycled
    last_cumulative = actual_df['Cumulative_Unrecycled_Mt'].iloc[-1]
    cumulative = []
    for val in unrecycled:
        last_cumulative += val
        cumulative.append(last_cumulative)
    df_future['Cumulative_Unrecycled_Mt'] = cumulative
    combined_df = pd.concat([actual_df, df_future], ignore_index=True)
    return combined_df, df_future

# ============================================================================
# INITIALIZATION & SESSION STATE — WITH MYSQL LOAD ON STARTUP
# ============================================================================

if 'model' not in st.session_state:
    st.session_state.model, st.session_state.full_df = load_and_train_model()
with st.sidebar:
    st.markdown('<div class="brand">Reclaim</div><div class="scope">Material recovery<br>Research workspace</div>',unsafe_allow_html=True)
    st.caption('Product traceability')
    st.write('Local Ethereum · chain 1337')
    st.caption('Smart-contract passports and confirmed custody transfers. Network status is shown in Traceability.')
    st.divider()
    st.caption('Jaswanth Raj\n\nE-waste research prototype')

workspace_names = ['Outlook', 'Traceability', 'Device assessment']
workspace_tabs = st.tabs(workspace_names, default="Traceability" if st.query_params.get("product") else "Outlook")
for view, workspace_tab in zip(workspace_names, workspace_tabs):
    with workspace_tab:
        if view == 'Outlook':
            st.title('E-waste outlook')
            st.markdown('<p class="intro">Explore the gap between electronic waste generation and material recovery.</p>',unsafe_allow_html=True)
            controls,space,download=st.columns([1,2,1])
            with controls:
                year=st.selectbox('Scenario horizon',options=list(range(2026,2031)),index=4)
            combined,forecast=forecast_ewaste_with_dataset(st.session_state.model,st.session_state.full_df)
            row=forecast[forecast.Year==year].iloc[0]
            base=st.session_state.full_df.iloc[-1]
            with download:
                st.download_button('Export data',combined.to_csv(index=False),'ewaste_scenario.csv','text/csv',use_container_width=True)
            st.caption('Global scope · Annual records, 2010–2025 · Scenario projections, 2026–2030')
            cols=st.columns(3)
            cols[0].metric(f'{year} generated',f"{row.Generated_Mt:.1f} Mt",f"{row.Generated_Mt-base.Generated_Mt:+.1f} Mt vs 2025",delta_color='off')
            cols[1].metric(f'{year} recycled',f"{row.Recycled_Mt:.1f} Mt",f"{100*row.Recycled_Mt/row.Generated_Mt:.1f}% of projected generation",delta_color='off')
            cols[2].metric(f'{year} unrecycled',f"{row.Unrecycled_Mt:.1f} Mt",'Generation minus recycling',delta_color='off')
            st.write('')
            left,right=st.columns([2.2,1])
            def style(fig,height=355):
                fig.update_layout(height=height,paper_bgcolor='#F6F5F2',plot_bgcolor='#F6F5F2',font=dict(family='IBM Plex Sans, sans-serif',color='#6E6A65',size=12),margin=dict(l=10,r=15,t=15,b=10),legend=dict(orientation='h',y=1.13),hovermode='x unified')
                fig.update_xaxes(showgrid=False,tickmode='array',tickvals=[2010,2015,2020,2025,2030])
                fig.update_yaxes(gridcolor='#e2e6df',zeroline=False,rangemode='tozero')
                return fig
            with left:
                with st.container(border=True):
                    st.subheader('Generation over time')
                    fig=go.Figure()
                    hist=combined[combined.Year<=2025]
                    future=combined[(combined.Year>=2025)&(combined.Year<=year)]
                    fig.add_trace(go.Scatter(x=hist.Year,y=hist.Generated_Mt,name='Dataset records',mode='lines',line=dict(color='#8B8882',width=2)))
                    fig.add_trace(go.Scatter(x=future.Year,y=future.Generated_Mt,name='Scenario forecast',mode='lines',line=dict(color='#B74936',width=2.5,dash='dash')))
                    fig.update_yaxes(title_text='Million tonnes')
                    st.plotly_chart(style(fig),use_container_width=True,config={'displayModeBar':False})
            with right:
                with st.container(border=True):
                    st.subheader(f'Material balance · {year}')
                    fig=go.Figure()
                    for label,value,color in [('Recycled',row.Recycled_Mt,'#B74936'),('Unrecycled',row.Unrecycled_Mt,'#B9B3AA')]:
                        fig.add_trace(go.Bar(x=[label],y=[value],name=label,marker_color=color,text=[f'{value:.1f} Mt'],textposition='outside',showlegend=False))
                    fig.update_yaxes(title_text='Million tonnes',range=[0,row.Generated_Mt])
                    fig=style(fig)
                    fig.update_xaxes(tickmode='auto')
                    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.caption('Interpretation: projections depend on assumed economic inputs and recycling rates. The dataset source is undocumented; these results are illustrative.')
            with st.expander('Methodology and assumptions'):
                st.write('Linear regression uses population, GDP and internet users. Training covers 2010–2023 (14 rows). No out-of-sample performance estimate has been established here.')
                st.write('2026–2030 predictors and recycling rates are predefined scenarios. The dataset has no documented source in this project. Cumulative totals start in 2010 and are not an estimate of all historical waste.')
                st.dataframe(forecast[['Year','Population_Billion','GDP_TrillionUSD','Internet_Users_Billion']].set_index('Year'),use_container_width=True)
            with st.expander('Explore all records'):
                st.dataframe(combined.round(2),use_container_width=True,hide_index=True)

        elif view == "Traceability":
            from traceability_ui import render as render_passports
            render_passports()

        elif view == "Device assessment":
            st.title('Device assessment')
            st.caption('Inspect the device, record functional checks, and understand its recovery options.')
            controls,scene_col=st.columns([1,2.1],gap='large')
            with controls:
                ewaste_type=st.selectbox('Device type',list(EWasteConditionAssessment.DEVICE_VALUES))
                condition_score=st.slider('Physical condition',0,100,85,help='75–100: intact. 40–74: cracks. Below 40: severe damage.')
                functionality=st.slider('Functionality',0,100,85)
                battery_health=st.slider('Battery health',0,100,80) if ewaste_type in BATTERY_DEVICES else None
                with st.expander('Device checks',expanded=True):
                    checks={name:st.selectbox(name,['Not checked','Pass','Impaired','Failed'],key=ewaste_type+'_'+name) for name in PROFILES[ewaste_type]}
                    hazard=st.checkbox('Swelling, leakage, overheating or burn damage',key='hazard_'+ewaste_type)
            result=evaluate(ewaste_type,condition_score,functionality,battery_health,checks,hazard)
            with scene_col:
                device_scene_component(device=ewaste_type,condition=condition_score,battery=battery_health if battery_health is not None else 100,functionality=functionality,hasBattery=battery_health is not None,key='device_scene',default=None)
                st.caption('Illustrative geometry. Drag to rotate; scroll to zoom. Physical damage, operation and battery health are independent inputs.')
                st.subheader(result['route'])
                st.write(result['action'])
            st.divider()
            score,explanation=st.columns([1,2.1],gap='large')
            with score:
                st.metric('Condition summary',str(result['score'])+'/100')
                st.caption('Arithmetic average of entered scores; not a confidence level. Critical faults override this number.')
            with explanation:
                st.subheader('Why this route?')
                for reason in result['reasons']: st.write('• '+reason)
                with st.expander('How the rules work'):
                    st.write('Priority: reported hazard → severe damage or non-operation → failed functional checks → battery service → incomplete checks → refurbishment → potential reuse.')
                    st.write('These are transparent prototype thresholds, not manufacturer standards or a safety certification. A low score alone never proves a device must be disposed of.')

# FOOTER
st.markdown('<div class="footer">Reclaim · E-waste research prototype · Forecasts are scenarios, not validated predictions.</div>',unsafe_allow_html=True)
