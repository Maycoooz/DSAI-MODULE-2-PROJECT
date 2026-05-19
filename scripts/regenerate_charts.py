"""
Regenerate all 20 chart JSON files from BigQuery with pastel colours.
Run from the project root: python scripts/regenerate_charts.py
"""
from dotenv import load_dotenv
import os, json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from google.cloud import bigquery
from google.oauth2 import service_account

pio.json.config.default_engine = 'json'

# -- Setup --------------------------------------------------------------------
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_root, '.env'))

project_id  = os.getenv('GCP_PROJECT_ID')
creds_path  = os.path.join(project_root, os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
credentials = service_account.Credentials.from_service_account_file(creds_path)
client      = bigquery.Client(credentials=credentials, project=project_id)
OUT         = os.path.join(project_root, 'outputs')
os.makedirs(OUT, exist_ok=True)

def bq(sql): return client.query(sql).to_dataframe()
def save(fig, name):
    path = os.path.join(OUT, name)
    with open(path, 'w') as f: f.write(fig.to_json())
    print(f'  OK {name}')

# -- Pastel palette ------------------------------------------------------------
SKY     = '#93C6E7'
MINT    = '#A8D5B5'
PEACH   = '#F4C89E'
LAVEND  = '#C9B8E8'
ROSE    = '#F4A0A0'
TEAL    = '#8EC5C4'
YELLOW  = '#F7E59B'
BLUE_SEQ = ['#D0E8F2','#93C6E7','#5BA4C8','#2E7BA6','#1A4F6E']
GREEN_SEQ= ['#C8EAD3','#A8D5B5','#7BB898','#4E9B7B','#2E6E55']
RED_SEQ  = ['#FADADD','#F4A0A0','#E87070','#D44040','#B02020']

LAYOUT_BASE = dict(
    paper_bgcolor='#1a1a2e',
    plot_bgcolor ='#1a1a2e',
    font         =dict(color='#eaeaea', family='Segoe UI, system-ui, sans-serif', size=12),
    margin       =dict(t=40, r=20, b=60, l=80),
    xaxis        =dict(gridcolor='#2a2a4a', zerolinecolor='#2a2a4a', tickfont=dict(size=11)),
    yaxis        =dict(gridcolor='#2a2a4a', zerolinecolor='#2a2a4a', tickfont=dict(size=11)),
)
def layout(**kwargs):
    d = dict(LAYOUT_BASE)
    d.update(kwargs)
    return d

print('\n-- Chapter 1: Sales & Revenue --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_sales_revenue` ORDER BY year_month")

fig = go.Figure(go.Scatter(x=df['year_month'], y=df['total_revenue'].round(0),
    mode='lines+markers', line=dict(color=MINT, width=2.5),
    marker=dict(color=MINT, size=6), fill='tozeroy', fillcolor='rgba(168,213,181,0.15)',
    hovertemplate='%{x}<br>BRL %{y:,.0f}<extra></extra>'))
fig.update_layout(**layout(title='Monthly Revenue (BRL)', xaxis_title='Month', yaxis_title='Revenue (BRL)'))
save(fig, 'sales_monthly_revenue.json')

fig = go.Figure(go.Bar(x=df['year_month'], y=df['total_orders'],
    marker_color=SKY, hovertemplate='%{x}<br>%{y:,} orders<extra></extra>'))
fig.update_layout(**layout(title='Monthly Order Volume', xaxis_title='Month', yaxis_title='Orders'))
save(fig, 'sales_monthly_orders.json')

fig = go.Figure(go.Scatter(x=df['year_month'], y=df['avg_order_value'].round(2),
    mode='lines+markers', line=dict(color=PEACH, width=2.5),
    marker=dict(color=PEACH, size=6),
    hovertemplate='%{x}<br>BRL %{y:.2f}<extra></extra>'))
fig.update_layout(**layout(title='Average Order Value Over Time (BRL)', xaxis_title='Month', yaxis_title='Avg Order Value (BRL)'))
save(fig, 'sales_avg_order_value.json')

fig = go.Figure(go.Bar(x=df['year_month'], y=df['active_sellers'],
    marker_color=LAVEND, hovertemplate='%{x}<br>%{y} sellers<extra></extra>'))
fig.update_layout(**layout(title='Active Sellers Per Month', xaxis_title='Month', yaxis_title='Active Sellers'))
save(fig, 'sales_active_sellers.json')

print('\n-- Chapter 2: Delivery Performance --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_delivery_performance`")
state = df.groupby('seller_state').agg(
    on_time=('on_time_deliveries','sum'), late=('late_deliveries','sum'),
    avg_days=('avg_delivery_days','mean'), avg_score=('avg_review_score','mean')
).reset_index()
state['on_time_pct'] = (state['on_time'] / (state['on_time'] + state['late']) * 100).round(1)
state = state.sort_values('on_time_pct', ascending=True)

fig = go.Figure(go.Bar(x=state['on_time_pct'], y=state['seller_state'],
    orientation='h', marker_color=TEAL,
    hovertemplate='%{y}: %{x:.1f}%<extra></extra>'))
fig.update_layout(**layout(title='On-Time Delivery % by Seller State',
    xaxis_title='On-Time %', yaxis_title='State', margin=dict(t=40,r=20,b=60,l=50)))
save(fig, 'delivery_on_time_by_state.json')

state_days = state.sort_values('avg_days', ascending=False)
fig = go.Figure(go.Bar(x=state_days['seller_state'], y=state_days['avg_days'].round(1),
    marker_color=SKY, hovertemplate='%{x}: %{y:.1f} days<extra></extra>'))
fig.update_layout(**layout(title='Average Delivery Days by Seller State',
    xaxis_title='State', yaxis_title='Avg Delivery Days'))
save(fig, 'delivery_avg_days_by_state.json')

monthly = df.groupby('year_month').agg(on_time=('on_time_deliveries','sum'), late=('late_deliveries','sum')).reset_index()
monthly['on_time_pct'] = (monthly['on_time'] / (monthly['on_time'] + monthly['late']) * 100).round(1)
fig = go.Figure(go.Scatter(x=monthly['year_month'], y=monthly['on_time_pct'],
    mode='lines+markers', line=dict(color=MINT, width=2.5),
    marker=dict(color=MINT, size=6),
    hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'))
fig.update_layout(**layout(title='Monthly On-Time Delivery Rate (%)', xaxis_title='Month', yaxis_title='On-Time %'))
save(fig, 'delivery_monthly_trend.json')

state_sc = state.sort_values('on_time_pct')
fig = go.Figure(go.Bar(x=state_sc['on_time_pct'], y=state_sc['avg_score'].round(2),
    orientation='v',
    marker=dict(color=state_sc['avg_score'], colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=True, colorbar=dict(title='Score')),
    customdata=state_sc[['seller_state','on_time_pct']].values,
    hovertemplate='State %{customdata[0]}<br>On-Time: %{customdata[1]:.1f}%<br>Score: %{y:.2f}<extra></extra>'))
fig.update_layout(**layout(title='Avg Review Score by On-Time % (per State)',
    xaxis_title='On-Time %', yaxis_title='Avg Review Score'))
save(fig, 'delivery_score_vs_ontime.json')

print('\n-- Chapter 3: Customer Behaviour --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_customer_behaviour`")
by_state = df.groupby('customer_state').agg(
    total_orders=('total_orders','sum'), total_revenue=('total_revenue','sum'),
    total_customers=('total_customers','sum'), avg_score=('avg_review_score','mean')
).reset_index().sort_values('total_orders', ascending=False)

fig = go.Figure(go.Bar(x=by_state['customer_state'], y=by_state['total_orders'],
    marker=dict(color=by_state['total_orders'], colorscale=[[0,'#D0E8F2'],[1,'#2E7BA6']],
                showscale=False),
    hovertemplate='%{x}<br>%{y:,} orders<extra></extra>'))
fig.update_layout(**layout(title='Total Orders by Customer State', xaxis_title='State', yaxis_title='Orders'))
save(fig, 'customer_orders_by_state.json')

top_cities = df.groupby('customer_city').agg(total_orders=('total_orders','sum')).reset_index()\
    .sort_values('total_orders', ascending=False).head(15).sort_values('total_orders', ascending=True)
fig = go.Figure(go.Bar(x=top_cities['total_orders'], y=top_cities['customer_city'],
    orientation='h', marker_color=TEAL,
    hovertemplate='%{y}: %{x:,} orders<extra></extra>'))
fig.update_layout(**layout(title='Top 15 Cities by Order Volume',
    xaxis_title='Total Orders', yaxis_title='City', margin=dict(t=40,r=20,b=60,l=120)))
save(fig, 'customer_top_cities.json')

state_score = by_state.sort_values('avg_score', ascending=True)
fig = go.Figure(go.Bar(x=state_score['avg_score'].round(2), y=state_score['customer_state'],
    orientation='h',
    marker=dict(color=state_score['avg_score'], colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=False),
    hovertemplate='%{y}: %{x:.2f} ⭐<extra></extra>'))
fig.update_layout(**layout(title='Average Review Score by Customer State',
    xaxis_title='Avg Review Score', yaxis_title='State', margin=dict(t=40,r=20,b=60,l=50)))
save(fig, 'customer_review_by_state.json')

# Revenue by state bar instead of bubble
by_state_rev = by_state.sort_values('total_revenue', ascending=False).head(15)
fig = go.Figure(go.Bar(x=by_state_rev['customer_state'], y=by_state_rev['total_revenue'].round(0),
    marker=dict(color=by_state_rev['total_revenue'], colorscale=[[0,'#C8EAD3'],[1,'#2E6E55']],
                showscale=False),
    hovertemplate='%{x}<br>BRL %{y:,.0f}<extra></extra>'))
fig.update_layout(**layout(title='Total Revenue by Customer State (Top 15)',
    xaxis_title='State', yaxis_title='Revenue (BRL)'))
save(fig, 'customer_revenue_vs_orders.json')

print('\n-- Chapter 4: Seller Analysis --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_seller_analysis` ORDER BY total_revenue DESC")

top20 = df.head(20).copy()
top20['label'] = top20['seller_id'].str[:8] + '...'
top20 = top20.sort_values('total_revenue', ascending=True)
fig = go.Figure(go.Bar(x=top20['total_revenue'].round(0), y=top20['label'],
    orientation='h',
    marker=dict(color=top20['avg_review_score'],
                colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=True, colorbar=dict(title='Avg Score')),
    hovertemplate='%{y}<br>BRL %{x:,.0f}<extra></extra>'))
fig.update_layout(**layout(title='Top 20 Sellers by Revenue (coloured by review score)',
    xaxis_title='Revenue (BRL)', yaxis_title='Seller', margin=dict(t=40,r=80,b=60,l=90)))
save(fig, 'seller_top20_revenue.json')

by_state = df.groupby('seller_state').agg(
    seller_count=('seller_id','count'), total_revenue=('total_revenue','sum'),
    avg_score=('avg_review_score','mean')
).reset_index().sort_values('total_revenue', ascending=False)
fig = go.Figure(go.Bar(x=by_state['seller_state'], y=by_state['total_revenue'].round(0),
    marker=dict(color=by_state['seller_count'],
                colorscale=[[0,'#D0E8F2'],[1,'#2E7BA6']],
                showscale=True, colorbar=dict(title='Seller Count')),
    hovertemplate='%{x}<br>BRL %{y:,.0f}<extra></extra>'))
fig.update_layout(**layout(title='Total Revenue by Seller State (coloured by seller count)',
    xaxis_title='State', yaxis_title='Revenue (BRL)'))
save(fig, 'seller_revenue_by_state.json')

# Scatter: avg_review_score vs on_time_pct per seller state
state_perf = df.groupby('seller_state').agg(
    avg_score=('avg_review_score','mean'),
    on_time=('on_time_deliveries','sum'),
    late=('late_deliveries','sum'),
    total_rev=('total_revenue','sum')
).reset_index()
state_perf['on_time_pct'] = (state_perf['on_time'] / (state_perf['on_time'] + state_perf['late']) * 100).round(1)
fig = go.Figure(go.Scatter(
    x=state_perf['on_time_pct'], y=state_perf['avg_score'].round(2),
    mode='markers+text', text=state_perf['seller_state'],
    textposition='top center',
    marker=dict(size=10, color=LAVEND, line=dict(color='white', width=1)),
    hovertemplate='%{text}<br>On-Time: %{x:.1f}%<br>Score: %{y:.2f}<extra></extra>'
))
fig.update_layout(**layout(title='Review Score vs On-Time % by Seller State',
    xaxis_title='On-Time %', yaxis_title='Avg Review Score'))
save(fig, 'seller_score_vs_ontime.json')

by_state_sorted = by_state.sort_values('seller_count', ascending=True)
fig = go.Figure(go.Bar(x=by_state_sorted['seller_count'], y=by_state_sorted['seller_state'],
    orientation='h', marker_color=SKY,
    hovertemplate='%{y}: %{x} sellers<extra></extra>'))
fig.update_layout(**layout(title='Seller Count by State',
    xaxis_title='Number of Sellers', yaxis_title='State', margin=dict(t=40,r=20,b=60,l=50)))
save(fig, 'seller_state_distribution.json')

print('\n-- Chapter 5: Customer Churn --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_customer_churn`")

seg = df['customer_segment'].value_counts().reset_index()
seg.columns = ['segment','count']
colors_seg = [ROSE if s=='one_time' else YELLOW if s=='occasional' else MINT for s in seg['segment']]
fig = go.Figure(go.Bar(x=seg['count'], y=seg['segment'], orientation='h',
    marker_color=colors_seg,
    hovertemplate='%{y}: %{x:,} customers<extra></extra>'))
fig.update_layout(**layout(title='Customer Segments', xaxis_title='Customers', yaxis_title='Segment'))
save(fig, 'churn_segment_breakdown.json')

churn = df['churn_status'].value_counts().reset_index()
churn.columns = ['status','count']
colors_churn = [ROSE if s=='churned' else YELLOW if s=='at_risk' else MINT for s in churn['status']]
fig = go.Figure(go.Bar(x=churn['status'], y=churn['count'],
    marker_color=colors_churn,
    hovertemplate='%{x}: %{y:,} customers<extra></extra>'))
fig.update_layout(**layout(title='Customer Churn Status', xaxis_title='Status', yaxis_title='Customers'))
save(fig, 'churn_status_breakdown.json')

spend = df.groupby('customer_segment')['total_spend'].mean().reset_index()
spend.columns = ['segment','avg_spend']
colors_spend = [ROSE if s=='one_time' else YELLOW if s=='occasional' else MINT for s in spend['segment']]
fig = go.Figure(go.Bar(x=spend['segment'], y=spend['avg_spend'].round(2),
    marker_color=colors_spend,
    hovertemplate='%{x}<br>Avg BRL %{y:.2f}<extra></extra>'))
fig.update_layout(**layout(title='Average Total Spend by Segment (BRL)', xaxis_title='Segment', yaxis_title='Avg Spend (BRL)'))
save(fig, 'churn_spend_by_segment.json')

state_churn = df.groupby('customer_state').apply(
    lambda x: round((x['churn_status']=='churned').sum() / len(x) * 100, 1)
).reset_index()
state_churn.columns = ['state','churn_rate']
state_churn = state_churn.sort_values('churn_rate', ascending=True)
fig = go.Figure(go.Bar(x=state_churn['churn_rate'], y=state_churn['state'],
    orientation='h',
    marker=dict(color=state_churn['churn_rate'], colorscale=[[0,'#C8EAD3'],[0.5,'#F7E59B'],[1,'#F4A0A0']],
                showscale=False),
    hovertemplate='%{y}: %{x:.1f}% churned<extra></extra>'))
fig.update_layout(**layout(title='Customer Churn Rate by State (%)',
    xaxis_title='Churn Rate (%)', yaxis_title='State', margin=dict(t=40,r=20,b=60,l=50)))
save(fig, 'churn_rate_by_state.json')

print('\nAll 20 charts regenerated successfully! OK')
