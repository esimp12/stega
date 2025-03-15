### Working

- [ ] Come up with an app architecture
  - MVP feature is daily price ingestion of SP500 tickers with a CLI tool to get portfolio returns and volatility

### Documentation

- [ ] add COPYING (license)
- [ ] add CONTRIBUTING.md
- [ ] update README.md
- [ ] document rate limit requirements
- [ ] document estimated size requirements (DB)
- [ ] add docstrings to all functions

### Backlog

- [ ] Update DB calls to bind all parameters
- [ ] Update DB to use context managers for handling connection/cursor objects
- [ ] Update requests to use Session context managers
- [ ] Scrape wikipedia for list of S&P500 companies
- [ ] Compute annualized returns for each company
- [ ] Prototype strategy for updating daily prices for each company (e.g. cron job that ingests data)
  - Validate we have no repeats (should not happen based on insertion query)
  - Validate we have no missing data (should not happen based on insertion query)
  - Update API call to only request data from last date in DB to today (wasteful to request more data)
  - Quick estimate of how long it will take to ingest data for ~500 companies, ~3000 companies, and ~N companies
