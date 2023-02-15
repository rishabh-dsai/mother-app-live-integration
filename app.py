# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 14:12:12 2023

@author: asus
"""


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(page_title='Mother App Data Analysis',layout="wide",)


main=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='main')
live_birth=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='Details of each Live birth')
anc_visit=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='Enter the ANC visit details')
hbnc_visit=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='HBNC Details')
live_birth_2=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='Details of Live births')
last_2_preg_records=pd.read_excel("Mother App Data live_integ.xlsx",sheet_name='Last two Pregnancy Record Grou')



#%%

def lov_date_conv(dt):
    if type(dt)==str:
        string=dt[:-6]
        date= pd.to_datetime(string,format="%Y-%m-%d")
        return date
    else:
        return dt

def long_date_conv(dt):
    if type(dt)==str:
        string=dt[:10]
        date= pd.to_datetime(string,format="%Y-%m-%d")
        return date
    else:
        return dt
    
def quarter_div(date):
    mnth=date.month    
    year=date.year
    qtr=[(mnth-1)//3 if mnth>3 else 4][0]
    year=[year-1 if qtr==4 else year][0]
    year_qtr=str(year)+'-'+'Q'+str(qtr)
    
    return year_qtr

    
month_dict={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',
            9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

#%%
# Pre-processing and getting datasets:

# Death Sub-Datasets
maternal_death=main[main['Maternal Death']=="Yes"]
infant_death=live_birth_2[live_birth_2['HBNC Details.Details of Live births.Live Status Group.Is the child alive']=='No']


# Mothers registrations in stages of pregnancy:
main['Mother Details.date_created']=main['Mother Details.date_created'].apply(lambda z:long_date_conv(z))
main['Mother Details.date_created Qtr']=main['Mother Details.date_created'].apply(quarter_div)    
ts_reg=main.groupby(['Mother Details.date_created Qtr','Mother Details.Registered in Trimester'])['main_sno'].nunique().reset_index()
tri_trend=pd.pivot_table(ts_reg,index='Mother Details.date_created Qtr',columns='Mother Details.Registered in Trimester',
                         values='main_sno')


# Delivered mothers
delivered=main[main['Delivery.Delivery Timestamp LOV'].notnull()]


# Home deliveries
home_deliver=main[main['Delivery.Delivery Details.Actual Location of the Delivery']=='Home Delivery']

#Instituional Deliveries
phc_chc=main['Delivery.Delivery Details.Actual Location of the Delivery'].value_counts()['PHC/CHC']
sc=main['Delivery.Delivery Details.Actual Location of the Delivery'].value_counts()['Sub- Center']


# Delivery Location
main['Delivery.Delivery Details.Actual Date of Delivery']=main['Delivery.Delivery Details.Actual Date of Delivery'].apply(lambda z:long_date_conv(z))
main['Delivery.Delivery Details.Actual Date of Delivery Qtr']=main['Delivery.Delivery Details.Actual Date of Delivery'].apply(quarter_div) 
ts_reg=main.groupby(['Delivery.Delivery Details.Actual Date of Delivery Qtr','Delivery.Delivery Details.Actual Location of the Delivery'])['main_sno'].nunique().reset_index()
delivery_trend=pd.pivot_table(ts_reg,index='Delivery.Delivery Details.Actual Date of Delivery Qtr',columns='Delivery.Delivery Details.Actual Location of the Delivery',
                         values='main_sno')
delivery_trend['Total']=delivery_trend.sum(axis=1)
pct_delivery_trend=pd.DataFrame()
for j in delivery_trend.columns[:-1]:
    pct_delivery_trend[j]=(delivery_trend[j]/delivery_trend['Total'])*100


# Distance from delivery points
overall_dist=main['Parameters Programmes for Institutional Delivery.PID.What is the distance from her place to nearest delivery point   in Kilometres'].reset_index()
overall_dist.columns=['index_num','Distance from Mother Residence to Nearerst Delivery Point']


# Who conducted the delivery
ts_del=main.groupby(['Delivery.Delivery Details.Actual Date of Delivery Qtr','Delivery.Who conducted the Delivery'])['main_sno'].nunique().reset_index()
delivery_conducted_trend=pd.pivot_table(ts_del,index='Delivery.Delivery Details.Actual Date of Delivery Qtr',columns='Delivery.Who conducted the Delivery',
                         values='main_sno')
delivery_conducted_trend['Total']=delivery_conducted_trend.sum(axis=1)
pct_delivery_conducted_trend=pd.DataFrame()
for j in delivery_conducted_trend.columns[:-1]:
    pct_delivery_conducted_trend[j]=(delivery_conducted_trend[j]/delivery_conducted_trend['Total'])*100



# Scheme Utilization
main['Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp']=main['Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp'].apply(lambda z:long_date_conv(z))
main['Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp Qtr']=main['Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp'].apply(quarter_div)
ts_sch=main.groupby(['Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp Qtr','Parameters Programmes for Institutional Delivery.PID.Under which scheme is she enrolled'])['main_sno'].nunique().reset_index()
ts_sch.rename(columns={'Parameters Programmes for Institutional Delivery.Parameters Programs Timestamp Qtr':'Program Registration Qtr'},inplace=True)
scheme_trend=pd.pivot_table(ts_sch,index='Program Registration Qtr',columns='Parameters Programmes for Institutional Delivery.PID.Under which scheme is she enrolled',
                         values='main_sno')
scheme_trend['Total']=scheme_trend.sum(axis=1)
pct_scheme_trend=pd.DataFrame()
for j in scheme_trend.columns[:-1]:
    pct_scheme_trend[j]=(scheme_trend[j]/scheme_trend['Total'])*100



# Immunisation:
immune_df=live_birth['Delivery.Children Group.Details of each Live birth.Please select the immunization doses given to the newborn'].reset_index()
immune_df.columns=['index','Immunizations']

def immunization_finder(lst):
    all_doses=lst.split(",")
    hep_B=1 if "Hep B" in all_doses else 0
    opv=1 if "OPV" in all_doses else 0
    bcg=1 if "BCG" in all_doses else 0
    vit_k=1 if "Vit K" in all_doses else 0
        
    return hep_B,opv,bcg,vit_k
    
immune_df['Hep B']="Missing"
immune_df['OPV']="Missing"
immune_df['BCG']="Missing"
immune_df['Vit K']="Missing"


immune_df['Hep B']=immune_df['Immunizations'].apply(lambda d:immunization_finder(d)[0])
immune_df['OPV']=immune_df['Immunizations'].apply(lambda d:immunization_finder(d)[1])
immune_df['BCG']=immune_df['Immunizations'].apply(lambda d:immunization_finder(d)[2])
immune_df['Vit K']=immune_df['Immunizations'].apply(lambda d:immunization_finder(d)[3])

pct_immune_df=pd.DataFrame(columns=['Vaccine','Pct'])
num_new_borns=live_birth['Details of each Live birth_sno'].nunique()
hep_pct=np.round((immune_df["Hep B"].sum()/num_new_borns)*100,0)
opv_pct=np.round((immune_df["OPV"].sum()/num_new_borns)*100,0)
bcg_pct=np.round((immune_df["BCG"].sum()/num_new_borns)*100,0)
vit_pct=np.round((immune_df["Vit K"].sum()/num_new_borns)*100,0)


pct_immune_df['Vaccine']=['Hep B', 'OPV', 'BCG', 'Vit K']
pct_immune_df['Pct']=[hep_pct,opv_pct,bcg_pct,vit_pct]



#%%

# UI

# Basic Insights

st.markdown('<div style="text-align: center; font-size:30px; font-weight:bold">Basic Insights and Numbers</div>', unsafe_allow_html=True)
st.markdown("\n\n")
st.markdown("\n\n")
col1,col2,col3=st.columns(3)

with col1:
    st.metric('Number of Deliveries',delivered.shape[0])
    st.metric("Number of Home Deliveries",home_deliver.shape[0])
    st.metric("Number of Institutional Deliveries",phc_chc+sc)


with col2:    
    st.metric("Number of Mother Registrations in 1st Trimester",int(tri_trend.sum()['1st Trimester']))
    st.metric("Number of Mother Registrations in 2nd Trimester",int(tri_trend.sum()['2nd Trimester']))
    st.metric("Number of Mother Registrations in 3rd Trimester",int(tri_trend.sum()['3rd Trimester']))

    
with col3:
    st.metric("Maternal Deaths",maternal_death.shape[0])
    st.metric("Infant Deaths",infant_death.shape[0]) 
    st.metric("Number of High risk Pregnancies",main['High Risk Case'].value_counts()['Yes'])

#%%


# Graphs

with st.expander("The Location of Deliveries"):
    delivery_loc_trend=delivery_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    st.write("Number of deliveries at various locations:")
    st.dataframe(delivery_loc_trend,use_container_width=True)
    delivery_loc_trend_display=pct_delivery_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    delivery_loc_trend_display.reset_index(inplace=True)
    st.markdown("\n")
    delivery_loc_trend_display.columns=['Actual Date of Delivery Qtr','Pct Higher Facility','Pct Home Delivery', 'Pct PHC/CHC','Pct Sub- Center']
    bar_ch_sch=px.bar(delivery_loc_trend_display,x='Actual Date of Delivery Qtr',y=['Pct Higher Facility','Pct Home Delivery', 'Pct PHC/CHC','Pct Sub- Center'],
                        title="FY Quarterly Trend- Pct of Deliveries",text_auto=True)
    st.plotly_chart(bar_ch_sch,use_container_width=True)
    st.markdown("\n")      
    st.subheader("Distance to Nearest Delivery Point for Mothers")
    fig = px.histogram(overall_dist['Distance from Mother Residence to Nearerst Delivery Point'].dropna(),nbins=7,text_auto=True) 
    st.plotly_chart(fig,use_container_width=True)
    
with st.expander("The Professional who conducted the Delivery"):
    delivery_prof=delivery_conducted_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    st.dataframe(delivery_prof,use_container_width=True)
    delivery_prof_display=pct_delivery_conducted_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    delivery_prof_display.reset_index(inplace=True)
    delivery_prof_display.columns=['Actual Date of Delivery Qtr','Pct ANM', 'Pct Dai', 'Pct Dai - Skilled Birth Attendant','Pct Dai - Unskilled Birth Attendant', 'Pct Medical Officer','Pct Others', 'Pct Staff Nurse']
    bar_ch_sch=px.bar(delivery_prof_display,x='Actual Date of Delivery Qtr',y=['Pct ANM', 'Pct Dai', 'Pct Dai - Skilled Birth Attendant','Pct Dai - Unskilled Birth Attendant', 'Pct Medical Officer','Pct Others', 'Pct Staff Nurse'],
                        title="FY Quarterly Trend- Person performing  delivery",text_auto=True)
    st.plotly_chart(bar_ch_sch,use_container_width=True)
    


with st.expander("Trend for Mothers who are enrolled in Govt. Schemes"):
    scheme_enrol_trend=scheme_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    st.dataframe(scheme_enrol_trend,use_container_width=True)
    scheme_enrol_trend_display=pct_scheme_trend.fillna(0).applymap(lambda z:int(np.round(z)))
    scheme_enrol_trend_display.reset_index(inplace=True)
    scheme_enrol_trend_display.columns=['Program Registration Qtr','Pct JSY & JSSK', 'Pct PMMVY', 'Pct Neither']
    bar_ch_sch=px.bar(scheme_enrol_trend_display,x='Program Registration Qtr',y=['Pct JSY & JSSK', 'Pct PMMVY', 'Pct Neither'],
                        title="FY Quarterly Trend- Mothers registering for Govt. Schemes",text_auto=True)
    st.plotly_chart(bar_ch_sch,use_container_width=True)


with st.expander("Immunization of New-borns"):
    bar_immun=px.bar(pct_immune_df,x='Vaccine',y='Pct',text_auto=True)
    st.plotly_chart(bar_immun,use_container_width=True)


#%%

st.markdown("\n")
st.caption("Please Note: All analyses have been done on the dataset received from Health Dept. Meghalaya.")
st.header("")
st.markdown('<div style="text-align: center; font-size:16px;">&#169 Copyright 2022 DSAI</div>', unsafe_allow_html=True)
st.markdown("\n")










