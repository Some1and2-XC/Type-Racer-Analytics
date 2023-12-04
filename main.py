#!/usr/bin/env python3

import pandas as pd

# Defines Package constants
DATASET = "../type_racer.csv"

def get_comma_values(df, key: str, sep=", ") -> pd.DataFrame:
    """
    function for getting the comma values from a dataframe
    df: pd.DataFrame
        The dataframe that is being searched through
    key: str
        The key string to index df from
    """

    return df[df[key].notna()][key] \
        .map(lambda cv: cv.split(sep)) \
        .explode() \
        .to_frame() \
        .rename(columns = {0:key})


def replace_punctuation(input_value: str) -> str:
    input_value = input_value.lower()
    punctuation = ",./<>?;:\"[]{}`1234567890-=\\~!@#$%^&*()_+|"
    for character in punctuation:
        input_value = " ".join(input_value.split(character))
    return input_value


def get_word_averages(df) -> pd.DataFrame:
    """
    Gets average values for each word in the dataframe
    df:
        The dataframe that is being analyzed
    Returns:
        Dataframe of the averages for each word
    """

    # Replaces values in the Text field to not have puncuation
    df["Text"] = df["Text"].apply(replace_punctuation)

    # Gets word values from text column
    comma_values = get_comma_values(df, "Text", sep=" ")

    # Merges the words with the original data (without original text column)
    df = df \
        .loc[:, df.columns != "Text"] \
        .merge(
            comma_values,
            left_index = True,
            right_index = True
        )

    # Adds the value count back to the dataframe
    df = df.merge(
        comma_values.value_counts(),
        on="Text"
    )

    # Gets average values of each word
    word_averages = df \
        .groupby("Text") \
        .mean(numeric_only=True)

    # Gets all the values where the amount of instances is more than one
    # Also removes any values that are empty
    word_averages = word_averages[word_averages["count"] > 1] \
        .drop("", axis=0)

    return word_averages

def get_combined_words(df, index="count") -> str:
    """
    Function for getting the amount of words combined by their strings
    """
    return "".join(
        word_section for word_section in \
            (df.index + " ") * df[index] \
                .astype(int)
    )


# Reads CSV
df = pd.read_csv(DATASET)

# Gets the averages of the words
word_averages = get_word_averages(df)

# Combines the words for the worst words
print(1,
    get_combined_words(
        word_averages \
            .sort_values("Speed (WPM)") \
            .head(10)
    )
)

# Combines the words for the best words
print(2,
    get_combined_words(
        word_averages \
            .sort_values("Speed (WPM)", ascending=False) \
            .head(10)
    )
)

exit()

# Saves the Averages to CSV
print("Saving File!")
word_averages.to_csv("outfile.csv")
print(word_averages)
print("\t~ Finished")
