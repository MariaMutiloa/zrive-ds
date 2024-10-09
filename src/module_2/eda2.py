import os
import logging
import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from typing import Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

current_directory = os.getcwd()
env_file_path = os.path.join(current_directory, "keys.env")
env_exists = os.path.isfile(env_file_path)

logger.info(f"Does the keys.env file exist? {env_exists}")

if env_exists:
    load_dotenv(env_file_path)
else:
    logger.warning("The keys.env file was not found.")

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

if aws_access_key is None or aws_secret_key is None:
    raise ValueError(
        "AWS environment variables did not load correctly. Check the keys.env file."
    )

try:
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )
    s3 = session.client("s3")
except Exception as e:
    logger.critical(f"Failed to create AWS session: {e}")
    exit(1)

bucket_name = "zrive-ds-data"
s3_key = "groceries/box_builder_dataset/feature_frame.csv"
local_file = "feature_frame.csv"

try:
    if not os.path.isfile(local_file):
        s3.download_file(bucket_name, s3_key, local_file)
        logger.info(f"Downloaded {s3_key} to {local_file}")
    else:
        logger.info(f"The file {local_file} already exists, proceeding to load it.")
except Exception as e:
    logger.error(f"Error downloading file from S3: {e}")
    exit(1)


def load_dataset() -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(local_file)
        logger.info("Dataset loaded successfully")
        return df
    except Exception as e:
        logger.error(f"Error loading the dataset: {e}")
        return None


box_builder = load_dataset()

if box_builder is not None:

    def quick_check(df: pd.DataFrame) -> None:
        logger.info(f"Size of the dataset: {df.shape}")
        logger.info(f"First rows:\n{df.head()}")
        logger.info("\nDataset information:")
        logger.info(df.info())

    quick_check(box_builder)

    def check_missing_and_duplicates(df: pd.DataFrame) -> None:
        logger.info(f"Missing values:\n{df.isnull().sum()}")
        logger.info(f"Duplicates: {df.duplicated().sum()}")

    check_missing_and_duplicates(box_builder)

    for column in box_builder.select_dtypes(include=["float64", "int64"]).columns:
        try:
            box_builder[column].fillna(box_builder[column].mean(), inplace=True)
        except Exception as e:
            logger.error(f"Error filling missing values in column {column}: {e}")

    def visualize_outcome_distribution(df: pd.DataFrame) -> None:
        try:
            plt.figure(figsize=(10, 6))
            sns.countplot(data=df, x="outcome")
            plt.title("Distribution of Purchased/Not Purchased Products")
            plt.xlabel("Outcome (1 = Purchased, 0 = Not Purchased)")
            plt.ylabel("Frequency")
            plt.show()
        except Exception as e:
            logger.error(f"Error visualizing outcome distribution: {e}")

    visualize_outcome_distribution(box_builder)

    def analyze_additional_features(df: pd.DataFrame) -> None:
        if "normalised_price" in df.columns:
            try:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["normalised_price"], kde=True)
                plt.title("Distribution of Normalized Prices")
                plt.xlabel("Normalized Price")
                plt.ylabel("Frequency")
                plt.show()
            except Exception as e:
                logger.error(f"Error visualizing normalized price: {e}")
        else:
            logger.warning("The column 'normalised_price' is not found in the dataset.")

    analyze_additional_features(box_builder)

    def analyze_price_discount_outcome(df: pd.DataFrame) -> None:
        try:
            plt.figure(figsize=(10, 6))
            sns.boxplot(x="outcome", y="normalised_price", data=df)
            plt.title("Distribution of Normalized Prices vs Purchase Outcome")
            plt.xlabel("Outcome (1 = Purchased, 0 = Not Purchased)")
            plt.ylabel("Normalized Price")
            plt.show()

            plt.figure(figsize=(10, 6))
            sns.boxplot(x="outcome", y="discount_pct", data=df)
            plt.title("Distribution of Discount (%) vs Purchase Outcome")
            plt.xlabel("Outcome (1 = Purchased, 0 = Not Purchased)")
            plt.ylabel("Discount (%)")
            plt.show()
        except Exception as e:
            logger.error(f"Error analyzing price and discount outcome: {e}")

    analyze_price_discount_outcome(box_builder)

    def analyze_global_popularity_vs_outcome(df: pd.DataFrame) -> None:
        try:
            plt.figure(figsize=(10, 6))
            sns.boxplot(x="outcome", y="global_popularity", data=df)
            plt.title("Distribution of Global Popularity vs Purchase Outcome")
            plt.xlabel("Outcome (1 = Purchased, 0 = Not Purchased)")
            plt.ylabel("Global Popularity")
            plt.show()
        except Exception as e:
            logger.error(f"Error analyzing global popularity vs outcome: {e}")

    analyze_global_popularity_vs_outcome(box_builder)

    def analyze_ordered_before_vs_outcome(df: pd.DataFrame) -> None:
        try:
            plt.figure(figsize=(10, 6))
            sns.countplot(x="ordered_before", hue="outcome", data=df)
            plt.title(
                "Relationship between Previous Purchase (ordered_before) and Purchase Outcome"
            )
            plt.xlabel("Previously Purchased Product (1 = Yes, 0 = No)")
            plt.ylabel("Frequency")
            plt.show()
        except Exception as e:
            logger.error(f"Error analyzing ordered before vs outcome: {e}")

    analyze_ordered_before_vs_outcome(box_builder)
else:
    logger.error("Failed to load the dataset. Exiting program.")
