"""
Regenerate all chart JSON files from BigQuery.
Polished, annotated, full-width charts with consistent dark styling.
Run from the project root: python scripts/regenerate_charts.py
"""
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from google.cloud import bigquery
from google.oauth2 import service_account

pio.json.config.default_engine = 'json'

# ── Setup ────────────────────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_root, '.env'))
project_id  = os.getenv('GCP_PROJECT_ID')
creds_path  = os.path.join(project_root, os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
client      = bigquery.Client(
    credentials=service_account.Credentials.from_service_account_file(creds_path),
    project=project_id)
OUT = os.path.join(project_root, 'outputs')
os.makedirs(OUT, exist_ok=True)

def bq(sql): return client.query(sql).to_dataframe()
def save(fig, name):
    with open(os.path.join(OUT, name), 'w') as f: f.write(fig.to_json())
    print(f'  saved {name}')

# ── Colour palette ────────────────────────────────────────────────────────────
SKY    = '#93C6E7'
MINT   = '#A8D5B5'
PEACH  = '#F4C89E'
LAVEND = '#C9B8E8'
ROSE   = '#F4A0A0'
TEAL   = '#8EC5C4'
YELLOW = '#F7E59B'

# Grid / axis colours for the transparent dark background
GRID  = 'rgba(255,255,255,0.06)'
ZERO  = 'rgba(255,255,255,0.10)'
TICK  = '#8b949e'
TEXT  = '#e6edf3'
FONT  = 'Inter, system-ui, sans-serif'

def base_layout(height=480, **kw):
    d = dict(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT, family=FONT, size=12),
        margin=dict(t=50, r=24, b=60, l=70),
        xaxis=dict(gridcolor=GRID, zerolinecolor=ZERO,
                   tickfont=dict(size=11, color=TICK), linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=ZERO,
                   tickfont=dict(size=11, color=TICK), linecolor=GRID),
        hoverlabel=dict(bgcolor='#21262d', bordercolor='rgba(255,255,255,0.15)',
                        font=dict(color=TEXT, size=12)),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=TICK, size=11)),
        hovermode='x unified',
    )
    d.update(kw)
    return d

def ann(x, y, text, ax=0, ay=-36, color=TEXT):
    return dict(x=x, y=y, text=text, showarrow=True,
                arrowhead=2, arrowwidth=1.5, arrowcolor=color,
                ax=ax, ay=ay, font=dict(size=11, color=color),
                bgcolor='rgba(33,38,45,0.85)', bordercolor=color,
                borderwidth=1, borderpad=5)

# ════════════════════════════════════════════════════════════════════
print('\n-- Chapter 1: Sales & Revenue --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_sales_revenue` ORDER BY year_month")

# 1a  Revenue area chart (HERO)
peak_idx = df['total_revenue'].idxmax()
peak_mon = df.loc[peak_idx, 'year_month']
peak_val = df.loc[peak_idx, 'total_revenue']

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['year_month'], y=df['total_revenue'].round(0),
    mode='lines', name='Revenue',
    line=dict(color=MINT, width=3),
    fill='tozeroy', fillcolor='rgba(168,213,181,0.12)',
    hovertemplate='%{x}<br><b>BRL %{y:,.0f}</b><extra></extra>'))
fig.add_annotation(**ann(peak_mon, peak_val,
    f'Peak: BRL {peak_val:,.0f}<br>Black Friday 2017', ay=-50, color=MINT))
fig.update_layout(**base_layout(height=420,
    xaxis_title='Month', yaxis_title='Revenue (BRL)',
    yaxis_tickformat=',.0f', hovermode='x unified'))
save(fig, 'sales_monthly_revenue.json')

# 1b  Orders + sellers dual axis
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['year_month'], y=df['total_orders'],
    name='Orders', marker_color=SKY, opacity=0.85,
    hovertemplate='%{x}<br><b>%{y:,} orders</b><extra></extra>'))
fig.add_trace(go.Scatter(
    x=df['year_month'], y=df['active_sellers'],
    name='Active Sellers', mode='lines+markers',
    line=dict(color=PEACH, width=2.5), marker=dict(size=5),
    yaxis='y2',
    hovertemplate='%{x}<br><b>%{y} sellers</b><extra></extra>'))
fig.update_layout(**base_layout(height=400,
    xaxis_title='Month',
    yaxis=dict(title='Monthly Orders', gridcolor=GRID, zerolinecolor=ZERO,
               tickfont=dict(size=11, color=TICK), tickformat=','),
    yaxis2=dict(title='Active Sellers', overlaying='y', side='right',
                gridcolor='rgba(0,0,0,0)', tickfont=dict(size=11, color=TICK)),
    legend=dict(orientation='h', x=0, y=1.08),
    hovermode='x unified'))
save(fig, 'sales_monthly_orders.json')

# 1c  AOV line with bands
fig = go.Figure()
avg_aov = df['avg_order_value'].mean()
fig.add_hline(y=avg_aov, line_dash='dash', line_color='rgba(255,255,255,0.2)',
              annotation_text=f'Avg BRL {avg_aov:.0f}',
              annotation_font_color=TICK, annotation_position='bottom right')
fig.add_trace(go.Scatter(
    x=df['year_month'], y=df['avg_order_value'].round(2),
    mode='lines+markers', name='Avg Order Value',
    line=dict(color=PEACH, width=3), marker=dict(size=5, color=PEACH),
    fill='tozeroy', fillcolor='rgba(244,200,158,0.08)',
    hovertemplate='%{x}<br><b>BRL %{y:.2f}</b><extra></extra>'))
fig.update_layout(**base_layout(height=380,
    xaxis_title='Month', yaxis_title='Avg Order Value (BRL)',
    yaxis_tickprefix='BRL ', hovermode='x unified'))
save(fig, 'sales_avg_order_value.json')

# 1d  Orders heatmap by month x year
df['year']  = df['year'].astype(int)
df['month'] = df['month'].astype(int)
pivot = df.pivot_table(index='month', columns='year', values='total_orders', fill_value=0)
month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig = go.Figure(go.Heatmap(
    z=pivot.values,
    x=[str(c) for c in pivot.columns],
    y=[month_names[m-1] for m in pivot.index],
    colorscale=[[0,'#0d1117'],[0.3,'#1f4068'],[0.7,SKY],[1,MINT]],
    hovertemplate='Year %{x} · %{y}<br><b>%{z:,} orders</b><extra></extra>',
    showscale=True,
    colorbar=dict(tickfont=dict(color=TICK), title=dict(text='Orders', font=dict(color=TICK)))))
fig.update_layout(**base_layout(height=380,
    xaxis_title='Year', yaxis_title='Month',
    hovermode='closest', margin=dict(t=30,r=80,b=50,l=60)))
save(fig, 'sales_active_sellers.json')


# ════════════════════════════════════════════════════════════════════
print('\n-- Chapter 2: Delivery Performance --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_delivery_performance`")
state = df.groupby('seller_state').agg(
    on_time=('on_time_deliveries','sum'), late=('late_deliveries','sum'),
    avg_days=('avg_delivery_days','mean'), avg_score=('avg_review_score','mean')
).reset_index()
state['on_time_pct'] = (state['on_time'] / (state['on_time'] + state['late']) * 100).round(1)
state = state.sort_values('on_time_pct', ascending=True)

# 2a  On-time horizontal bar (HERO)
fig = go.Figure(go.Bar(
    x=state['on_time_pct'], y=state['seller_state'],
    orientation='h',
    marker=dict(
        color=state['on_time_pct'],
        colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
        showscale=True,
        colorbar=dict(title=dict(text='On-Time %', font=dict(color=TICK)),
                      tickfont=dict(color=TICK), x=1.02)),
    text=state['on_time_pct'].apply(lambda x: f'{x:.1f}%'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}<br><b>%{x:.1f}% on time</b><extra></extra>'))
nat_avg = state['on_time_pct'].mean()
fig.add_vline(x=nat_avg, line_dash='dash', line_color='rgba(255,255,255,0.3)',
              annotation_text=f'Avg {nat_avg:.1f}%',
              annotation_font_color=TICK)
fig.update_layout(**base_layout(height=580,
    xaxis_title='On-Time Delivery %', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=100,b=50,l=55)))
save(fig, 'delivery_on_time_by_state.json')

# 2b  Avg delivery days bar
state_days = state.sort_values('avg_days', ascending=False)
fig = go.Figure(go.Bar(
    x=state_days['seller_state'], y=state_days['avg_days'].round(1),
    marker=dict(color=state_days['avg_days'],
                colorscale=[[0,MINT],[0.5,YELLOW],[1,ROSE]],
                showscale=False),
    text=state_days['avg_days'].round(1),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{x}<br><b>%{y:.1f} days</b><extra></extra>'))
fig.add_hline(y=state_days['avg_days'].mean(), line_dash='dot',
              line_color='rgba(255,255,255,0.25)',
              annotation_text=f"Avg {state_days['avg_days'].mean():.1f}d",
              annotation_font_color=TICK)
fig.update_layout(**base_layout(height=400,
    xaxis_title='Seller State', yaxis_title='Avg Delivery Days', hovermode='closest'))
save(fig, 'delivery_avg_days_by_state.json')

# 2c  Monthly on-time trend
monthly = df.groupby('year_month').agg(
    on_time=('on_time_deliveries','sum'), late=('late_deliveries','sum')).reset_index()
monthly['on_time_pct'] = (monthly['on_time']/(monthly['on_time']+monthly['late'])*100).round(1)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=monthly['year_month'], y=monthly['on_time_pct'],
    mode='lines+markers', name='On-Time %',
    line=dict(color=TEAL, width=3), marker=dict(size=6, color=TEAL),
    fill='tozeroy', fillcolor='rgba(142,197,196,0.10)',
    hovertemplate='%{x}<br><b>%{y:.1f}% on time</b><extra></extra>'))
fig.update_layout(**base_layout(height=380,
    xaxis_title='Month', yaxis_title='On-Time Rate (%)', hovermode='x unified'))
save(fig, 'delivery_monthly_trend.json')

# 2d  Score vs on-time scatter
fig = go.Figure(go.Scatter(
    x=state['on_time_pct'], y=state['avg_score'].round(2),
    mode='markers+text',
    text=state['seller_state'], textposition='top center',
    textfont=dict(size=10, color=TICK),
    marker=dict(size=12, color=state['avg_score'],
                colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=True, line=dict(color='rgba(255,255,255,0.2)', width=1),
                colorbar=dict(title=dict(text='Score', font=dict(color=TICK)),
                              tickfont=dict(color=TICK))),
    hovertemplate='<b>%{text}</b><br>On-Time: %{x:.1f}%<br>Score: %{y:.2f}<extra></extra>'))
fig.update_layout(**base_layout(height=420,
    xaxis_title='On-Time Delivery %', yaxis_title='Avg Review Score',
    hovermode='closest', margin=dict(t=30,r=100,b=60,l=70)))
save(fig, 'delivery_score_vs_ontime.json')


# ════════════════════════════════════════════════════════════════════
print('\n-- Chapter 3: Customer Behaviour --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_customer_behaviour`")
by_state = df.groupby('customer_state').agg(
    total_orders=('total_orders','sum'), total_revenue=('total_revenue','sum'),
    total_customers=('total_customers','sum'), avg_score=('avg_review_score','mean')
).reset_index().sort_values('total_orders', ascending=False)

# 3a  Orders by state (HERO) — horizontal for readability
bs = by_state.sort_values('total_orders', ascending=True)
fig = go.Figure(go.Bar(
    x=bs['total_orders'], y=bs['customer_state'],
    orientation='h',
    marker=dict(color=bs['total_orders'],
                colorscale=[[0,'#1f4068'],[0.5,SKY],[1,MINT]],
                showscale=False),
    text=bs['total_orders'].apply(lambda x: f'{x:,}'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}<br><b>%{x:,} orders</b><extra></extra>'))
fig.update_layout(**base_layout(height=560,
    xaxis_title='Total Orders', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=80,b=50,l=50)))
save(fig, 'customer_orders_by_state.json')

# 3b  Top 15 cities
top_cities = df.groupby('customer_city').agg(
    total_orders=('total_orders','sum')).reset_index()\
    .sort_values('total_orders', ascending=False).head(15)\
    .sort_values('total_orders', ascending=True)
fig = go.Figure(go.Bar(
    x=top_cities['total_orders'], y=top_cities['customer_city'],
    orientation='h', marker_color=TEAL,
    text=top_cities['total_orders'].apply(lambda x: f'{x:,}'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}<br><b>%{x:,} orders</b><extra></extra>'))
fig.update_layout(**base_layout(height=460,
    xaxis_title='Total Orders', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=80,b=50,l=120)))
save(fig, 'customer_top_cities.json')

# 3c  Review score by state
state_sc = by_state.sort_values('avg_score', ascending=True)
fig = go.Figure(go.Bar(
    x=state_sc['avg_score'].round(2), y=state_sc['customer_state'],
    orientation='h',
    marker=dict(color=state_sc['avg_score'],
                colorscale=[[0,ROSE],[0.4,YELLOW],[1,MINT]],
                showscale=True,
                colorbar=dict(title=dict(text='Score', font=dict(color=TICK)),
                              tickfont=dict(color=TICK), x=1.02)),
    text=state_sc['avg_score'].round(2),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}<br><b>%{x:.2f} stars</b><extra></extra>'))
fig.update_layout(**base_layout(height=560,
    xaxis_title='Avg Review Score', yaxis_title='',
    xaxis_range=[3.5, 4.5],
    hovermode='closest', margin=dict(t=30,r=100,b=50,l=55)))
save(fig, 'customer_review_by_state.json')

# 3d  Revenue by state bar
rev_state = by_state.sort_values('total_revenue', ascending=False).head(12)
fig = go.Figure(go.Bar(
    x=rev_state['customer_state'], y=rev_state['total_revenue'].round(0),
    marker=dict(color=rev_state['total_revenue'],
                colorscale=[[0,'#1f4068'],[0.5,SKY],[1,MINT]],
                showscale=False),
    text=rev_state['total_revenue'].apply(lambda x: f'BRL {x/1e6:.1f}M'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{x}<br><b>BRL %{y:,.0f}</b><extra></extra>'))
fig.update_layout(**base_layout(height=400,
    xaxis_title='State', yaxis_title='Total Revenue (BRL)',
    yaxis_tickformat=',.0f', hovermode='closest'))
save(fig, 'customer_revenue_vs_orders.json')


# ════════════════════════════════════════════════════════════════════
print('\n-- Chapter 4: Seller Analysis --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_seller_analysis` ORDER BY total_revenue DESC")

# 4a  Top 20 sellers (HERO)
top20 = df.head(20).copy().sort_values('total_revenue', ascending=True)
top20['label'] = top20['seller_id'].str[:8] + '...'
fig = go.Figure(go.Bar(
    x=top20['total_revenue'].round(0), y=top20['label'],
    orientation='h',
    marker=dict(color=top20['avg_review_score'],
                colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=True,
                colorbar=dict(title=dict(text='Avg Review', font=dict(color=TICK)),
                              tickfont=dict(color=TICK), x=1.02)),
    text=top20['total_revenue'].apply(lambda x: f'BRL {x:,.0f}'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='<b>%{y}</b><br>Revenue: BRL %{x:,.0f}<extra></extra>'))
fig.update_layout(**base_layout(height=560,
    xaxis_title='Total Revenue (BRL)', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=120,b=50,l=100)))
save(fig, 'seller_top20_revenue.json')

# 4b  Revenue by state
by_state_s = df.groupby('seller_state').agg(
    seller_count=('seller_id','count'),
    total_revenue=('total_revenue','sum'),
    avg_score=('avg_review_score','mean')
).reset_index().sort_values('total_revenue', ascending=False)
fig = go.Figure(go.Bar(
    x=by_state_s['seller_state'], y=by_state_s['total_revenue'].round(0),
    marker=dict(color=by_state_s['seller_count'],
                colorscale=[[0,'#1f4068'],[0.5,LAVEND],[1,'#a5b4fc']],
                showscale=True,
                colorbar=dict(title=dict(text='Sellers', font=dict(color=TICK)),
                              tickfont=dict(color=TICK))),
    text=by_state_s['total_revenue'].apply(lambda x: f'BRL {x/1e6:.1f}M'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{x}<br>Revenue: BRL %{y:,.0f}<extra></extra>'))
fig.update_layout(**base_layout(height=420,
    xaxis_title='State', yaxis_title='Total Revenue (BRL)',
    yaxis_tickformat=',.0f', hovermode='closest'))
save(fig, 'seller_revenue_by_state.json')

# 4c  Score vs on-time by state scatter
sp = df.groupby('seller_state').agg(
    avg_score=('avg_review_score','mean'),
    on_time=('on_time_deliveries','sum'),
    late=('late_deliveries','sum'),
    total_rev=('total_revenue','sum')
).reset_index()
sp['on_time_pct'] = (sp['on_time'] / (sp['on_time']+sp['late'])*100).round(1)
fig = go.Figure(go.Scatter(
    x=sp['on_time_pct'], y=sp['avg_score'].round(2),
    mode='markers+text',
    text=sp['seller_state'], textposition='top center',
    textfont=dict(size=10, color=TICK),
    marker=dict(size=sp['total_rev']/sp['total_rev'].max()*40+8,
                color=sp['avg_score'],
                colorscale=[[0,ROSE],[0.5,YELLOW],[1,MINT]],
                showscale=True, line=dict(color='rgba(255,255,255,0.15)', width=1),
                colorbar=dict(title=dict(text='Score', font=dict(color=TICK)),
                              tickfont=dict(color=TICK))),
    hovertemplate='<b>%{text}</b><br>On-Time: %{x:.1f}%<br>Score: %{y:.2f}<extra></extra>'))
fig.update_layout(**base_layout(height=440,
    xaxis_title='On-Time Delivery %', yaxis_title='Avg Review Score',
    hovermode='closest', margin=dict(t=30,r=110,b=60,l=70)))
save(fig, 'seller_score_vs_ontime.json')

# 4d  Seller count by state
by_state_cnt = by_state_s.sort_values('seller_count', ascending=True)
fig = go.Figure(go.Bar(
    x=by_state_cnt['seller_count'], y=by_state_cnt['seller_state'],
    orientation='h',
    marker=dict(color=by_state_cnt['seller_count'],
                colorscale=[[0,'#1f4068'],[0.5,LAVEND],[1,'#a5b4fc']],
                showscale=False),
    text=by_state_cnt['seller_count'],
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}: <b>%{x} sellers</b><extra></extra>'))
fig.update_layout(**base_layout(height=560,
    xaxis_title='Number of Sellers', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=60,b=50,l=50)))
save(fig, 'seller_state_distribution.json')


# ════════════════════════════════════════════════════════════════════
print('\n-- Chapter 5: Customer Churn --')
df = bq(f"SELECT * FROM `{project_id}.olist_raw.mart_customer_churn`")

# 5a  Segment funnel-style bar (HERO)
seg = df['customer_segment'].value_counts().reset_index()
seg.columns = ['segment','count']
seg_order = {'one_time':0,'occasional':1,'loyal':2}
seg = seg.sort_values('segment', key=lambda x: x.map(seg_order))
seg['pct'] = (seg['count']/seg['count'].sum()*100).round(1)
colors_seg = [ROSE, YELLOW, MINT]
fig = go.Figure()
for i, row in seg.iterrows():
    fig.add_trace(go.Bar(
        x=[row['count']], y=[row['segment']],
        orientation='h', name=row['segment'],
        marker_color=colors_seg[seg_order[row['segment']]],
        text=f"{row['pct']:.1f}%  ({row['count']:,})",
        textposition='outside', textfont=dict(size=13, color=TEXT),
        hovertemplate=f"<b>{row['segment']}</b><br>{row['count']:,} customers ({row['pct']:.1f}%)<extra></extra>"))
fig.update_layout(**base_layout(height=300,
    xaxis_title='Number of Customers', yaxis_title='',
    barmode='group', showlegend=False,
    hovermode='closest', margin=dict(t=20,r=160,b=50,l=90)))
save(fig, 'churn_segment_breakdown.json')

# 5b  Churn status grouped bar
churn_seg = df.groupby(['customer_segment','churn_status']).size().reset_index(name='count')
seg_order_l = ['one_time','occasional','loyal']
status_colors = {'churned': ROSE, 'at_risk': YELLOW, 'active': MINT}
fig = go.Figure()
for status, color in status_colors.items():
    sub = churn_seg[churn_seg['churn_status']==status]
    sub = sub.set_index('customer_segment').reindex(seg_order_l).reset_index()
    fig.add_trace(go.Bar(
        x=sub['customer_segment'], y=sub['count'],
        name=status.replace('_',' ').title(),
        marker_color=color,
        hovertemplate=f'%{{x}}<br><b>{status}: %{{y:,}}</b><extra></extra>'))
fig.update_layout(**base_layout(height=400,
    xaxis_title='Customer Segment', yaxis_title='Customers',
    barmode='group', yaxis_tickformat=',',
    legend=dict(orientation='h', x=0, y=1.08),
    hovermode='x unified'))
save(fig, 'churn_status_breakdown.json')

# 5c  Avg spend by segment
spend = df.groupby('customer_segment')['total_spend'].agg(['mean','median','count']).reset_index()
spend.columns = ['segment','avg_spend','median_spend','count']
spend = spend.sort_values('segment', key=lambda x: x.map(seg_order))
spend_colors = [ROSE, YELLOW, MINT]
fig = go.Figure()
fig.add_trace(go.Bar(
    x=spend['segment'], y=spend['avg_spend'].round(2),
    name='Avg Spend', marker_color=[spend_colors[seg_order[s]] for s in spend['segment']],
    text=spend['avg_spend'].apply(lambda x: f'BRL {x:.0f}'),
    textposition='outside', textfont=dict(color=TEXT, size=12),
    hovertemplate='%{x}<br>Avg: <b>BRL %{y:.2f}</b><extra></extra>'))
fig.update_layout(**base_layout(height=380,
    xaxis_title='Customer Segment', yaxis_title='Avg Total Spend (BRL)',
    showlegend=False, hovermode='closest'))
save(fig, 'churn_spend_by_segment.json')

# 5d  Churn rate by state
state_churn = df.groupby('customer_state').apply(
    lambda x: pd.Series({
        'total': len(x),
        'churned': (x['churn_status']=='churned').sum()
    }), include_groups=False).reset_index()
state_churn['churn_rate'] = (state_churn['churned']/state_churn['total']*100).round(1)
state_churn = state_churn.sort_values('churn_rate', ascending=True)
fig = go.Figure(go.Bar(
    x=state_churn['churn_rate'], y=state_churn['customer_state'],
    orientation='h',
    marker=dict(color=state_churn['churn_rate'],
                colorscale=[[0,MINT],[0.5,YELLOW],[1,ROSE]],
                showscale=True,
                colorbar=dict(title=dict(text='Churn %', font=dict(color=TICK)),
                              tickfont=dict(color=TICK), x=1.02)),
    text=state_churn['churn_rate'].apply(lambda x: f'{x:.1f}%'),
    textposition='outside', textfont=dict(color=TICK, size=10),
    hovertemplate='%{y}<br><b>%{x:.1f}% churned</b><extra></extra>'))
avg_churn = state_churn['churn_rate'].mean()
fig.add_vline(x=avg_churn, line_dash='dash', line_color='rgba(255,255,255,0.25)',
              annotation_text=f'Avg {avg_churn:.1f}%', annotation_font_color=TICK)
fig.update_layout(**base_layout(height=580,
    xaxis_title='Churn Rate (%)', yaxis_title='',
    hovermode='closest', margin=dict(t=30,r=100,b=50,l=55)))
save(fig, 'churn_rate_by_state.json')

print('\nAll charts regenerated successfully!')
