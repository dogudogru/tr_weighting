import streamlit as st
import pandas as pd
import numpy as np
import base64

from streamlit.uploaded_file_manager import UploadedFile

st.set_page_config(layout='wide')

#Menü gizleme
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: url("bg.png");
#         background-repeat:no-repeat;
#         background-size: 100px
#     }
#    .sidebar .sidebar-content {
#         background-image: linear-gradient(#2e7bcf,#2e7bcf);
#         color: yellow;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

main_bg = "bg.png"
main_bg_ext = "png"

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
        background-repeat: no-repeat;
        background-position: right top;
        background-size: 300px;
    }}
    .sidebar.sidebar-content {{
        background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()})
    }}
    </style>
    """,
    unsafe_allow_html=True
)






@st.cache

def convert_df(df):

     return df.to_csv().encode('utf-8')

def main():
    cs_sidebar()
    cs_main_calc()
    cs_text()

def cs_sidebar():
    
    

    return None

st.title('Türkiye Raporu - Anket Verisi Ağırlıklandırma')

uploaded_file = st.sidebar.file_uploader("Anket verisini yükleyin",type=['xlsx'],accept_multiple_files=False,key="fileUploader")

def cs_main_calc():

    

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)

        df['educ_realprct'] = df['educ']
        df['educ_real'] = df['educ']
        df['2018_party_real'] = df['2018_party']   

        sex_pop = pd.DataFrame({'sex':['Kadın','Erkek'], 'sex_weight':[0.501716178,0.498283822]})
        age_pop = pd.DataFrame({'age':['18-24','25-34','35-44','45-54','55-64','65 ve üstü'], 'age_weight':[0.155496,0.211942377,0.210170714,0.169884995,0.129716679,0.122789]})
        educ_pop = pd.DataFrame({'educ':['Okuma-yazma bilmiyor','İlkokul terk','İlkokul mezunu','Ortaokul veya dengi meslek ortaokul mezunu','Lise ve dengi meslek okulu mezunu','Yüksekokul veya üniversite mezunu','Yüksek lisans','Doktora'], 'educ_weight':[0.276159321,0.276159321,0.276159321,0.535093254,0.535093254,0.188747425,0.188747425,0.188747425]})
        party_pop = pd.DataFrame({'2018_party':['Adalet ve Kalkınma Partisi (AKP)','Cumhuriyet Halk Partisi (CHP)','Diğer','Halkların Demokratik Partisi (HDP)','İYİ Parti','Milliyetçi Hareket Partisi (MHP)','Oy kullanmadım < 21','Saadet Partisi','Bağımsız aday','Oy kullanmadım > 20'], 'party_weight':[0.339423446488676,0.180605171173664,0.00430128656841585,0.0933281090097647,0.0794286628590058,0.0885248140019761,0.0556726723005184,0.0106913640821138,0.0012030069160252,0.14682146659984]})

        df['all'] = len(df['sex']) # Toplam katilimci sayisini belirten kolon

        df['count_sex'] = (df.groupby('sex')['sex'].transform('count')) #Cinsiyet kirilimli sayim
        df['count_age'] = (df.groupby('age')['age'].transform('count')) #Yas kirilimli sayim
        df['count_educ']= (df.groupby('educ')['educ'].transform('count')) #Egitim kirilimli sayim

        df['sex_prct'] = df['count_sex']  / df['all'] #Orneklem dagilimini buluyorum
        df['age_prct'] = df['count_age']  / df['all'] #Orneklem dagilimini buluyorum
        df['educ_prct']= df['count_educ'] / df['all'] #Orneklem dagilimini buluyorum

        df = df.merge(sex_pop, on='sex', how= 'left') #Populasyon bilgilerini bagliyorum 
        df = df.merge(age_pop, on='age', how= 'left') #Populasyon bilgilerini bagliyorum
        df = df.merge(educ_pop, on='educ', how = 'left') #Populasyon bilgilerini bagliyorum
        df = df.merge(party_pop, on='2018_party', how = 'left') #Populasyon bilgilerini bagliyorum


        df['educ_realprct']= df['educ_realprct'].replace({'Okuma-yazma bilmiyor': 'ilk', 
                                        'İlkokul terk': 'ilk',
                                        'İlkokul mezunu': 'ilk',
                                        'Ortaokul veya dengi meslek ortaokul mezunu': 'orta_lise',
                                        'Lise ve dengi meslek okulu mezunu': 'orta_lise',
                                        'Yüksekokul veya üniversite mezunu': 'uni',
                                        'Yüksek lisans': 'uni',
                                        'Doktora': 'uni',
                                        })

        df['educ_real']= df['educ_real'].replace({'Okuma-yazma bilmiyor': 'İlköğretim veya daha az', 
                                        'İlkokul terk': 'İlköğretim veya daha az',
                                        'İlkokul mezunu': 'İlköğretim veya daha az',
                                        'Ortaokul veya dengi meslek ortaokul mezunu': 'Ortaokul',
                                        'Lise ve dengi meslek okulu mezunu': 'Lise',
                                        'Yüksekokul veya üniversite mezunu': 'Üniversite veya daha fazla',
                                        'Yüksek lisans': 'Üniversite veya daha fazla',
                                        'Doktora': 'Üniversite veya daha fazla',
                                        })

        #burada agirliklandirma icin kullanacagimiz birlestirilmis egitim gruplarini olusturuyorum

        ed_a = df.loc[df['educ'] == 'Okuma-yazma bilmiyor', 'educ_prct'].iloc[0]
        ed_b = df.loc[df['educ'] == 'İlkokul terk', 'educ_prct'].iloc[0]
        ed_c = df.loc[df['educ'] == 'İlkokul mezunu', 'educ_prct'].iloc[0]
        ed_d = df.loc[df['educ'] == 'Ortaokul veya dengi meslek ortaokul mezunu', 'educ_prct'].iloc[0]
        ed_e = df.loc[df['educ'] == 'Lise ve dengi meslek okulu mezunu', 'educ_prct'].iloc[0]
        ed_f = df.loc[df['educ'] == 'Yüksekokul veya üniversite mezunu', 'educ_prct'].iloc[0]
        ed_g = df.loc[df['educ'] == 'Yüksek lisans', 'educ_prct'].iloc[0]
        ed_h = df.loc[df['educ'] == 'Doktora', 'educ_prct'].iloc[0]

        ed_ilk = ed_a + ed_b + ed_c
        ed_orta_lise = ed_d + ed_e
        ed_uni = ed_f + ed_g + ed_h

        df['educ_realprct'] = df['educ_realprct'].replace('ilk',ed_ilk).replace('orta_lise',ed_orta_lise).replace('uni',ed_uni)


        df['w_sex'] =  df['sex_weight'] /  df['sex_prct']
        df['w_age'] = df['age_weight']  / df['age_prct'] 
        df['w_educ'] = df['educ_weight'] / df['educ_realprct']  #educ_prct yerine educ_realprct kullandigimiz yer

        df['total'] = df['w_sex'] * df['w_age'] * df['w_educ'] 

        df['std'] = df.loc[:,"total"].std(ddof=1)
        df['avg'] = df.loc[:,"total"].mean()
        df['thold'] = df['std'] * 2 + df['avg']
        df = df.drop(columns=['std', 'avg'])

        calc = np.where(df['total'] > df['thold'], df['thold'], df['total'])
        df['ilk_agirliklar'] = calc

        party_pivot = pd.pivot_table(df,
                                    index='2018_party',
                                    values='ilk_agirliklar',
                                    aggfunc=np.sum).reset_index()

        # party_pivot = party_pivot.columns.get_level_values(0)

        party_pivot = party_pivot.rename({'ilk_agirliklar': 'first_party_weight'}, axis=1)

        party_pivot['all'] = df['ilk_agirliklar'].sum()
        
        party_pivot['party_prct'] = party_pivot['first_party_weight']  / party_pivot['all']

        df = df.merge(party_pivot, on='2018_party', how= 'left')

        df['w_party'] =  df['party_weight'] / df['party_prct'] 

        df['total2'] = df['w_party'] * df['ilk_agirliklar']

        df['std2'] = df.loc[:,"total2"].std(ddof=1)
        df['avg2'] = df.loc[:,"total2"].mean()
        df['thold2'] = df['std2'] * 2 + df['avg2']
        df = df.drop(columns=['std2', 'avg2'])

        calc2 = np.where(df['total2'] > df['thold2'], df['thold2'], df['total2'])
        df['Duzeltilmis_Agirlik'] = calc2

        min_weight = df['Duzeltilmis_Agirlik'].min()
        max_weight = df['Duzeltilmis_Agirlik'].max()
        std_weight = df['Duzeltilmis_Agirlik'].std() 
        mean_weight = df['Duzeltilmis_Agirlik'].mean()

        dataframe_x = pd.DataFrame({
                'Ağırlık Özeti': ["Minimum Ağırlık", "Maksimum Ağırlık", "Standart Sapma", "Ortalama Ağırlık"],
                '': [min_weight, max_weight, std_weight, mean_weight],
            })
        dataframe_x.set_index('Ağırlık Özeti')

        st.markdown("""---""")

        st.write("Minimum ağırlık",round(min_weight,3))
        st.write("Maksimum ağırlık",round(max_weight,3))
        st.write("Örneklem Standart Sapması",round(std_weight,3))
        st.write("Ortalama Ağırlık",round(mean_weight,3))

        st.markdown("""---""")

        st.markdown(f"""Toplam **{len(df['sex']) }** kayıttan oluşan anket verisi için gerekli ağırlıklandırma hesaplamaları yapılmıştır. Ağırlıklandırma sonucu katılımcıların dağılımları hakkındaki özeti aşağıda bulabilirsiniz.""", unsafe_allow_html=True)


        st.header("Ağırlıklandırma Özeti")
        
        sex_dist_w = df.pivot_table(values='Duzeltilmis_Agirlik',
                    index='sex',
                    aggfunc=np.sum,
                    fill_value=0,
                    margins=True,
                    margins_name='Genel Toplam')

        #sex_dist_p = round(sex_dist_w*100/sex_dist_w.iloc[-1,:],2).astype(str) + "%"
        sex_dist_p = sex_dist_w/sex_dist_w.iloc[-1,:]
        #sex_dist = pd.concat([sex_dist_w,sex_dist_p], axis=1,ignore_index=True)
        sex_dist_p= sex_dist_p.drop(sex_dist_p.tail(1).index)
        st.write("**Cinsiyet Dağılımı**")

        # st.write(sex_dist_p)
        st.bar_chart(sex_dist_p)


        educ_dist_w = df.pivot_table(values='Duzeltilmis_Agirlik',
                    index='educ',
                    aggfunc=np.sum,
                    fill_value=0,
                    margins=True,
                    margins_name='Genel Toplam')

        # educ_dist_p = round(educ_dist_w*100/educ_dist_w.iloc[-1,:],2).astype(str) + "%"
        educ_dist_p = educ_dist_w/educ_dist_w.iloc[-1,:]
        educ_dist_p= educ_dist_p.drop(educ_dist_p.tail(1).index)

        educ_dist_w_2 = df.pivot_table(values='Duzeltilmis_Agirlik',
                    index='educ_real',
                    aggfunc=np.sum,
                    fill_value=0,
                    margins=True,
                    margins_name='Genel Toplam')

        # educ_dist_p_2 = round(educ_dist_w_2*100/educ_dist_w_2.iloc[-1,:],2).astype(str) + "%"
        educ_dist_p_2 = educ_dist_w_2/educ_dist_w_2.iloc[-1,:]
        educ_dist_p_2= educ_dist_p_2.drop(educ_dist_p_2.tail(1).index)

        col1, col2 = st.columns(2)

        col1.write("**Eğitim Dağılımı**")

        col1.bar_chart(educ_dist_p)

        col2.write("**Tablolarda Kullanılan Eğitim Grubu Dağılımı**")

        col2.bar_chart(educ_dist_p_2)


        age_dist_w = df.pivot_table(values='Duzeltilmis_Agirlik',
                    index='age',
                    aggfunc=np.sum,
                    fill_value=0,
                    margins=True,
                    margins_name='Genel Toplam')

        # age_dist_p = round(age_dist_w*100/age_dist_w.iloc[-1,:],2).astype(str) + "%"
        age_dist_p = age_dist_w/age_dist_w.iloc[-1,:]

        age_dist_p= age_dist_p.drop(age_dist_p.tail(1).index)
        #sex_dist = pd.concat([sex_dist_w,sex_dist_p], axis=1,ignore_index=True)
        
        st.write("**Yaş Dağılımı**")

        st.bar_chart(age_dist_p)


        party_dist_w = df.pivot_table(values='Duzeltilmis_Agirlik',
                    index='2018_party',
                    aggfunc=np.sum,
                    fill_value=0,
                    margins=True,
                    margins_name='Genel Toplam')

        # party_dist_p = round(party_dist_w*100/party_dist_w.iloc[-1,:],2).astype(str) + "%"
        party_dist_p = party_dist_w/party_dist_w.iloc[-1,:]
        party_dist_p= party_dist_p.drop(party_dist_p.tail(1).index)
        #sex_dist = pd.concat([sex_dist_w,sex_dist_p], axis=1,ignore_index=True)
        
        st.write("**2018'de Tercih Edilen Parti Dağılımı**")

        st.bar_chart(party_dist_p)

        


        #Veriyi indirmek icin
        csv = convert_df(df)
        
        st.success("Ağırlıklandırılmış veriyi CSV dosyası olarak indirebilirsiniz")
        st.download_button(
        label="İndir",
        data=csv,
        file_name='Turkiye_Raporu_Agirliklandirilmis.csv',
        mime='text/csv')

    


    else:

        st.warning("Anket verisini Excel dosyası olarak yan taraftaki butondan yüklemeniz gerekir.")


    return None


def cs_text():

    if uploaded_file is None:
        st.header('Veriyi Hazırlama')
        st.markdown('Veriyi yüklemeden önce bazı sütunların isimlerini değiştirmeniz gerekir!')
        sampledf = pd.DataFrame({'Old':['Katılımcının cinsiyeti','Katılımcının yaş grubu (18-24 vs.)','Katılımcının eğitim seviyesi','Katılımcının 2018 seçimlerinde oy verdiği parti'], 'New':['sex','age','educ','2018_party']})
        sampledf.set_index('Old', inplace=True)
        st.dataframe(sampledf)
    else:
        st.markdown("---")

    return None

if __name__ == '__main__':
    main()