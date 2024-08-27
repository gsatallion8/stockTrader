import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
import talib

# Function to get stock data and calculate indicators
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    # Calculate technical indicators
    df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
    df['SMA_200'] = talib.SMA(df['Close'], timeperiod=200)
    df['EMA_12'] = talib.EMA(df['Close'], timeperiod=12)
    df['EMA_26'] = talib.EMA(df['Close'], timeperiod=26)
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    df['MACD'], df['Signal_Line'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['Upper_Band'], df['Middle_Band'], df['Lower_Band'] = talib.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['Stochastic_K'], df['Stochastic_D'] = talib.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowd_period=3)
    df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    df['SAR'] = talib.SAR(df['High'], df['Low'], acceleration=0.02, maximum=0.2)

    # Buy/Sell Signals
    df['Buy_Signal'] = (
        (df['MACD'] > df['Signal_Line']) &  # MACD crossover
        (df['RSI'] < 30) |  # RSI oversold
        (df['Close'] < df['Lower_Band']) |  # Price below lower Bollinger band
        (df['ADX'] > 20) & (df['EMA_12'] > df['EMA_26'])  # ADX confirms trend strength
    )

    df['Sell_Signal'] = (
        (df['MACD'] < df['Signal_Line']) &  # MACD crossover
        (df['RSI'] > 70) |  # RSI overbought
        (df['Close'] > df['Upper_Band']) |  # Price above upper Bollinger band
        (df['ADX'] > 20) & (df['EMA_12'] < df['EMA_26'])  # ADX confirms trend strength
    )

    # Target Prices using recent price swings or Fibonacci levels
    df['Target_Buy_Price'] = df['Close'] * 1.05  # Hypothetical 5% above current price
    df['Target_Sell_Price'] = df['Close'] * 0.95  # Hypothetical 5% below current price

    return df

# Function to plot data and signals
def plot_signals(ticker, period):
    df = get_stock_data(ticker, period)
    
    plt.figure(figsize=(20, 12))
    
    # Plot stock prices and buy/sell signals
    plt.subplot(4, 1, 1)
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.scatter(df.index[df['Buy_Signal']], df['Close'][df['Buy_Signal']], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(df.index[df['Sell_Signal']], df['Close'][df['Sell_Signal']], marker='v', color='red', label='Sell Signal', alpha=1)
    plt.plot(df.index, df['Upper_Band'], label='Upper Bollinger Band', linestyle='--', color='gray')
    plt.plot(df.index, df['Lower_Band'], label='Lower Bollinger Band', linestyle='--', color='gray')
    
    plt.title(f"{ticker} Stock Price with Buy/Sell Signals and Technical Indicators")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Plot MACD and Signal Line
    plt.subplot(4, 1, 2)
    plt.plot(df.index, df['MACD'], label='MACD', color='orange')
    plt.plot(df.index, df['Signal_Line'], label='Signal Line', color='purple')
    plt.title('MACD and Signal Line')
    plt.xlabel('Date')
    plt.legend()

    # Plot RSI and Stochastic Oscillator
    plt.subplot(4, 1, 3)
    plt.plot(df.index, df['RSI'], label='RSI', color='red')
    plt.plot(df.index, df['Stochastic_K'], label='Stochastic %K', color='magenta')
    plt.plot(df.index, df['Stochastic_D'], label='Stochastic %D', color='cyan')
    plt.axhline(30, color='green', linestyle='--')
    plt.axhline(70, color='red', linestyle='--')
    plt.title('RSI and Stochastic Oscillator')
    plt.xlabel('Date')
    plt.legend()

    # Plot SAR and ADX
    plt.subplot(4, 1, 4)
    plt.plot(df.index, df['SAR'], label='SAR', color='blue')
    plt.plot(df.index, df['ADX'], label='ADX', color='orange')
    plt.axhline(20, color='green', linestyle='--')
    plt.title('SAR and ADX')
    plt.xlabel('Date')
    plt.legend()
    

    plt.tight_layout()
    
    # Save plot to file
    plt_path = "plot.png"
    plt.savefig(plt_path)
    plt.close()
    
    return plt_path

# Gradio Interface
def analyze_stock(ticker, period):
    plot_path = plot_signals(ticker, period)
    return plot_path

# Gradio app using the latest syntax
with gr.Blocks() as demo:
    gr.Markdown("# Stock Market Analyzer with Buy/Sell Signals and Technical Indicators")
    gr.Markdown("Enter a stock ticker and select a time period to visualize the buy/sell signals, target prices, and key technical indicators.")
    
    with gr.Row():
        ticker_input = gr.Textbox(label="Stock Ticker (e.g., AAPL)", placeholder="Enter stock ticker")
        period_input = gr.Dropdown(choices=["1mo", "3mo", "6mo", "1y", "5y"], label="Period", value="1y")
    
    analyze_button = gr.Button("Analyze")
    
    # Output: Show the plotted image
    plot_output = gr.Image(label="Stock Analysis Plot")

    # Function triggered on button click
    analyze_button.click(analyze_stock, inputs=[ticker_input, period_input], outputs=plot_output)

demo.launch()
