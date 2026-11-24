import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# CSS to center the elements
st.markdown(
    """
    <style>
    .center {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Centering the headers
st.markdown(
    "<h1 class='center'>An EsteStyle Streamlit Page<br>Where Python Wiz Meets Data Viz!</h1>",
    unsafe_allow_html=True,
)
st.markdown("<h1 class='center'></h1>", unsafe_allow_html=True)

st.markdown(
    "<img src='https://1drv.ms/i/s!ArWyPNkF5S-foZspwsary83MhqEWiA?embed=1&width=307&height=307' width='300' style='display: block; margin: 0 auto;'>",
    unsafe_allow_html=True,
)

st.markdown("<h1 class='center'> </h1>", unsafe_allow_html=True)

st.markdown(
    "<h1 class='center'>Multi-Stock Comparision App</h1>", unsafe_allow_html=True
)

st.markdown("<h1 class='center'> </h1>", unsafe_allow_html=True)

st.markdown(
    "<h3 class='center'>- Analysis to compare historical data of stocks</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 class='center'>- Stocks analyzed are identified by their ticker symbols</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 class='center'>- All stock analysis done with data from Yahoo Finance</h3>",
    unsafe_allow_html=True,
)

st.markdown("<h1 class='center'> </h1>", unsafe_allow_html=True)

ticker_symbol_data = {
    "Company Name": [
        "Apple",
        "NVIDIA",
        "Microsoft",
        "Alphabet",
        "Amazon",
        "Meta Platforms",
        "Berkshire Hathaway",
        "Broadcom",
        "Tesla",
        "Eli Lilly",
        "Walmart",
        "JPMorgan Chase",
        "Visa",
        "Exxon Mobil",
        "United Health",
        "Oracle",
        "Mastercard",
        "Procter & Gamble",
        "Costco",
        "Home Depot",
        "Johnson & Johnson",
        "AbbVie",
        "Bank of America",
        "Netflix",
        "Salesforce",
        "Coca-Cola",
        "Chevron",
        "Advanced Micro Devices",
        "Merck",
        "T-Mobile",
        "PepsiCo",
        "Accenture",
        "Linde",
        "Cisco Systems",
        "Wells Fargo",
        "Adobe",
        "McDonald's",
        "Thermo Fisher Scientific",
        "Philip Morris",
        "Abbott Laboratories",
        "ServiceNow",
        "QUALCOMM",
        "International Business Machines",
        "Texas Instruments",
        "Morgan Stanley",
        "American Express",
        "General Electric",
        "Caterpillar",
        "Intuitive Surgical",
        "Danaher",
    ],
    "Ticker Symbol": [
        "AAPL",
        "NVDA",
        "MSFT",
        "GOOGL",
        "AMZN",
        "META",
        "BRK-B",
        "AVGO",
        "TSLA",
        "LLY",
        "WMT",
        "JPM",
        "V",
        "XOM",
        "UNH",
        "ORCL",
        "MA",
        "PG",
        "COST",
        "HD",
        "JNJ",
        "ABBV",
        "BAC",
        "NFLX",
        "CRM",
        "KO",
        "CVX",
        "AMD",
        "MRK",
        "TMUS",
        "PEP",
        "ACN",
        "LIN",
        "CSCO",
        "WFC",
        "ADBE",
        "MCD",
        "TMO",
        "PM",
        "ABT",
        "NOW",
        "QCOM",
        "IBM",
        "TXN",
        "MS",
        "AXP",
        "GE",
        "CAT",
        "ISRG",
        "DHR",
    ],
}

st.caption(f"yfinance version: {yf.__version__}")
@st.cache_data(ttl=3600, show_spinner=False)
def debug_fetch(ticker: str, start_date, end_date):
  clean_ticker = ticker.strip().upper()
  start_str = pd.Timestamp(start_date).strftime("%Y-%m-%d")
  end_str = pd.Timestamp(end_date).strftime("%Y-%m-%d")

  try:
    df = yf.download(
        clean_ticker,
        start=start_str,
        end=end_str,
        progress=False,
        threads=False,
        auto_adjust=False,
    )
    if df is None or df.empty:
      st.warning(
          f"[{clean_ticker}] yf.download returned empty for {start_str} ->"
          f" {end_str}"
      )
      return None

    # Handle MultiIndex columns if yfinance returns (Price, Ticker)
    if isinstance(df.columns, pd.MultiIndex):
      if "Close" in df.columns.get_level_values(0):
        close_col = df["Close"]
        if isinstance(close_col, pd.DataFrame):
          close_series = close_col.iloc[:, 0]
        else:
          close_series = close_col
      else:
        st.warning(
            f"[{clean_ticker}] No 'Close' level in columns: {list(df.columns)}"
        )
        return None
    else:
      if "Close" not in df.columns:
        st.warning(f"[{clean_ticker}] No 'Close' column in: {list(df.columns)}")
        return None
      close_series = df["Close"]

    close_series = close_series.dropna()
    if close_series.empty:
      st.warning(f"[{clean_ticker}] 'Close' series was all NaN.")
      return None

    clean_df = pd.DataFrame({"Close": close_series})
    start_price = float(clean_df["Close"].iloc[0])
    end_price = float(clean_df["Close"].iloc[-1])

    return {
        "data": clean_df,
        "start_price": start_price,
        "end_price": end_price,
        "price_difference": end_price - start_price,
    }
  except Exception as e:
    st.error(f"[{clean_ticker}] Exception during fetch: {type(e).__name__}: {e}")
    return None


def compute_risk_return(df: pd.DataFrame):
    daily_returns = df["Close"].pct_change().dropna()
    if daily_returns.empty:
        return None, None
    return float(daily_returns.mean()), float(daily_returns.std())


# Create Streamlit app
col_list = st.columns([1, 2, 1, 2, 1])

# Initialize session state for the number of assets and tickers list
if "num_of_assets" not in st.session_state:
    st.session_state.num_of_assets = 1

if "tickers" not in st.session_state:
    st.session_state.tickers = []

with col_list[1]:
    st.title("Total Stocks")
    st.session_state.num_of_assets = st.number_input(
        "How many stocks do you want to analyze?",
        min_value=1,
        max_value=100,
        value=st.session_state.num_of_assets,
    )

with col_list[1]:
    st.write("")
    if st.button("Create Ticker Id Fields"):
        st.session_state.tickers = [
            "" for _ in range(st.session_state.num_of_assets)
        ]

with col_list[3]:
    st.title("Date Range")
    start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))

# If tickers were created, display ticker input fields
if st.session_state.tickers:
    with col_list[1]:
        st.title("Stock Ids")
        for i in range(st.session_state.num_of_assets):
            st.session_state.tickers[i] = st.text_input(
                f"Enter stock ticker #{i + 1} (e.g., AAPL)",
                st.session_state.tickers[i],
            )

        st.write("")
        analysis_button = st.button("Perform Graphical Analysis")

    with col_list[3]:
        st.title("Ticker Id Ref")
        st.write("50 top tickers of the S&P 500 Index")
        st.dataframe(ticker_symbol_data)

    if analysis_button:
        active_tickers = [
            t.strip().upper() for t in st.session_state.tickers if t and t.strip()
        ]

        if not active_tickers:
            st.warning("Please enter at least one stock ticker symbol.")
        elif start_date >= end_date:
            st.warning("Start Date must be earlier than End Date.")
        else:
            results = {}
            for ticker in active_tickers:
                fetched = get_stock_data(ticker, start_date, end_date)
                if fetched is None:
                    st.warning(
                        f"Could not load valid price data for '{ticker}' in the selected date range."
                    )
                else:
                    results[ticker] = fetched

            valid_tickers = list(results.keys())

            if not valid_tickers:
                st.error("No valid stock data available to plot.")
            else:
                ####### Logic for Stock Price Display #######
                st.title("")
                st.markdown(
                    "<h3 class='center'>- To visualize changing price value, Close Price over time is displayed</h3>",
                    unsafe_allow_html=True,
                )

                fig = go.Figure()
                for ticker in valid_tickers:
                    df = results[ticker]["data"]
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["Close"],
                            mode="lines",
                            name=ticker,
                        )
                    )

                fig.update_layout(
                    title="Stock Value as Close Price",
                    xaxis_title="Date",
                    yaxis_title="USD",
                )
                st.plotly_chart(fig)

                metrics_container = st.container()
                max_columns_per_row = 5

                for i in range(0, len(valid_tickers), max_columns_per_row):
                    row_tickers = valid_tickers[i : i + max_columns_per_row]
                    metric_col_list = st.columns(len(row_tickers))

                    for met_index, ticker in enumerate(row_tickers):
                        item = results[ticker]
                        start_price = round(item["start_price"], 2)
                        end_price = round(item["end_price"], 2)
                        price_difference = round(item["price_difference"], 2)

                        with metrics_container:
                            with metric_col_list[met_index]:
                                st.metric(
                                    label=f"Start: {start_price} | End: {end_price}",
                                    value=ticker,
                                    delta=f"${price_difference}",
                                )

                ####### Logic for Total Percent Change Display #######
                st.title("")
                st.markdown(
                    "<h3 class='center'>- Equalizing Initial Value: Analysis of Total Percent Change</h3>",
                    unsafe_allow_html=True,
                )

                fig = go.Figure()
                for ticker in valid_tickers:
                    df = results[ticker]["data"]
                    first_close = df["Close"].dropna().iloc[0]
                    pct_series = (df["Close"] / first_close - 1) * 100
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=pct_series,
                            mode="lines",
                            name=ticker,
                        )
                    )

                fig.update_layout(
                    title="Stock Value as Total Percent Change",
                    xaxis_title="Date",
                    yaxis_title="Percent Change (%)",
                )
                st.plotly_chart(fig)

                metrics_container = st.container()
                for i in range(0, len(valid_tickers), max_columns_per_row):
                    row_tickers = valid_tickers[i : i + max_columns_per_row]
                    metric_col_list = st.columns(len(row_tickers))

                    for met_index, ticker in enumerate(row_tickers):
                        item = results[ticker]
                        start_price = round(item["start_price"], 2)
                        end_price = round(item["end_price"], 2)
                        percent_change = round(
                            (item["end_price"] - item["start_price"])
                            / item["start_price"]
                            * 100,
                            2,
                        )

                        with metrics_container:
                            with metric_col_list[met_index]:
                                st.metric(
                                    label=f"Start: {start_price} | End: {end_price}",
                                    value=ticker,
                                    delta=f"{percent_change}%",
                                )

                ####### Logic for Risk vs Return Display #######
                st.title("")
                st.markdown(
                    "<h3 class='center'>- To quantify risk, using pct returns, compare expected return with std of daily return</h3>",
                    unsafe_allow_html=True,
                )

                risk_return_rows = []
                for ticker in valid_tickers:
                    exp_ret, risk_std = compute_risk_return(results[ticker]["data"])
                    if exp_ret is not None and risk_std is not None:
                        risk_return_rows.append({
                            "ticker": ticker,
                            "expected_return": exp_ret,
                            "risk": risk_std,
                        })

                if risk_return_rows:
                    rr_df = pd.DataFrame(risk_return_rows)
                    fig = go.Figure()
                    area = np.pi * 7

                    fig.add_trace(
                        go.Scatter(
                            x=rr_df["expected_return"],
                            y=rr_df["risk"],
                            mode="markers",
                            marker=dict(
                                size=area,
                                color=rr_df["expected_return"] * rr_df["risk"],
                                colorscale="Blues",
                                opacity=1,
                            ),
                            text=rr_df["ticker"],
                            hovertemplate="<b>%{text}</b><br>Expected Return: %{x:.4f}<br>Risk (Std Dev): %{y:.4f}<extra></extra>",
                        )
                    )

                    for _, row in rr_df.iterrows():
                        fig.add_annotation(
                            x=row["expected_return"],
                            y=row["risk"],
                            text=row["ticker"],
                            showarrow=True,
                            arrowhead=0,
                            ax=0,
                            ay=-50,
                            font=dict(color="black"),
                            bgcolor="white",
                            bordercolor="black",
                            borderwidth=1,
                            borderpad=4,
                        )

                    fig.update_layout(
                        title="Expected Return vs Risk",
                        xaxis_title="Expected Return",
                        yaxis_title="Risk (Std Dev)",
                        showlegend=False,
                    )
                    st.plotly_chart(fig)

                    metrics_container = st.container()
                    for i in range(0, len(risk_return_rows), max_columns_per_row):
                        row_items = risk_return_rows[i : i + max_columns_per_row]
                        metric_col_list = st.columns(len(row_items))

                        for met_index, rr_item in enumerate(row_items):
                            exp_pct = round(rr_item["expected_return"] * 100, 2)
                            risk_pct = round(rr_item["risk"] * 100, 2)

                            with metrics_container:
                                with metric_col_list[met_index]:
                                    st.metric(
                                        label=f"Expected Return {exp_pct}%",
                                        value=rr_item["ticker"],
                                        delta=f"Risk (Std): {risk_pct}%",
                                        delta_color="inverse",
                                    )
