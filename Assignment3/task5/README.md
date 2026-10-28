Assumptions:

1) ### Approximating yields for endering bonds
- FRED only publishes yields at fixed maturities: 1y, 2y, 3y, 5y, 7y, 10y.
- After one month, the 2y bond is a 1y11m bond. The 10y bond is a 9y11m bond. FRED has no yields for any of those.
- We fill the gap with a straight line between the two nearest points:
  - **2y leg:** line from 1y (`DGS1`) to 2y (`DGS2`). Monthly roll = (2y − 1y) / 12.
  - **10y leg:** line from 7y (`DGS7`) to 10y (`DGS10`). Monthly roll = (10y − 7y) / 3 / 12. We use the 7y because FRED has no 8y or 9y.

2) ### Data
- FRED daily series (`DGS1`, `DGS2`, `DGS7`, `DGS10`, `DTB3`), January 2000 – latest month.
- Days with any missing value are dropped before taking month-end values.

3) ### Carry
- Carry = coupon income − financing cost, per month.
- Financing at the 3-month T-bill rate (`DTB3`), as a proxy for the repo rate. `DTB3` is quoted on a discount basis, slightly below a bond-equivalent yield.
- Carry and roll use yields at the start of each month (`.shift(1)`).


## Completed analysis

The additional analysis is appended to `HW2_T5.ipynb`; the original code cells are unchanged. Use the added section for the final results. See [task5_notes.md](task5_notes.md) for its full assumptions and run instructions, and [task5_report.md](task5_report.md) for the written report.
