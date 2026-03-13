# Connecting Power BI to the SQLite Database

Since all the data generation, ETL cleaning, validation, and analytics are handled by our Python backend, the data sitting in your SQLite database is perfectly prepped for Power BI!

Here is the step-by-step guide to connect Power BI Desktop to our local database and build your visualizations.

## Step 1: Install the SQLite ODBC Driver
Power BI cannot natively connect to SQLite without an ODBC (Open Database Connectivity) driver.

1. Download the 64-bit SQLite ODBC driver for Windows:
   - Go to: http://www.ch-werner.de/sqliteodbc/
   - Download the file named: `sqliteodbc_w64.exe`
2. Run the installer and complete the setup (accepting default settings is fine).

## Step 2: Set up the System DSN (Data Source Name)
1. In Windows Search, type **"ODBC Data Sources (64-bit)"** and open the app.
2. Go to the **System DSN** tab.
3. Click **Add...**
4. Select **SQLite3 ODBC Driver** and click **Finish**.
5. A configuration dialog will appear:
   - **Data Source Name**: Enter `FinancialDataDB`
   - **Database Name**: Click **Browse** and navigate to your project folder: `C:\Users\Priyansh PC\Desktop\DA\database\financial_data.db`
6. Click **OK** on both windows.

## Step 3: Connect Power BI to the Database
1. Open **Power BI Desktop**.
2. From the Home ribbon, click **Get Data** → **More...**
3. In the search box, type `ODBC`.
4. Select **ODBC** and click **Connect**.
5. In the Data Source Name (DSN) dropdown, select the `FinancialDataDB` you just created.
6. Click **OK**.
7. If prompted for credentials, select **Windows** or **Default/Custom** (no username/password is needed for local SQLite) and click **Connect**.

## Step 4: Import the Tables
The Navigator window will appear, showing the tables in your database. Check the boxes next to the following 5 tables to load them:
- `transactions`
- `ledger_entries`
- `quality_log`
- `anomaly_log`
- `benchmarks`

Click **Load** (or **Transform Data** if you want to inspect them in Power Query first).

## Step 5: Build Your Dashboards!

Now you can recreate the interactive Dash web experience inside Power BI:

### 1. Data Modeling (Model View)
- Create a relationship linking `transaction_id` in the **transactions** table to `transaction_id` in the **ledger_entries** and **anomaly_log** tables.

### 2. Suggested Visualizations
* **Executive Overview**: Use Card visuals for total transaction volume and average transaction amount. Use Line charts for `amount` by `transaction_date` to show revenue/expense trends over time.
* **Data Quality**: Build a matrix or table visual using the `quality_log` showing `check_name`, `severity`, and `pass_rate` (apply conditional formatting to highlight critical severity!).
* **Anomaly Detection**: Use a Scatter chart with `anomaly_score` on the X-axis and `amount` on the Y-axis. Filter by `anomaly_type` to visualize the detected statistical outliers.
* **Reconciliation**: Use a Waterfall chart or Stacked Bar showing matched vs. mismatched transaction counts.

With both the Python/Dash web app codebase in your GitHub and a `.pbix` file showing BI expertise, you've got an incredibly strong portfolio piece!
