# Analysis Preview

## 1. Statistical Question
I want to test whether Bitcoin daily returns are different on Fear days compared to Greed days.

## 2. Outcome Variable
The outcome variable is `btc_daily_return`.

## 3. Grouping Variable
The grouping variable is `fear_greed_label`.

## 4. Binary Variable
I created `positive_return`, which shows whether the Bitcoin daily return was positive or not.
This can be useful for a proportion-based z-test in Part 2.

## 5. Hypotheses
Null hypothesis (H0): The mean Bitcoin daily return is the same on Fear days and Greed days.

Alternative hypothesis (H1): The mean Bitcoin daily return is different on Fear days and Greed days.

## 6. Best Test
A two-sample t-test may be the best choice because it compares the mean return between two groups.