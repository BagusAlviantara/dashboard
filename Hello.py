import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_product_category_df(df):
    sum_product_category_df = df.groupby("product_category_name_english").product_id.nunique().sort_values(ascending=False).reset_index()
    return sum_product_category_df

def create_customer_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

def create_review_score_byrating_df(df):
    byrating_df = df.groupby(by="review_score").review_id.nunique().reset_index()
    byrating_df.rename(columns={
        "review_id": "rating_count"
    }, inplace=True)
    return byrating_df

def create_product_byscore_df(df):
    byscore_df = df.groupby(by="product_category_name_english").review_score.nunique().reset_index()
    byscore_df.rename(columns={
        "review_score": "rating_count"
    }, inplace=True)
    return byscore_df

def create_monthly_rating_score_df(df):
    rating_df= df[(df['order_purchase_timestamp'] >= '2017-01-31')]
    monthly_rating_df = rating_df.resample(rule='M', on='order_purchase_timestamp').agg({
        "review_id": "nunique",
        "review_score": "mean"
    })
    monthly_rating_df.index = monthly_rating_df.index.strftime('%Y-%m')
    monthly_rating_df = monthly_rating_df.reset_index()
    monthly_rating_df.rename(columns={
        "review_id": "nunique",
        "review_score": "mean"
    }, inplace=True)
    return monthly_rating_df

def create_customer_counts(df):
    customer_counts_df= df[(df['order_purchase_timestamp'] >= '2017-01-31')]
    customer_counts_df = customer_counts_df.resample(rule='M', on='order_purchase_timestamp').agg({
        "customer_id": "nunique"
    })
    customer_counts_df.index = customer_counts_df.index.strftime('%Y-%m')
    customer_counts_df = customer_counts_df.reset_index()
    customer_counts_df.rename(columns={
        "customer_id": "nunique"
    }, inplace=True)
    return customer_counts_df

def create_order_counts_df(df):
    order_counts_df= df[(df['order_purchase_timestamp'] >= '2017-01-31')]
    order_counts_df = order_counts_df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique"
    })
    order_counts_df.index = order_counts_df.index.strftime('%Y-%m')
    order_counts_df = order_counts_df.reset_index()
    order_counts_df.rename(columns={
        "order_id": "nunique"
    }, inplace=True)
    return order_counts_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "count", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
 
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
 
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

#load data sebagai sebuah dataframe
all_df = pd.read_csv("all_data.csv")

# columns to convert to datetime
columns_to_convert = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date', 'shipping_limit_date']
all_df[columns_to_convert] = all_df[columns_to_convert].apply(pd.to_datetime)

#mengurutkan DataFrame berdasarkan order_date
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


#memanggil dataframe yang telah dibuat
sum_product_category_df = create_sum_product_category_df(all_df)
bystate_df = create_customer_bystate_df(all_df)
byrating_df = create_review_score_byrating_df(all_df)
byscore_df = create_product_byscore_df(all_df)
monthly_rating_df = create_monthly_rating_score_df(all_df)
customer_counts_df = create_customer_counts(all_df)
order_counts_df = create_order_counts_df(all_df)
rfm_df = create_rfm_df(all_df)


#menambahkan header pada dashboard
st.header('Transaction Dashboard :sparkles:')

#menampilkan informasi tentang performa penjualan dari setiap produk
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors1 = ["#72BCD4", "#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_id", y="product_category_name_english", data=sum_product_category_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=15)
 
sns.barplot(x="product_id", y="product_category_name_english", data=sum_product_category_df.sort_values(by="product_id", ascending=True).head(5), palette=colors1, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=13)
plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=20)
st.pyplot(fig)


#menampilkan informasi demografi pelanggan
st.subheader("Customer Demographics")
fig, ax = plt.subplots(figsize=(24, 6))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors_,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


#menampilkan informasi kepuasan pelanggan terhadap product
st.subheader("Rating of Products")
fig, ax = plt.subplots(figsize=(24, 6)) 
colors2 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
sns.barplot(
    x="review_score", 
    y="rating_count",
    data=byrating_df.sort_values(by="rating_count", ascending=False),
    palette=colors2
)
ax.set_title("Rating of Products", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


#menampilkan informasi kepuasan pelanggan terhadap setiap product
st.subheader("Rating of Products Category")
fig, ax = plt.subplots(figsize=(24, 36)) 
colors__ = [
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4",
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4",
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4",
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4", 
    "#72BCD4",
    "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="rating_count", 
    y="product_category_name_english",
    data=byscore_df.sort_values(by="rating_count", ascending=False),
    palette=colors__
)
ax.set_title("Rating of Products Category", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


#menampilkan informasi kepuasan pelanggan setiap bulan
st.subheader("Average Review Score Over Time")
fig, ax = plt.subplots(figsize=(24, 6)) 
ax.plot(monthly_rating_df["order_purchase_timestamp"], monthly_rating_df["mean"], marker='o', linewidth=2) 
ax.set_title("Average Review Score Over Time", loc="center", fontsize=30)
ax.set_ylabel('Average Review Score')
ax.set_xlabel('Month')
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.grid(True)
st.pyplot(fig)


#menampilkan informasi jumlah pelanggan setiap bulan
st.subheader("Average of Customer Each Month")
fig, ax = plt.subplots(figsize=(24, 6)) 
ax.plot(customer_counts_df["order_purchase_timestamp"], customer_counts_df["nunique"], marker='o', linewidth=2) 
ax.set_title("Average of Customer Each Month", loc="center", fontsize=20) 
ax.set_xlabel('Month')
ax.set_ylabel('Average Customer')
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.grid(True)
st.pyplot(fig)


#menampilkan informasi jumlah pesanan setiap bulan
st.subheader("Average of Orders Each Month")
fig, ax = plt.subplots(figsize=(24, 6)) 
ax.plot(order_counts_df["order_purchase_timestamp"], order_counts_df["nunique"], marker='o', linewidth=2) 
ax.set_title("Average of Orders Each Month", loc="center", fontsize=20) 
ax.set_xlabel('Month')
ax.set_ylabel('Average Orders')
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.grid(True)
st.pyplot(fig)


#menampilkan informasi terkait parameter RFM (Recency, Frequency, & Monetary)
#menampilkan nilai average dari ketiga parameter tersebut
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=90)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)
 
st.pyplot(fig)