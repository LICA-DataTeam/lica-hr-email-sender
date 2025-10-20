# lica hr email

# Flow

1. `GSheetUtil` -> extract and collect list of emails from Google Spreadsheet
2. Build Looker Studio URL
3. Run web automation (Playwright)

    1. Use the params filter in the Looker Studio URL

        1. Input each name, month, year from the list in the param

        2. Generate the report card (Download PDF)
4. Run email automation (`GmailUtil`)

---

### TO DO

- [ ] ~~Dynamic date parameters in `app/routes/app.py`~~

#### Notes

**End-to-End flow for `feat-batch-send-by-branch-sc`**

1. Collect SC roster

2. Group by branch

3. Link employees to their PDFs

4. Assemble branch email content

    - Craft per-branch email content.

5. Build recipient list per branch

6. Send one email per branch

    - Iterate over the branch map. For each branch, call the `Gmail` service once with the branch-specific subject/body and the assembled recipient list. If you plan to attach PDFs, extend `GmailService.send_email()` to accept attachments before wiring it in. Keep the call inside a `try/except` so one branch's failure doesn't cancel the entire batch.