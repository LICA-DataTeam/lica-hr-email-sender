# lica hr email

# Flow

1. `GSheetUtil` -> extract and collect list of emails from Google Spreadsheet
2. Build Looker Studio URL
3. Run web automation (Playwright)

    1. Use the params filter in the Looker Studio URL

        1. Input each name, month, year from the list in the param

        2. Generate the report card (Download PDF)
4. Run email automation (`GmailUtil`)