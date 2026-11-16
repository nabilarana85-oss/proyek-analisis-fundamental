# dashboard.py
# Jalankan: streamlit run dashboard.py
# Letakkan main_data.csv dan hour_data.csv di folder yang sama dengan file ini.

from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

sns.set_theme(style="whitegrid")
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

BASE = Path(__file__).parent


@st.cache_data
def load_data():
    day = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE / "hour_data.csv", parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()

# Filter tanggal
st.sidebar.header("Filter")
rentang = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(day_df["dteday"].min(), day_df["dteday"].max()),
    min_value=day_df["dteday"].min(),
    max_value=day_df["dteday"].max(),
)
if len(rentang) != 2:
    st.info("Pilih tanggal akhir pada filter.")
    st.stop()

mulai, akhir = pd.to_datetime(rentang[0]), pd.to_datetime(rentang[1])
day = day_df[day_df["dteday"].between(mulai, akhir)]
hour = hour_df[hour_df["dteday"].between(mulai, akhir)]

st.title("Dashboard Penyewaan Sepeda (Bike Sharing)")

# Ringkasan
c1, c2, c3 = st.columns(3)
c1.metric("Total Penyewaan", f"{day['cnt'].sum():,}")
c2.metric("Rata-rata Harian", f"{day['cnt'].mean():,.0f}")
c3.metric("Jumlah Hari", f"{len(day)}")

# Pertanyaan 1
st.subheader("Pola Penyewaan per Jam: Hari Kerja vs Bukan Hari Kerja")
per_jam = hour.groupby(["hr", "workingday"])["cnt"].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(12, 5))
sns.lineplot(data=per_jam, x="hr", y="cnt", hue="workingday", marker="o", ax=ax1)
ax1.set_xlabel("Jam (00.00–23.00)")
ax1.set_ylabel("Rata-rata Penyewaan")
ax1.set_xticks(range(24))
ax1.legend(title="Jenis Hari")
st.pyplot(fig1)

puncak = per_jam.loc[per_jam.groupby("workingday")["cnt"].idxmax()]
st.markdown("**Insight**")
for _, r in puncak.iterrows():
    st.write(f"- {r['workingday']}: puncak pukul {int(r['hr']):02d}.00 ({r['cnt']:.2f} penyewaan/jam).")
st.write("- Hari kerja memiliki lonjakan pada jam berangkat dan pulang aktivitas (sekitar 07.00–08.00 dan 17.00–18.00).")
st.write("- Bukan hari kerja cenderung lebih tinggi pada siang hingga sore hari.")

# Pertanyaan 2
st.subheader("Rata-rata Penyewaan Harian berdasarkan Musim dan Cuaca")
musim_cuaca = day.groupby(["season", "weathersit"])["cnt"].agg(["mean", "count"]).reset_index()

fig2, ax2 = plt.subplots(figsize=(12, 5))
sns.barplot(
    data=musim_cuaca,
    x="season",
    y="mean",
    hue="weathersit",
    order=["Spring", "Summer", "Fall", "Winter"],
    hue_order=["Clear", "Cloudy", "Light Rain/Snow"],
    ax=ax2,
)
ax2.set_xlabel("Musim")
ax2.set_ylabel("Rata-rata Penyewaan per Hari")
ax2.legend(title="Kondisi Cuaca")
st.pyplot(fig2)

st.markdown("**Insight**")
if not musim_cuaca.empty:
    tinggi = musim_cuaca.loc[musim_cuaca["mean"].idxmax()]
    rendah = musim_cuaca.loc[musim_cuaca["mean"].idxmin()]
    st.write(f"- Tertinggi: {tinggi['season']} - {tinggi['weathersit']} ({tinggi['mean']:,.2f}/hari, {int(tinggi['count'])} hari).")
    st.write(f"- Terendah: {rendah['season']} - {rendah['weathersit']} ({rendah['mean']:,.2f}/hari, {int(rendah['count'])} hari).")
st.write("- Cuaca Clear umumnya menghasilkan rata-rata penyewaan lebih tinggi daripada Cloudy dan Light Rain/Snow.")
st.write("- Kombinasi dengan jumlah hari sedikit perlu ditafsirkan dengan hati-hati.")

# Conclusion
st.header("Conclusion")
st.markdown(
    """
**Pertanyaan 1**
- Sepanjang 2011–2012, rata-rata penyewaan per jam pada hari kerja (193,21) sedikit lebih tinggi daripada bukan hari kerja (181,41).
- Hari kerja memuncak pukul 17.00 (525,29), sedangkan bukan hari kerja memuncak pukul 13.00 (372,73).

**Pertanyaan 2**
- Rata-rata harian tertinggi: Fall dengan cuaca Clear (5.878,26 penyewaan/hari, 136 hari).
- Rata-rata harian terendah: Spring dengan cuaca Light Rain/Snow (934,75 penyewaan/hari, 4 hari).

**Rekomendasi**
- Tambah ketersediaan sepeda pada hari kerja pukul 07.00–08.00 dan 17.00–18.00, serta pada bukan hari kerja sekitar pukul 13.00.
- Sesuaikan jumlah armada dengan musim dan cuaca: tingkatkan pada Fall saat cuaca cerah, dan sesuaikan strategi operasional atau promosi saat cuaca kurang mendukung.
"""
)