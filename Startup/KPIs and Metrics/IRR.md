**IRR**, or **Internal Rate of Return**, is a financial metric used to estimate the profitability of an investment. It represents the discount rate at which the net present value ([[NPV]]) of all future cash flows (both incoming and outgoing) from an investment equals zero. In simpler terms, it’s the rate of return an investment is expected to generate over its lifetime.

### Key Concept:

- **IRR** is expressed as a percentage and helps evaluate the attractiveness of an investment or project.
- It’s a more detailed metric than ROI because it considers the timing and size of cash flows.

### Formula:

IRR is calculated using the [[NPV]] formula, setting [[NPV]] to zero and solving for the discount rate (**IRR**):

0=∑t=1nCt(1+IRR)t−C00 = \sum_{t=1}^{n} \frac{C_t}{(1 + IRR)^t} - C_0

Where:

- CtC_t: Cash inflow or outflow at time tt.
- C0C_0: Initial investment (cash outflow at t=0t = 0).
- tt: Time period.
- nn: Total number of periods.

Since solving this equation analytically is complex, IRR is typically calculated using spreadsheet tools (like Excel's **=IRR()**) or financial calculators.

### Example:

Suppose you invest $1,000 in a project, and it generates the following cash flows over 3 years:

|Year|Cash Flow ($)|
|---|---|
|0|-1,000|
|1|400|
|2|500|
|3|600|

Using software or a financial calculator, you find the IRR is **18.1%**. This means the project is expected to generate an 18.1% annual return.

### Why Is IRR Important?

1. **Investment Evaluation**:
    
    - If the IRR is greater than the company’s required rate of return (hurdle rate), the investment is considered attractive.
2. **Project Comparison**:
    
    - IRR is useful for comparing multiple projects, especially when resources are limited.
3. **Cash Flow Sensitivity**:
    
    - Accounts for the timing of cash flows, unlike simpler metrics like ROI.

### Limitations:

1. **Assumes Reinvestment**:
    
    - IRR assumes that intermediate cash flows are reinvested at the same IRR, which may not be realistic.
2. **Multiple IRRs**:
    
    - For projects with non-conventional cash flows (e.g., alternating inflows and outflows), there may be multiple IRRs, making interpretation challenging.
3. **Ignores Scale**:
    
    - A small project might have a high IRR but generate less total profit than a larger project with a lower IRR.

### IRR vs [[NPV]]:

- **IRR** gives the rate of return as a percentage, while **[[NPV]]** provides a dollar value of the investment's profitability.
- **[[NPV]]** is preferred when cash flow amounts and project scales differ, while **IRR** is often used for quick comparisons.

### Applications:

- Evaluating capital investment projects.
- Comparing potential acquisitions or mergers.
- Assessing venture capital and private equity opportunities.