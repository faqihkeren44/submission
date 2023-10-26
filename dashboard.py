import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency


def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    return monthly_orders_df


orders = pd.read_csv("orders.csv")
order_items = pd.read_csv("order_items.csv")


orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders.sort_values(by="order_purchase_timestamp", inplace=True)
orders.reset_index(inplace=True)


datetime_columns = ["shipping_limit_date", "review_creation_date", "review_answer_timestamp"]
 
for column in datetime_columns:
    order_items[column] = pd.to_datetime(order_items[column])


min_date = orders["order_purchase_timestamp"].min()
max_date = orders["order_purchase_timestamp"].max()
 
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = orders[(orders["order_purchase_timestamp"] >= str(start_date)) & 
                (orders["order_purchase_timestamp"] <= str(end_date))]


monthly_orders_df = create_monthly_orders_df(main_df)


st.header('E-Commerce Public Dashboard')


st.subheader('Daily Orders')
col1, col2 = st.columns(2)
with col1:
    total_orders = monthly_orders_df.order_id.sum()
    st.metric("Total orders", value=total_orders)
with col2:
    total_payment = format_currency(monthly_orders_df.payment_value.sum(), "AUD", locale='es_CO') 
    st.metric("Total Payment", value=total_payment)
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_id"],
    linewidth=2,
    color="#90CAF9",
)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

order_by_state = orders.groupby(by="customer_state")["order_id"].nunique().reset_index()
order_by_state = order_by_state.sort_values(by='order_id', ascending=False)
order_by_state.columns = ['state', 'order_total']

up_state_6 = order_by_state.iloc[5:27]
up_state_6 = pd.DataFrame([
    ["Others", up_state_6["order_total"].sum()]],
    columns=["state", "order_total"])
order_by_state5 = pd.concat([up_state_6, order_by_state.head()])
order_by_state5.sort_values(by="order_total", ascending=False).reset_index()
st.subheader("Top 5 Payment State")

fig, ax = plt.subplots()
ax.pie(
    x = order_by_state5["order_total"],
    labels = order_by_state5["state"],
    autopct = "%1.1f%%",
    explode = (0, 0.1, 0, 0, 0, 0),
)
st.pyplot(fig)

low5 = order_by_state.iloc[5:27]
low5.sort_values(by="order_total", ascending=False)

fig, ax = plt.subplots()
colors = ["#07e60e"]
sns.barplot(x="state", y="order_total", data=low5, palette=colors)
plt.ylabel(None)
plt.xlabel(None)
plt.title("Payment State Under 5th rank", loc="center")
plt.tick_params(axis='x', labelsize=10)
st.pyplot(fig)


id = order_items.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index()

st.subheader("Best and Worst Product by Total Ordering")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#07e60e", "#6dde70", "#6dde70", "#6dde70", "#6dde70"]
sns.barplot(x="order_id", y="product_category_name_english", data=id.head(), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None, fontsize=30)
ax[0].set_title("Most Sold Product", loc="center", fontsize=60)
ax[0].tick_params(axis='y', labelsize=50)
ax[0].tick_params(axis='x', labelsize=50)
sns.barplot(x="order_id", y="product_category_name_english", data=id.sort_values(by="order_id", ascending=True).head(), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None, fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Least Sold Product", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis='x', labelsize=50)
st.pyplot(fig)


score = order_items.review_score.mean()
score_data = order_items.groupby("product_category_name_english").review_score.mean().sort_values(ascending=False).reset_index()

st.subheader("Best and Worst Product by Review")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#07e60e", "#6dde70", "#6dde70", "#6dde70", "#6dde70"]
sns.barplot(x="review_score", y="product_category_name_english", data=score_data.head(), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=60)
ax[0].tick_params(axis='y', labelsize=50)
ax[0].tick_params(axis='x', labelsize=50)
sns.barplot(x="review_score", y="product_category_name_english", data=score_data.sort_values(by="review_score", ascending=True).head(), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None, fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=50)
ax[1].tick_params(axis='x', labelsize=50)
st.pyplot(fig)

