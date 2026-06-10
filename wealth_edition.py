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
    ##This table shows how what the final rank and score are based on the above variables
    """)
    return


@app.cell
def _(scored_df):
    scored_df[["zcta", "cbsa_name", "rank", "wealth_score", ]]
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
        return df.sort_values("wealth_score", ascending=False), weights


    scored_df, weights = compute_wealth_score(df)
    return (scored_df,)


@app.cell
def _(mo):
    mo.md("""
    ## And this one shows which ZIPs are changing the most based on adjustments to the sliders
    """)
    return


@app.cell
def _(df, scored_df):
    # only compute once
    baseline_weights = {
        "age_variable": 25,
        "savings_variable": 0.10,
        "equity_variable": 0.50,
        "poverty_variable": 0,
    }

    def baseline_scores(df):
        df = df.copy()

        df["baseline_score"] = (
            (df["population_per_square_mile"] * (df["income_per_capita"] * (df["median_age"] - baseline_weights["age_variable"]) * baseline_weights["savings_variable"]) +
            (df["population_per_square_mile"] * (((df["housing_units"] * df["hu_pct_occupied"]) * df["occupied_hu_pct_owner_occupied"]) * df["ZILLOW Typical Home Values"]) / df["pop_total"] * baseline_weights["equity_variable"]))
        )
        return df


    df_base = baseline_scores(df)

    merged = scored_df.merge(
        df_base[["zcta", "baseline_score"]], on="zcta"
    )

    merged["rank"] = merged["wealth_score"].rank(ascending=False)
    merged["baseline_rank"] = merged["baseline_score"].rank(ascending=False)

    merged["rank_change"] = merged["baseline_rank"] - merged["rank"]

    merged[["zcta", "rank", "cbsa_name", "wealth_score", "rank_change"]].sort_values("rank_change", ascending=False)
    return


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


if __name__ == "__main__":
    app.run()
