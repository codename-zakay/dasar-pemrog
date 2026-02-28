import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Data OBD - Tugas Minggu 4",
    page_icon="🌊",
    layout="wide"
)

# Judul aplikasi
st.title("🌊 Analisis Data Oseanografi - Tugas Minggu 4")
st.markdown("---")

# Inisialisasi session state untuk menyimpan data
if 'df_suhu' not in st.session_state:
    st.session_state.df_suhu = None
if 'df_pasut' not in st.session_state:
    st.session_state.df_pasut = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Sidebar untuk upload file
st.sidebar.title("📂 Upload Data")
st.sidebar.markdown("Upload file CSV untuk analisis")

# Upload file suhu salinitas
uploaded_suhu = st.sidebar.file_uploader(
    "Upload Data Suhu Salinitas (CSV)", 
    type=['csv'],
    key="suhu_uploader"
)

# Upload file pasut
uploaded_pasut = st.sidebar.file_uploader(
    "Upload Data Pasut (CSV)", 
    type=['csv'],
    key="pasut_uploader"
)

# Tombol untuk memproses upload
if st.sidebar.button("🔄 Proses Upload Data", type="primary"):
    if uploaded_suhu is not None and uploaded_pasut is not None:
        with st.spinner("Memproses data..."):
            try:
                # Baca data suhu salinitas
                df_suhu = pd.read_csv(uploaded_suhu)
                df_suhu['time'] = pd.to_datetime(df_suhu['time'], format='%d/%m/%Y %H:%M')
                st.session_state.df_suhu = df_suhu
                
                # Baca data pasut
                df_pasut = pd.read_csv(uploaded_pasut, sep=';')
                # Konversi datetime dengan dayfirst=True
                df_pasut['datetime'] = pd.to_datetime(
                    df_pasut['yyyy-mm-dd'] + ' ' + df_pasut['hh:mm:ss'], 
                    dayfirst=True
                )
                df_pasut = df_pasut.drop(['yyyy-mm-dd', 'hh:mm:ss'], axis=1)
                st.session_state.df_pasut = df_pasut
                
                st.session_state.data_loaded = True
                st.sidebar.success("✅ Data berhasil diupload!")
                
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
                st.session_state.data_loaded = False
    else:
        st.sidebar.warning("⚠️ Harap upload kedua file terlebih dahulu")

# Tampilkan info data jika sudah diupload
if st.session_state.data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Info Data")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Data Suhu", f"{len(st.session_state.df_suhu):,} baris")
    with col2:
        st.metric("Data Pasut", f"{len(st.session_state.df_pasut):,} baris")
    
    # Tombol reset
    if st.sidebar.button("🔄 Reset Data"):
        st.session_state.df_suhu = None
        st.session_state.df_pasut = None
        st.session_state.data_loaded = False
        st.rerun()

# Main content - hanya tampil jika data sudah diupload
if st.session_state.data_loaded:
    df_suhu = st.session_state.df_suhu
    df_pasut = st.session_state.df_pasut
    
    # Sidebar untuk navigasi
    st.sidebar.markdown("---")
    st.sidebar.title("📊 Navigasi Tugas")
    tugas = st.sidebar.radio(
        "Pilih Nomor Tugas:",
        ["1. Data Suhu Salinitas", 
         "2. Ekstraksi Waktu & Rata-rata Bulanan",
         "3. Agregasi Harian",
         "4. Analisis 5 Hari Tertinggi/Terendah",
         "5. Analisis Pasut - Lembah & Bukit",
         "6. Statistik Pasut",
         "7. Kategorisasi Pasang",
         "8. Merge Data",
         "9. Rata-rata Harian, Bulanan, Tahunan",
         "10. Filter Data"]
    )
    
    # Tampilan berdasarkan pilihan
    if "1. Data Suhu Salinitas" in tugas:
        st.header("📈 Soal 1: Data Suhu Salinitas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Info Dataset")
            st.write(f"**Nama file:** {uploaded_suhu.name}")
            st.write(f"**Jumlah baris:** {len(df_suhu)}")
            st.write(f"**Jumlah kolom:** {len(df_suhu.columns)}")
            st.write(f"**Rentang waktu:** {df_suhu['time'].min()} - {df_suhu['time'].max()}")
        
        with col2:
            st.subheader("Cek Missing Value")
            missing = df_suhu[['so', 'thetao']].isnull().sum()
            st.write(missing)
            
            if missing.sum() == 0:
                st.success("✅ Tidak ada missing value pada kolom so dan thetao")
            else:
                st.warning(f"⚠️ Terdapat {missing.sum()} missing value")
        
        st.subheader("Statistik Deskriptif")
        st.dataframe(df_suhu[['so', 'thetao']].describe().T, use_container_width=True)
        
        # Visualisasi dengan line chart streamlit
        st.subheader("Visualisasi Data")
        
        # Sample data untuk performa (ambil 5000 sample)
        sample_size = min(5000, len(df_suhu))
        df_sample = df_suhu.sample(sample_size).sort_values('time')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Suhu (thetao)**")
            chart_data = df_sample[['time', 'thetao']].copy()
            chart_data = chart_data.set_index('time')
            st.line_chart(chart_data, height=300)
        
        with col2:
            st.write("**Salinitas (so)**")
            chart_data = df_sample[['time', 'so']].copy()
            chart_data = chart_data.set_index('time')
            st.line_chart(chart_data, height=300)
        
        # Tampilkan data
        with st.expander("Lihat Data"):
            st.dataframe(df_suhu.head(100), use_container_width=True)
    
    elif "2. Ekstraksi Waktu" in tugas:
        st.header("📅 Soal 2: Ekstraksi Waktu & Rata-rata Bulanan")
        
        # Membuat salinan dataframe
        df = df_suhu.copy()
        
        # Ekstraksi komponen waktu
        df['year'] = df['time'].dt.year
        df['month'] = df['time'].dt.month
        df['day'] = df['time'].dt.day
        df['hour'] = df['time'].dt.hour
        
        st.subheader("Data dengan Kolom Waktu Baru")
        st.dataframe(df[['time', 'year', 'month', 'day', 'hour', 'so', 'thetao']].head(10), use_container_width=True)
        
        # Rata-rata bulanan
        monthly_mean = df.groupby(['year', 'month'])[['so', 'thetao']].mean().reset_index()
        monthly_mean['period'] = monthly_mean['year'].astype(str) + '-' + monthly_mean['month'].astype(str).str.zfill(2)
        
        st.subheader("Rata-rata Bulanan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Salinitas (so)**")
            chart_data = monthly_mean.set_index('period')[['so']]
            st.bar_chart(chart_data, height=300)
        
        with col2:
            st.write("**Suhu (thetao)**")
            chart_data = monthly_mean.set_index('period')[['thetao']]
            st.bar_chart(chart_data, height=300)
        
        st.dataframe(monthly_mean[['period', 'so', 'thetao']], use_container_width=True)
        
        # Tombol download hasil
        csv = monthly_mean.to_csv(index=False)
        st.download_button(
            label="📥 Download Rata-rata Bulanan (CSV)",
            data=csv,
            file_name="rata_rata_bulanan.csv",
            mime="text/csv"
        )
    
    elif "3. Agregasi Harian" in tugas:
        st.header("📊 Soal 3: Agregasi Harian")
        
        # Membuat salinan dataframe
        df = df_suhu.copy()
        df['date'] = df['time'].dt.date
        
        # Agregasi harian
        daily_agg = df.groupby('date').agg(
            rata_rata_thetao=('thetao', 'mean'),
            maksimum_so=('so', 'max'),
            standar_deviasi_thetao=('thetao', 'std')
        ).reset_index()
        
        # Set index sebagai tanggal
        daily_agg.set_index('date', inplace=True)
        
        st.subheader("DataFrame Hasil Agregasi Harian")
        st.dataframe(daily_agg, use_container_width=True)
        
        # Visualisasi dengan line chart
        st.subheader("Visualisasi Agregasi Harian")
        
        tab1, tab2, tab3 = st.tabs(["Rata-rata Suhu", "Maksimum Salinitas", "Std Dev Suhu"])
        
        with tab1:
            chart_data = daily_agg[['rata_rata_thetao']].copy()
            st.line_chart(chart_data, height=300)
        
        with tab2:
            chart_data = daily_agg[['maksimum_so']].copy()
            st.line_chart(chart_data, height=300)
        
        with tab3:
            chart_data = daily_agg[['standar_deviasi_thetao']].copy()
            st.line_chart(chart_data, height=300)
        
        # Statistik agregasi
        st.subheader("Statistik Agregasi Harian")
        st.dataframe(daily_agg.describe(), use_container_width=True)
        
        # Tombol download
        csv = daily_agg.reset_index().to_csv(index=False)
        st.download_button(
            label="📥 Download Agregasi Harian (CSV)",
            data=csv,
            file_name="agregasi_harian.csv",
            mime="text/csv"
        )
    
    elif "4. Analisis 5 Hari" in tugas:
        st.header("🏆 Soal 4: Analisis 5 Hari Tertinggi/Terendah")
        
        # Membuat salinan dataframe dan agregasi harian
        df = df_suhu.copy()
        df['date'] = df['time'].dt.date
        
        daily_agg = df.groupby('date').agg(
            rata_rata_thetao=('thetao', 'mean'),
            maksimum_so=('so', 'max')
        ).reset_index()
        
        daily_agg['date'] = pd.to_datetime(daily_agg['date'])
        daily_agg.set_index('date', inplace=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("5 Hari dengan Suhu Rata-rata Tertinggi")
            top5_thetao = daily_agg.nlargest(5, 'rata_rata_thetao')[['rata_rata_thetao']]
            top5_thetao_display = top5_thetao.copy()
            top5_thetao_display.index = top5_thetao_display.index.strftime('%d %b %Y')
            st.dataframe(top5_thetao_display, use_container_width=True)
            
            # Bar chart
            chart_data = pd.DataFrame({
                'Tanggal': top5_thetao.index.strftime('%d-%b'),
                'Suhu': top5_thetao['rata_rata_thetao'].values
            }).set_index('Tanggal')
            st.bar_chart(chart_data, height=250)
        
        with col2:
            st.subheader("5 Hari dengan Salinitas Maksimum Terendah")
            bottom5_so = daily_agg.nsmallest(5, 'maksimum_so')[['maksimum_so']]
            bottom5_so_display = bottom5_so.copy()
            bottom5_so_display.index = bottom5_so_display.index.strftime('%d %b %Y')
            st.dataframe(bottom5_so_display, use_container_width=True)
            
            # Bar chart
            chart_data = pd.DataFrame({
                'Tanggal': bottom5_so.index.strftime('%d-%b'),
                'Salinitas': bottom5_so['maksimum_so'].values
            }).set_index('Tanggal')
            st.bar_chart(chart_data, height=250)
        
        st.subheader("Selisih Suhu Rata-rata")
        
        # Hitung selisih suhu tertinggi dan terendah sepanjang tahun
        max_temp = daily_agg['rata_rata_thetao'].max()
        min_temp = daily_agg['rata_rata_thetao'].min()
        diff_temp = max_temp - min_temp
        
        # Cari tanggalnya
        date_max = daily_agg['rata_rata_thetao'].idxmax()
        date_min = daily_agg['rata_rata_thetao'].idxmin()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Suhu Tertinggi", f"{max_temp:.2f} °C", f"Tanggal: {date_max.strftime('%d %b %Y')}")
        
        with col2:
            st.metric("Suhu Terendah", f"{min_temp:.2f} °C", f"Tanggal: {date_min.strftime('%d %b %Y')}")
        
        with col3:
            st.metric("Selisih", f"{diff_temp:.2f} °C")
    
    elif "5. Analisis Pasut" in tugas:
        st.header("🌊 Soal 5: Analisis Pasut - Lembah dan Bukit")
        
        st.subheader("Data Pasut")
        st.write(f"**Nama file:** {uploaded_pasut.name}")
        st.dataframe(df_pasut.head(10), use_container_width=True)
        
        # Fungsi untuk mendeteksi puncak dan lembah
        def find_peaks_and_valleys(data):
            peaks = []
            valleys = []
            
            for i in range(1, len(data) - 1):
                # Deteksi puncak (bukit)
                if data[i] > data[i-1] and data[i] > data[i+1]:
                    peaks.append(i)
                # Deteksi lembah
                if data[i] < data[i-1] and data[i] < data[i+1]:
                    valleys.append(i)
            
            return peaks, valleys
        
        # Cari puncak dan lembah
        elevasi = df_pasut['elevasi (m)'].values
        peaks_idx, valleys_idx = find_peaks_and_valleys(elevasi)
        
        peaks = df_pasut.iloc[peaks_idx]
        valleys = df_pasut.iloc[valleys_idx]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Jumlah Bukit (Puncak)", len(peaks))
        with col2:
            st.metric("Jumlah Lembah", len(valleys))
        with col3:
            st.metric("Total", len(peaks) + len(valleys))
        
        # Visualisasi dengan line chart
        st.subheader("Visualisasi Pasut (30 hari pertama)")
        
        # Batasi untuk 30 hari pertama agar lebih jelas
        end_date = df_pasut['datetime'].min() + pd.Timedelta(days=30)
        df_sample = df_pasut[df_pasut['datetime'] <= end_date].copy()
        
        chart_data = df_sample.set_index('datetime')[['elevasi (m)']]
        st.line_chart(chart_data, height=400)
        
        # Tandai puncak dan lembah dalam tabel
        st.subheader("Data Puncak dan Lembah")
        
        tab1, tab2 = st.tabs(["Data Puncak", "Data Lembah"])
        
        with tab1:
            if len(peaks) > 0:
                peaks_display = peaks[['datetime', 'elevasi (m)']].copy()
                peaks_display['datetime'] = peaks_display['datetime'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(peaks_display, use_container_width=True)
                
                # Download data puncak
                csv_peaks = peaks.to_csv(index=False)
                st.download_button("📥 Download Data Puncak", csv_peaks, "data_puncak.csv", "text/csv")
            else:
                st.info("Tidak ada data puncak")
        
        with tab2:
            if len(valleys) > 0:
                valleys_display = valleys[['datetime', 'elevasi (m)']].copy()
                valleys_display['datetime'] = valleys_display['datetime'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(valleys_display, use_container_width=True)
                
                # Download data lembah
                csv_valleys = valleys.to_csv(index=False)
                st.download_button("📥 Download Data Lembah", csv_valleys, "data_lembah.csv", "text/csv")
            else:
                st.info("Tidak ada data lembah")
    
    elif "6. Statistik Pasut" in tugas:
        st.header("📊 Soal 6: Statistik Pasut")
        
        # Hitung statistik
        monthly_mean = df_pasut.groupby(df_pasut['datetime'].dt.to_period('M'))['elevasi (m)'].mean().reset_index()
        monthly_mean['datetime'] = monthly_mean['datetime'].astype(str)
        
        max_yearly = df_pasut.groupby(df_pasut['datetime'].dt.year)['elevasi (m)'].max()
        min_yearly = df_pasut.groupby(df_pasut['datetime'].dt.year)['elevasi (m)'].min()
        range_yearly = max_yearly - min_yearly
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rata-rata Bulanan")
            monthly_display = monthly_mean.rename(columns={'datetime': 'Bulan', 'elevasi (m)': 'Rata-rata Elevasi'})
            st.dataframe(monthly_display, use_container_width=True)
            
            # Bar chart
            chart_data = monthly_mean.set_index('datetime')[['elevasi (m)']]
            st.bar_chart(chart_data, height=250)
        
        with col2:
            st.subheader("Maksimum & Minimum Tahunan")
            
            stats_df = pd.DataFrame({
                'Tahun': max_yearly.index,
                'Maksimum': max_yearly.values,
                'Minimum': min_yearly.values,
                'Rentang': range_yearly.values
            })
            
            st.dataframe(stats_df, use_container_width=True)
        
        st.subheader("Rentang Elevasi Tahunan")
        rentang_data = stats_df.set_index('Tahun')[['Rentang']]
        st.bar_chart(rentang_data, height=300)
        
        # Download semua statistik
        col1, col2 = st.columns(2)
        with col1:
            csv_monthly = monthly_mean.to_csv(index=False)
            st.download_button("📥 Download Statistik Bulanan", csv_monthly, "statistik_bulanan.csv", "text/csv")
        with col2:
            csv_yearly = stats_df.to_csv(index=False)
            st.download_button("📥 Download Statistik Tahunan", csv_yearly, "statistik_tahunan.csv", "text/csv")
    
    elif "7. Kategorisasi Pasang" in tugas:
        st.header("🏷️ Soal 7: Kategorisasi Pasang")
        
        # Hitung mean dan std
        mean_elev = df_pasut['elevasi (m)'].mean()
        std_elev = df_pasut['elevasi (m)'].std()
        
        upper_bound = mean_elev + std_elev
        lower_bound = mean_elev - std_elev
        
        # Buat salinan dataframe
        df_pasut_copy = df_pasut.copy()
        
        # Buat kolom kategori
        conditions = [
            df_pasut_copy['elevasi (m)'] > upper_bound,
            df_pasut_copy['elevasi (m)'] < lower_bound
        ]
        choices = ['Pasang Tinggi', 'Pasang Rendah']
        
        df_pasut_copy['kategori'] = np.select(conditions, choices, default='Normal')
        
        # Hitung jumlah masing-masing kategori
        kategori_counts = df_pasut_copy['kategori'].value_counts()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{mean_elev:.3f} m")
        with col2:
            st.metric("Std Dev", f"{std_elev:.3f} m")
        with col3:
            st.metric("Upper Bound", f"{upper_bound:.3f} m")
        with col4:
            st.metric("Lower Bound", f"{lower_bound:.3f} m")
        
        st.subheader("Jumlah Masing-masing Kategori")
        
        # Bar chart
        chart_data = pd.DataFrame({
            'Kategori': kategori_counts.index,
            'Jumlah': kategori_counts.values
        }).set_index('Kategori')
        
        st.bar_chart(chart_data, height=300)
        
        # Tabel hasil
        result_df = pd.DataFrame({
            'Kategori': kategori_counts.index,
            'Jumlah': kategori_counts.values,
            'Persentase': (kategori_counts.values / kategori_counts.sum() * 100).round(2)
        })
        
        st.dataframe(result_df, use_container_width=True)
        
        # Download data dengan kategori
        csv_with_category = df_pasut_copy.to_csv(index=False)
        st.download_button(
            label="📥 Download Data Pasut dengan Kategori",
            data=csv_with_category,
            file_name="data_pasut_dengan_kategori.csv",
            mime="text/csv"
        )
    
    elif "8. Merge Data" in tugas:
        st.header("🔄 Soal 8: Merge Data Suhu Salinitas dan Pasut")
        
        # Siapkan data suhu salinitas (resample harian)
        df_suhu_daily = df_suhu.copy()
        df_suhu_daily['date'] = df_suhu_daily['time'].dt.date
        
        # Agregasi harian suhu salinitas
        suhu_daily = df_suhu_daily.groupby('date').agg({
            'so': 'mean',
            'thetao': 'mean',
            'depth': 'mean',
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        
        suhu_daily['date'] = pd.to_datetime(suhu_daily['date'])
        
        # Siapkan data pasut (resample harian)
        df_pasut_daily = df_pasut.copy()
        df_pasut_daily['date'] = df_pasut_daily['datetime'].dt.date
        
        pasut_daily = df_pasut_daily.groupby('date').agg({
            'elevasi (m)': ['mean', 'max', 'min', 'std'],
            'Latitude': 'first',
            'Longitude': 'first'
        }).reset_index()
        
        pasut_daily.columns = ['date', 'elevasi_mean', 'elevasi_max', 'elevasi_min', 'elevasi_std', 'Latitude', 'Longitude']
        pasut_daily['date'] = pd.to_datetime(pasut_daily['date'])
        
        # Merge data
        merged_df = pd.merge(suhu_daily, pasut_daily, on='date', how='inner')
        
        st.subheader("Hasil Merge (Data Harian)")
        st.write(f"**Jumlah baris setelah merge:** {len(merged_df)}")
        st.dataframe(merged_df.head(10), use_container_width=True)
        
        # Statistik data merge
        st.subheader("Statistik Data Merge")
        st.dataframe(merged_df[['so', 'thetao', 'elevasi_mean', 'elevasi_max', 'elevasi_min']].describe(), 
                    use_container_width=True)
        
        # Korelasi
        st.subheader("Korelasi antar Parameter")
        corr_cols = ['so', 'thetao', 'elevasi_mean', 'elevasi_max', 'elevasi_min']
        corr_matrix = merged_df[corr_cols].corr()
        st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'), use_container_width=True)
        
        # Download data merge
        csv = merged_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data Merge (CSV)",
            data=csv,
            file_name="data_merge_suhu_pasut.csv",
            mime="text/csv"
        )
    
    elif "9. Rata-rata Harian" in tugas:
        st.header("📈 Soal 9: Rata-rata Harian, Bulanan, dan Tahunan")
        
        # Siapkan data suhu salinitas
        df_suhu_daily = df_suhu.copy()
        df_suhu_daily['date'] = df_suhu_daily['time'].dt.date
        
        # Agregasi harian
        daily_stats = df_suhu_daily.groupby('date').agg({
            'so': ['mean', 'std', 'min', 'max'],
            'thetao': ['mean', 'std', 'min', 'max']
        }).reset_index()
        daily_stats.columns = ['date', 'so_mean', 'so_std', 'so_min', 'so_max', 
                              'thetao_mean', 'thetao_std', 'thetao_min', 'thetao_max']
        daily_stats['date'] = pd.to_datetime(daily_stats['date'])
        
        # Agregasi bulanan
        df_suhu_daily['year_month'] = df_suhu_daily['time'].dt.to_period('M')
        monthly_stats = df_suhu_daily.groupby('year_month').agg({
            'so': ['mean', 'std', 'min', 'max'],
            'thetao': ['mean', 'std', 'min', 'max']
        }).reset_index()
        monthly_stats.columns = ['year_month', 'so_mean', 'so_std', 'so_min', 'so_max', 
                                'thetao_mean', 'thetao_std', 'thetao_min', 'thetao_max']
        monthly_stats['year_month'] = monthly_stats['year_month'].astype(str)
        
        # Agregasi tahunan
        df_suhu_daily['year'] = df_suhu_daily['time'].dt.year
        yearly_stats = df_suhu_daily.groupby('year').agg({
            'so': ['mean', 'std', 'min', 'max'],
            'thetao': ['mean', 'std', 'min', 'max']
        }).reset_index()
        yearly_stats.columns = ['year', 'so_mean', 'so_std', 'so_min', 'so_max', 
                               'thetao_mean', 'thetao_std', 'thetao_min', 'thetao_max']
        
        tab1, tab2, tab3 = st.tabs(["Harian", "Bulanan", "Tahunan"])
        
        with tab1:
            st.subheader("Statistik Harian")
            st.dataframe(daily_stats, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Salinitas Harian**")
                chart_data = daily_stats.set_index('date')[['so_mean', 'so_min', 'so_max']]
                st.line_chart(chart_data, height=250)
            with col2:
                st.write("**Suhu Harian**")
                chart_data = daily_stats.set_index('date')[['thetao_mean', 'thetao_min', 'thetao_max']]
                st.line_chart(chart_data, height=250)
        
        with tab2:
            st.subheader("Statistik Bulanan")
            st.dataframe(monthly_stats, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Salinitas Bulanan**")
                chart_data = monthly_stats.set_index('year_month')[['so_mean']]
                st.bar_chart(chart_data, height=250)
            with col2:
                st.write("**Suhu Bulanan**")
                chart_data = monthly_stats.set_index('year_month')[['thetao_mean']]
                st.bar_chart(chart_data, height=250)
        
        with tab3:
            st.subheader("Statistik Tahunan")
            st.dataframe(yearly_stats, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Salinitas Tahunan**")
                chart_data = yearly_stats.set_index('year')[['so_mean']]
                st.bar_chart(chart_data, height=250)
            with col2:
                st.write("**Suhu Tahunan**")
                chart_data = yearly_stats.set_index('year')[['thetao_mean']]
                st.bar_chart(chart_data, height=250)
        
        # Download semua statistik
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_daily = daily_stats.to_csv(index=False)
            st.download_button("📥 Download Harian", csv_daily, "statistik_harian.csv", "text/csv")
        with col2:
            csv_monthly = monthly_stats.to_csv(index=False)
            st.download_button("📥 Download Bulanan", csv_monthly, "statistik_bulanan.csv", "text/csv")
        with col3:
            csv_yearly = yearly_stats.to_csv(index=False)
            st.download_button("📥 Download Tahunan", csv_yearly, "statistik_tahunan.csv", "text/csv")
    
    elif "10. Filter Data" in tugas:
        st.header("🗑️ Soal 10: Filter Data")
        
        st.subheader("Data Sebelum Filter")
        st.write(f"**Jumlah data suhu salinitas:** {len(df_suhu)}")
        st.write(f"**Jumlah data pasut:** {len(df_pasut)}")
        
        # Filter data suhu salinitas
        df_suhu_filtered = df_suhu.copy()
        df_suhu_filtered['day'] = df_suhu_filtered['time'].dt.day
        
        # Hapus tanggal 5, 7, dan 21
        df_suhu_filtered = df_suhu_filtered[~df_suhu_filtered['day'].isin([5, 7, 21])]
        df_suhu_filtered = df_suhu_filtered.drop('day', axis=1)
        
        # Filter data pasut (hapus nilai negatif)
        df_pasut_filtered = df_pasut[df_pasut['elevasi (m)'] >= 0].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data Suhu Salinitas Setelah Filter")
            st.write(f"**Jumlah data awal:** {len(df_suhu)}")
            st.write(f"**Jumlah data setelah filter:** {len(df_suhu_filtered)}")
            st.write(f"**Data terhapus:** {len(df_suhu) - len(df_suhu_filtered)}")
            st.dataframe(df_suhu_filtered.head(10), use_container_width=True)
        
        with col2:
            st.subheader("Data Pasut Setelah Filter")
            st.write(f"**Jumlah data awal:** {len(df_pasut)}")
            st.write(f"**Jumlah data setelah filter:** {len(df_pasut_filtered)}")
            st.write(f"**Data terhapus:** {len(df_pasut) - len(df_pasut_filtered)}")
            st.dataframe(df_pasut_filtered.head(10), use_container_width=True)
        
        # Download button untuk data yang sudah difilter
        col1, col2 = st.columns(2)
        
        with col1:
            csv_suhu = df_suhu_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Data Suhu Salinitas Filtered",
                data=csv_suhu,
                file_name="data_suhu_salinitas_filtered.csv",
                mime="text/csv"
            )
        
        with col2:
            csv_pasut = df_pasut_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Data Pasut Filtered",
                data=csv_pasut,
                file_name="data_pasut_filtered.csv",
                mime="text/csv"
            )

else:
    # Tampilan jika belum upload data
    st.info("👋 Silakan upload file CSV terlebih dahulu di sidebar untuk memulai analisis.")
    
    st.markdown("""
    ### 📋 Petunjuk Penggunaan:
    
    1. **Klik tombol "Browse files"** di sidebar untuk memilih file
    2. Upload **file Data Suhu Salinitas** (format CSV)
    3. Upload **file Data Pasut** (format CSV dengan separator ;)
    4. Klik tombol **"Proses Upload Data"**
    5. Pilih nomor tugas yang ingin dianalisis
    
    ### 📁 Format File:
    
    **Data Suhu Salinitas:**
    ```
    time,depth,latitude,longitude,so,thetao
    
    Contoh: 
    01/01/2024 00:00,0.494025,-6.0833335,105.250015,33.03554,29.614788
    ```
    
    **Data Pasut:**
    ```
    Latitude;Longitude;yyyy-mm-dd;hh:mm:ss;elevasi (m)
    
    Contoh:
    -5.925;107.025;01/01/2020;00:00:00;0.133
    ```
    """)
    
    st.markdown("""
        <div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
            <p style="margin: 0;">
                <strong>🏛️Universitas Institut Pertanian Bogor</strong> • Fakultas Perikanan, Ocean Fisheries Big Data
            </p>
            <p style="margin: 5px 0 0 0; font-size: 11px;">
                Developed by <strong>Fauzi Dwi Edit Waskito</strong> • © Februari 2026
            </p>
        </div>
        """, unsafe_allow_html=True)