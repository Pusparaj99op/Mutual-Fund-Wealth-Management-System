# Federal Wealth Management System
## Problem Statement Title:
AI-Based Mutual Fund Wealth Management System.

## Problem Statement Description:
Develop an AI/ML-powered system for middle-class investors using Indian mutual fund data to analyze historical trends, predict future performance, and recommend suitable funds based on AMC, category, investment amount, and tenure.

## Problem:
The problem domain concerns wealth management for the common middle class people, focusing on Mutual Funds. Now why this topic there are very limited technique or wealth management like FDs, Stocks Trading, Crypto, Estate Planning, Corporate Bonds etc. However, all of them require time, focus, significant capital, involve risk  factors, and offer limited interest rates. Mutual funds are investment vehicles that pool money from multiple investors to invest in a diversified portfolio of securities such as stocks, bonds, money market instruments, where they are managed by an asset management company (AMC).

## dataset: /PS/dataset/Clean_MF_India_AI.csv

## terms of dataset: Data Parameters for Mutual Funds India (MF_India_AI.csv):
Scheme Name: Name of the mutual fund scheme
Min sip: Min sip amount required to start.
Min lumpsum: Min lumpsum amount required to start.
Expense ratio: calculated as a percentage of the Scheme's average Net Asset Value (NAV).
Fund size: the total amount of money that a mutual fund manager must oversee and invest.
Fund age: years since inception of scheme
Fund manager: A fund manager is responsible for implementing a fund's investment strategy and managing its trading activities.
Sortino : Sortino ratio measures the risk-adjusted return of an investment asset, portfolio, or strategy
Alpha: Alpha is the excess returns relative to market benchmark for a given amount of risk taken by the scheme
Standard deviation: A standard deviation is a number that can be used to show how much the returns of a mutual fund scheme are likely to deviate from its average annual returns.
Beta: Beta in a mutual fund is often used to convey the fund's volatility (gains or losses) in relation to its respective benchmark index
Sharpe: Sharpe Ratio of a mutual fund reveals its potential risk-adjusted returns
Risk level:
1- Low risk
2- Low to moderate
3- Moderate
4- Moderately High
5- High
6- Very High
AMC name: Mutual fund house managing the assets.
Rating: 0-5 rating assigned to scheme
Category: The category to which the mutual fund belongs (e.g. equity, debt, hybrid)
Sub-category : It includes category like Small cap, Large cap, ELSS, etc.
Return_1yr (%): The return percentage of the mutual fund scheme over 1 year.
Return_3yr (%): The return percentage of the mutual fund scheme over 3 year.
Return_5yr (%): The return percentage of the mutual fund scheme over 5year.

## Expected Outcomes:
We have live web scraped data of Mutual Funds India, our goal is to present descriptive analysis to understand this data and their patterns, then make predictions on the given data to forecast the future performance of specific mutual funds, develop a dashboard to display past data and projections Finally, create an AI-based recommendation system for selected inputs: AMC Name, Category, Amount Invested, Tenure.
