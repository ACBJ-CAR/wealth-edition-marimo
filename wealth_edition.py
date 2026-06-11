import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    return mo, pd


@app.cell
def _(pd):
    def load_data():
        return pd.read_csv(
            "https://raw.githubusercontent.com/ACBJ-CAR/wealth-edition-marimo/refs/heads/main/data/wealth_data_2023.csv"
        )

    df = load_data()
    return (df,)


@app.cell
def _(mo):
    w_age = mo.ui.slider(0, 100, value=25, step=1, label="Age variable", show_value=True)
    w_savings = mo.ui.slider(0, 1, value=0.10, step=0.1, label="Savings percentage variable", show_value=True)
    w_equity = mo.ui.slider(0, 1, value=0.50, step=0.1, label="Home equity percentage variable", show_value=True)
    w_poverty_rate = mo.ui.slider(0, 1, value=0, step=1, label="Poverty rate yes/no", show_value=True)
    return w_age, w_equity, w_poverty_rate, w_savings


@app.cell
def _(mo):
    mo.md("""
    #Adjust your variables here:
    Baseline variables: <br>
    Age of savings start: 25<br>
    Savings rate: 10% (0.1)<br>
    Average home equity rate: 50% (0.5)<br>
    Poverty rate included? No (0)
    """)
    return


@app.cell
def _(mo, w_age, w_equity, w_poverty_rate, w_savings):
    mo.vstack([
        w_age,
        w_savings,
        w_equity,
        w_poverty_rate,
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ##This table shows what the final rank and score are, as well as the difference in rank and score from the baseline, based on the above variables.
    """)
    return


@app.cell
def _(scored_df):
    scored_df.drop_duplicates(subset="zcta", inplace=True)
    scored_df["Difference in wealth score"] = scored_df["baseline_score"] - scored_df["wealth_score"]
    scored_df["Change in rank"] = scored_df["baseline_rank"] - scored_df["rank"]

    scored_df_reordered = scored_df[["zcta", "cbsa_name", "county_name", "state_name", "rank", "baseline_rank", "Change in rank","wealth_score", "baseline_score", "Difference in wealth score", "population_per_square_mile", "income_per_capita", "Median age - V1 x income per capita x V2 (income per capita*(median age-V1)*V2)", "Home equity per capita (housing units*%owner-occupied*median value)*V3", "poverty_rate", "pop_total", "pop_total.1", "area_land_sq_miles", "median_age", "median_age_male", "median_age_female", "pop_total_18_64", "pop_pct_18_64", "race_pct_nh_white", "race_pct_nh_black", "race_pct_nh_amerind_alaskan", "race_pct_nh_asian", "race_pct_nh_nhpi", "race_pct_nh_other", "race_pct_nh_two_plus", "race_pct_hispanic", "income_per_capita.1", "income_median_hh", "mean_travel_time_to_work", "housing_units", "hu_pct_occupied", "occupied_hu_pct_owner_occupied", "ZILLOW Typical Home Values", "educ_pct_hs_grad", "educ_pct_bachelors", "educ_pct_postgrad", "veteran_pct"]]
    scored_df_reordered.rename(columns={"rank": "new_rank"}, inplace=True)

    # scored_df.insert(0, "rank", rank_col)
    # scored_df.insert(5, "New wealth score", new_wealth_col)
    # scored_df.insert(6, "Old wealth score", old_wealth_col)

    scored_df_reordered
    return


@app.cell
def _(df, w_age, w_equity, w_poverty_rate, w_savings):
    def compute_wealth_score(df):
        weights = {
            "age_variable": w_age.value,
            "savings_variable": w_savings.value,
            "equity_variable": w_equity.value,
            "poverty_variable": w_poverty_rate.value,
        }

        baseline_weights = {
        "age_variable": 25,
        "savings_variable": 0.10,
        "equity_variable": 0.50,
        "poverty_variable": 0,
    }

        df = df.copy()
        base_wealth_score = (
        ((df["population_per_square_mile"] * (df["income_per_capita"] * (df["median_age"] - weights["age_variable"]) * weights["savings_variable"]) +
            (df["population_per_square_mile"] * (((df["housing_units"] * df["hu_pct_occupied"]) * df["occupied_hu_pct_owner_occupied"]) * df["ZILLOW Typical Home Values"]) / df["pop_total"] * weights["equity_variable"])))
        )

        if weights["poverty_variable"] > 0:
            df["wealth_score"] = base_wealth_score * (
                weights["poverty_variable"] * (1 - df["poverty_rate"] * 2)
            )
        else:
            df["wealth_score"] = base_wealth_score

        df["rank"] = df["wealth_score"].rank(ascending=False)

        df["baseline_score"] = (
            (df["population_per_square_mile"] * (df["income_per_capita"] * (df["median_age"] - baseline_weights["age_variable"]) * baseline_weights["savings_variable"]) +
             (df["population_per_square_mile"] * (((df["housing_units"] * df["hu_pct_occupied"]) * df["occupied_hu_pct_owner_occupied"]) * df["ZILLOW Typical Home Values"]) / df["pop_total"] * baseline_weights["equity_variable"]))
        )

        df["baseline_rank"] = df["baseline_score"].rank(ascending=False)

        return df.sort_values("rank", ascending=True), weights


    scored_df, weights = compute_wealth_score(df)
    return (scored_df,)


@app.cell
def _(scored_df):
    import altair as alt

    chart = alt.Chart(scored_df.head(20)).mark_bar().encode(
        x="wealth_score:Q",
        y=alt.Y("zcta:N", sort="-x"),
        tooltip=["zcta", "wealth_score"]
    )

    chart
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
