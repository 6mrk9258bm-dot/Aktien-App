
import streamlit as st 
import yfinance as yf
import plotly.graph_objects as go

st.title(" 📈Aktien Dashboard")

#Eingaben
tickers_input = st.text_input("Aktien-Symbole eingeben und mit Komma trennen(z.B AAPL, MSFT, TSLA)", value = "AAPL")
period = st.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y", "2y"])

#Symbole aufteilen und bereinigen
tickers = [t.strip().upper() for t in tickers_input.split(",")]

#Daten laden
fig = go.Figure()
has_data = False


for ticker in tickers:
    data = yf.download(ticker, period=period, auto_adjust=True)
    data.columns = data.columns.get_level_values(0)

    if data.empty:
        st.warning(f"Keine Daten für {ticker} gefunden.")
        continue

    has_data = True 

    #Candlestick nur wenn Aktie
    if len(tickers) == 1:
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name=ticker
        ))
    else:
        #Linechart für mehrere Aktien
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name=ticker
        ))

    #Gleitende Durchschnitte
    if len(data) >= 50:
        ma50 = data["Close"].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index, y=ma50,
            mode="lines",
            name=f"{ticker} MA50",
            line=dict(dash="dash", width=1)
        ))

    if len(data) >= 200:
        ma200 = data["Close"].rolling(window=200).mean()
        fig.add_trace(go.Scatter(
            x=data.index, y=ma200,
            mode="lines",
            name=f"{ticker} MA200",
            line=dict(dash="dot", width=1)
        ))

    #Kennzahlen bei einer Aktie
    if len(tickers) == 1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Aktueller Kurs", f"${float(data['Close'].iloc[-1]):.2f}")
        col2.metric("Höchstkurs", f"${float(data['High'].max()):.2f}")
        col3.metric("Tiefstkurs", f"${float(data['Low'].min()):.2f}")

fig.update_layout(
    title="Kursverlauf: " + ", ".join(tickers),
    xaxis_rangeslider_visible=False
)

if has_data:
    st.plotly_chart(fig, use_container_width=True)

#News
if has_data:
    st.subheader("📰 Aktuelle News")
    for ticker in tickers:
        st.markdown(f"### {ticker}")
        try:
            news = yf.Ticker(ticker).news
            if not news:
                st.write("Keine News gefunden.")
            else:
                for article in news[:5]:
                    content = article.get("content", {})
                    title = content.get("title", "Kein Titel")
                    url = content.get("canonicalUrl", {}).get("url", "#")
                    st.markdown(f"- [{title}]({url})")
        except Exception:
            st.write("News konnten nicht geladen werden.")

#Bash: streamlit run "/Users/eileenikuye/Desktop/Mini Projekt/app.py"
