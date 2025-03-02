### Working

- [ ] Add portfolio command that takes a file of stock symbols with corresponding weights and returns the expected return and volatility of the portfolio (according to MPT)
  - [ ] Compute the annualized returns for each stock
  - [ ] Compute the covariance matrix of the stocks returns
    - _NOTE_: The covariance matrix is computed using the stocks daily returns. Note that not all companies have been public for the same amount of time, so there will be discrepancies in the number of data points for each company. We will only consider companies that have been public for at least 4 years as a result (e.g. 252 trading days/yr \* 4 = ~1000 data points).

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
