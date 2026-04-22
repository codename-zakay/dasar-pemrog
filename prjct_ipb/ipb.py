import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Fungsi untuk memuat data
@st.cache_data
def load_suhu_salinitas_data():
    """Memuat data suhu salinitas dari file CSV"""
    try:
        # Membaca file CSV dengan separator koma
        df = pd.read_csv('data suhu salinitas obd.csv')
        
        # Konversi kolom time ke datetime
        df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M')
        
        return df
    except Exception as e:
        st.error(f"Error loading suhu salinitas data: {e}")
        return None

@st.cache_data
def load_pasut_data():
    """Memuat data pasut dari file CSV"""
    try:
        # Membaca file CSV dengan separator ;
        df = pd.read_csv('pasut.csv', sep=';')
        
        # Membuat kolom datetime dari yyyy-mm-dd dan hh:mm:ss
        df['datetime'] = pd.to_datetime(df['yyyy-mm-dd'] + ' ' + df['hh:mm:ss'])
        
        # Hapus kolom yang tidak diperlukan
        df = df.drop(['yyyy-mm-dd', 'hh:mm:ss'], axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error loading pasut data: {e}")
        return None

# Load data
with st.spinner("Memuat data..."):
    df_suhu = load_suhu_salinitas_data()
    df_pasut = load_pasut_data()

if df_suhu is not None and df_pasut is not None:
    # Sidebar untuk navigasi
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
    
    st.sidebar.markdown("---")
    st.sidebar.info("👨‍💻 Tugas Minggu 4 OBD\n\nData: Suhu Salinitas & Pasut")
    
    # Tampilan berdasarkan pilihan
    if "1. Data Suhu Salinitas" in tugas:
        st.header("📈 Soal 1: Data Suhu Salinitas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Info Dataset")
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
        
        # Visualisasi
        st.subheader("Visualisasi Data")
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot suhu
        axes[0].plot(df_suhu['time'], df_suhu['thetao'], 'r-', alpha=0.7, linewidth=0.5)
        axes[0].set_title('Suhu (thetao)')
        axes[0].set_xlabel('Waktu')
        axes[0].set_ylabel('Suhu (°C)')
        axes[0].grid(True, alpha=0.3)
        
        # Plot salinitas
        axes[1].plot(df_suhu['time'], df_suhu['so'], 'b-', alpha=0.7, linewidth=0.5)
        axes[1].set_title('Salinitas (so)')
        axes[1].set_xlabel('Waktu')
        axes[1].set_ylabel('Salinitas (psu)')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
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
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.bar(monthly_mean['period'], monthly_mean['so'], color='skyblue')
            ax1.set_xlabel('Bulan')
            ax1.set_ylabel('Salinitas Rata-rata (psu)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig1)
        
        with col2:
            st.write("**Suhu (thetao)**")
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.bar(monthly_mean['period'], monthly_mean['thetao'], color='salmon')
            ax2.set_xlabel('Bulan')
            ax2.set_ylabel('Suhu Rata-rata (°C)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig2)
        
        st.dataframe(monthly_mean[['period', 'so', 'thetao']], use_container_width=True)
    
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
        
        # Visualisasi
        st.subheader("Visualisasi Agregasi Harian")
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 10))
        
        # Rata-rata thetao
        axes[0].plot(daily_agg.index, daily_agg['rata_rata_thetao'], 'g-', linewidth=1)
        axes[0].set_title('Rata-rata Suhu Harian')
        axes[0].set_ylabel('Suhu (°C)')
        axes[0].grid(True, alpha=0.3)
        axes[0].tick_params(axis='x', rotation=45)
        
        # Maksimum so
        axes[1].plot(daily_agg.index, daily_agg['maksimum_so'], 'b-', linewidth=1)
        axes[1].set_title('Maksimum Salinitas Harian')
        axes[1].set_ylabel('Salinitas (psu)')
        axes[1].grid(True, alpha=0.3)
        axes[1].tick_params(axis='x', rotation=45)
        
        # Standar deviasi thetao
        axes[2].plot(daily_agg.index, daily_agg['standar_deviasi_thetao'], 'r-', linewidth=1)
        axes[2].set_title('Standar Deviasi Suhu Harian')
        axes[2].set_ylabel('Std Dev Suhu (°C)')
        axes[2].set_xlabel('Tanggal')
        axes[2].grid(True, alpha=0.3)
        axes[2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Statistik agregasi
        st.subheader("Statistik Agregasi Harian")
        st.dataframe(daily_agg.describe(), use_container_width=True)
    
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("5 Hari dengan Suhu Rata-rata Tertinggi")
            top5_thetao = daily_agg.nlargest(5, 'rata_rata_thetao')[['rata_rata_thetao']]
            st.dataframe(top5_thetao, use_container_width=True)
            
            # Visualisasi
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            bars = ax1.bar(range(5), top5_thetao['rata_rata_thetao'].values, color='orange')
            ax1.set_xticks(range(5))
            ax1.set_xticklabels([d.strftime('%d-%b') for d in top5_thetao.index])
            ax1.set_ylabel('Suhu Rata-rata (°C)')
            ax1.set_title('Top 5 Suhu Tertinggi')
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Tambahkan nilai di atas bar
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom')
            
            st.pyplot(fig1)
        
        with col2:
            st.subheader("5 Hari dengan Salinitas Maksimum Terendah")
            bottom5_so = daily_agg.nsmallest(5, 'maksimum_so')[['maksimum_so']]
            st.dataframe(bottom5_so, use_container_width=True)
            
            # Visualisasi
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            bars = ax2.bar(range(5), bottom5_so['maksimum_so'].values, color='lightblue')
            ax2.set_xticks(range(5))
            ax2.set_xticklabels([d.strftime('%d-%b') for d in bottom5_so.index])
            ax2.set_ylabel('Salinitas Maksimum (psu)')
            ax2.set_title('Bottom 5 Salinitas Maksimum Terendah')
            ax2.grid(True, alpha=0.3, axis='y')
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom')
            
            st.pyplot(fig2)
        
        with col3:
            st.subheader("Selisih Suhu Rata-rata")
            
            # Hitung selisih suhu tertinggi dan terendah sepanjang tahun
            max_temp = daily_agg['rata_rata_thetao'].max()
            min_temp = daily_agg['rata_rata_thetao'].min()
            diff_temp = max_temp - min_temp
            
            # Cari tanggalnya
            date_max = daily_agg['rata_rata_thetao'].idxmax()
            date_min = daily_agg['rata_rata_thetao'].idxmin()
            
            st.metric("Suhu Tertinggi", f"{max_temp:.2f} °C", f"Tanggal: {date_max.strftime('%d %b %Y')}")
            st.metric("Suhu Terendah", f"{min_temp:.2f} °C", f"Tanggal: {date_min.strftime('%d %b %Y')}")
            st.metric("Selisih", f"{diff_temp:.2f} °C", delta_color="inverse")
            
            # Visualisasi distribusi suhu
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            ax3.hist(daily_agg['rata_rata_thetao'], bins=20, color='green', alpha=0.7, edgecolor='black')
            ax3.axvline(max_temp, color='red', linestyle='--', linewidth=2, label=f'Maks: {max_temp:.2f}')
            ax3.axvline(min_temp, color='blue', linestyle='--', linewidth=2, label=f'Min: {min_temp:.2f}')
            ax3.set_xlabel('Suhu Rata-rata Harian (°C)')
            ax3.set_ylabel('Frekuensi')
            ax3.set_title('Distribusi Suhu Rata-rata Harian')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            st.pyplot(fig3)
    
    elif "5. Analisis Pasut" in tugas:
        st.header("🌊 Soal 5: Analisis Pasut - Lembah dan Bukit")
        
        st.subheader("Data Pasut")
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
        
        # Visualisasi
        st.subheader("Visualisasi Pasut dengan Puncak dan Lembah")
        
        fig, ax = plt.subplots(figsize=(15, 6))
        
        # Plot seluruh data
        ax.plot(df_pasut['datetime'], df_pasut['elevasi (m)'], 'b-', linewidth=0.5, alpha=0.7, label='Elevasi')
        
        # Tandai puncak
        ax.scatter(peaks['datetime'], peaks['elevasi (m)'], color='red', s=30, marker='^', label='Puncak', zorder=5)
        
        # Tandai lembah
        ax.scatter(valleys['datetime'], valleys['elevasi (m)'], color='green', s=30, marker='v', label='Lembah', zorder=5)
        
        ax.set_xlabel('Waktu')
        ax.set_ylabel('Elevasi (m)')
        ax.set_title('Data Pasut dengan Puncak dan Lembah')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Batasi tampilan untuk kejelasan (misal 30 hari pertama)
        end_date = df_pasut['datetime'].min() + pd.Timedelta(days=30)
        ax.set_xlim(df_pasut['datetime'].min(), end_date)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        with st.expander("Lihat Data Puncak dan Lembah"):
            tab1, tab2 = st.tabs(["Data Puncak", "Data Lembah"])
            
            with tab1:
                st.dataframe(peaks, use_container_width=True)
            
            with tab2:
                st.dataframe(valleys, use_container_width=True)
    
    elif "6. Statistik Pasut" in tugas:
        st.header("📊 Soal 6: Statistik Pasut")
        
        # Hitung statistik
        monthly_mean = df_pasut.groupby(df_pasut['datetime'].dt.to_period('M'))['elevasi (m)'].mean().reset_index()
        monthly_mean['datetime'] = monthly_mean['datetime'].astype(str)
        
        max_yearly = df_pasut.groupby(df_pasut['datetime'].dt.year)['elevasi (m)'].max()
        min_yearly = df_pasut.groupby(df_pasut['datetime'].dt.year)['elevasi (m)'].min()
        range_yearly = max_yearly - min_yearly
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Rata-rata Bulanan")
            st.dataframe(monthly_mean.rename(columns={'datetime': 'Bulan', 'elevasi (m)': 'Rata-rata Elevasi'}), 
                        use_container_width=True)
            
            # Visualisasi rata-rata bulanan
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.bar(monthly_mean['datetime'], monthly_mean['elevasi (m)'], color='skyblue')
            ax1.set_xlabel('Bulan')
            ax1.set_ylabel('Rata-rata Elevasi (m)')
            ax1.set_title('Rata-rata Bulanan Elevasi Pasut')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig1)
        
        with col2:
            st.subheader("Maksimum & Minimum Tahunan")
            
            stats_df = pd.DataFrame({
                'Tahun': max_yearly.index,
                'Maksimum': max_yearly.values,
                'Minimum': min_yearly.values,
                'Rentang': range_yearly.values
            })
            
            st.dataframe(stats_df, use_container_width=True)
            
            # Visualisasi
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            x = range(len(stats_df))
            width = 0.35
            
            ax2.bar([i - width/2 for i in x], stats_df['Maksimum'], width, label='Maksimum', color='red', alpha=0.7)
            ax2.bar([i + width/2 for i in x], stats_df['Minimum'], width, label='Minimum', color='blue', alpha=0.7)
            
            ax2.set_xlabel('Tahun')
            ax2.set_ylabel('Elevasi (m)')
            ax2.set_title('Maksimum dan Minimum Tahunan')
            ax2.set_xticks(x)
            ax2.set_xticklabels(stats_df['Tahun'])
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig2)
        
        with col3:
            st.subheader("Rentang Elevasi Tahunan")
            
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            bars = ax3.bar(stats_df['Tahun'].astype(str), stats_df['Rentang'], color='purple', alpha=0.7)
            ax3.set_xlabel('Tahun')
            ax3.set_ylabel('Rentang Elevasi (m)')
            ax3.set_title('Rentang Elevasi (Max - Min) per Tahun')
            ax3.grid(True, alpha=0.3, axis='y')
            
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            st.pyplot(fig3)
    
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
            st.metric("Upper Bound (Mean + Std)", f"{upper_bound:.3f} m")
        with col4:
            st.metric("Lower Bound (Mean - Std)", f"{lower_bound:.3f} m")
        
        st.subheader("Jumlah Masing-masing Kategori")
        
        # Tampilkan hasil dalam bentuk bar
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Bar chart
        colors = {'Pasang Tinggi': 'red', 'Normal': 'green', 'Pasang Rendah': 'blue'}
        bar_colors = [colors[cat] for cat in kategori_counts.index]
        
        bars = ax1.bar(kategori_counts.index, kategori_counts.values, color=bar_colors)
        ax1.set_xlabel('Kategori')
        ax1.set_ylabel('Jumlah')
        ax1.set_title('Jumlah Data per Kategori Pasang')
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Pie chart
        ax2.pie(kategori_counts.values, labels=kategori_counts.index, autopct='%1.1f%%',
                colors=[colors[cat] for cat in kategori_counts.index], startangle=90)
        ax2.set_title('Proporsi Kategori Pasang')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabel hasil
        result_df = pd.DataFrame({
            'Kategori': kategori_counts.index,
            'Jumlah': kategori_counts.values,
            'Persentase': (kategori_counts.values / kategori_counts.sum() * 100).round(2)
        })
        
        st.dataframe(result_df, use_container_width=True)
        
        # Tampilkan sample data
        with st.expander("Lihat Sample Data dengan Kategori"):
            st.dataframe(df_pasut_copy[['datetime', 'elevasi (m)', 'kategori']].head(20), use_container_width=True)
    
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
        
        # Visualisasi korelasi
        st.subheader("Korelasi antar Parameter")
        
        corr_cols = ['so', 'thetao', 'elevasi_mean', 'elevasi_max', 'elevasi_min']
        corr_matrix = merged_df[corr_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        ax.set_title('Matriks Korelasi')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Simpan data merge ke CSV (opsional)
        csv = merged_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data Merge (CSV)",
            data=csv,
            file_name="data_merge_suhu_pasut.csv",
            mime="text/csv"
        )
    
    elif "9. Rata-rata Harian" in tugas:
        st.header("📈 Soal 9: Rata-rata Harian, Bulanan, dan Tahunan")
        
        # Siapkan data suhu salinitas (resample)
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
            
            fig, axes = plt.subplots(2, 1, figsize=(15, 8))
            
            axes[0].plot(daily_stats['date'], daily_stats['so_mean'], 'b-', linewidth=1, label='Rata-rata')
            axes[0].fill_between(daily_stats['date'], 
                                 daily_stats['so_mean'] - daily_stats['so_std'],
                                 daily_stats['so_mean'] + daily_stats['so_std'],
                                 alpha=0.3, color='blue', label='±1 Std Dev')
            axes[0].set_ylabel('Salinitas (psu)')
            axes[0].set_title('Salinitas Harian')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            axes[1].plot(daily_stats['date'], daily_stats['thetao_mean'], 'r-', linewidth=1, label='Rata-rata')
            axes[1].fill_between(daily_stats['date'], 
                                 daily_stats['thetao_mean'] - daily_stats['thetao_std'],
                                 daily_stats['thetao_mean'] + daily_stats['thetao_std'],
                                 alpha=0.3, color='red', label='±1 Std Dev')
            axes[1].set_xlabel('Tanggal')
            axes[1].set_ylabel('Suhu (°C)')
            axes[1].set_title('Suhu Harian')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with tab2:
            st.subheader("Statistik Bulanan")
            st.dataframe(monthly_stats, use_container_width=True)
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            
            axes[0].bar(monthly_stats['year_month'], monthly_stats['so_mean'], color='skyblue', alpha=0.7, label='Mean')
            axes[0].errorbar(monthly_stats['year_month'], monthly_stats['so_mean'], 
                           yerr=monthly_stats['so_std'], fmt='none', color='black', capsize=5)
            axes[0].set_ylabel('Salinitas (psu)')
            axes[0].set_title('Salinitas Bulanan')
            axes[0].tick_params(axis='x', rotation=45)
            axes[0].grid(True, alpha=0.3, axis='y')
            
            axes[1].bar(monthly_stats['year_month'], monthly_stats['thetao_mean'], color='salmon', alpha=0.7, label='Mean')
            axes[1].errorbar(monthly_stats['year_month'], monthly_stats['thetao_mean'], 
                           yerr=monthly_stats['thetao_std'], fmt='none', color='black', capsize=5)
            axes[1].set_ylabel('Suhu (°C)')
            axes[1].set_title('Suhu Bulanan')
            axes[1].tick_params(axis='x', rotation=45)
            axes[1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with tab3:
            st.subheader("Statistik Tahunan")
            st.dataframe(yearly_stats, use_container_width=True)
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            x = yearly_stats['year'].astype(str)
            width = 0.35
            
           