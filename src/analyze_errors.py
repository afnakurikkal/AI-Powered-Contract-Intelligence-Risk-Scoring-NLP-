from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "reports" / "clause_classification_errors.csv"
OUTPUT_FILE = ROOT / "reports" / "top_label_confusions.csv"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required = {"label", "predicted_label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    summary = (
        df.dropna(subset=["label", "predicted_label"])
        .groupby(["label", "predicted_label"])
        .size()
        .reset_index(name="error_count")
        .rename(columns={"label": "actual_label"})
        .sort_values("error_count", ascending=False)
    )

    summary.to_csv(OUTPUT_FILE, index=False)

    print(f"Error records analyzed: {len(df)}")
    print(f"Summary saved to: {OUTPUT_FILE}")
    print("\nTop 10 label confusions:")
    print(summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()