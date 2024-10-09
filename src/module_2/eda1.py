import os
import logging
import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
from dotenv import load_dotenv

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


def download_s3_file(bucket_name: str, s3_key: str, local_path: str) -> None:
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        logger.info(f"Downloaded {s3_key} to {local_path}")
    except Exception as e:
        logger.error(f"Error downloading {s3_key}: {e}")
        raise


bucket_name = "zrive-ds-data"
datasets = {
    "orders": "groceries/sampled-datasets/orders.parquet",
    "regulars": "groceries/sampled-datasets/regulars.parquet",
    "abandoned_cart": "groceries/sampled-datasets/abandoned_carts.parquet",
    "inventory": "groceries/sampled-datasets/inventory.parquet",
    "users": "groceries/sampled-datasets/users.parquet",
}

for dataset, s3_key in datasets.items():
    local_file = f"{dataset}.parquet"
    if not os.path.isfile(local_file):
        try:
            download_s3_file(bucket_name, s3_key, local_file)
        except Exception as e:
            logger.critical(f"Failed to download {dataset}: {e}")
            continue
    else:
        logger.info(f"The file {local_file} already exists, proceeding to load it.")


def load_data() -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
):
    try:
        orders = pd.read_parquet("orders.parquet")
        regulars = pd.read_parquet("regulars.parquet")
        abandoned_cart = pd.read_parquet("abandoned_cart.parquet")
        inventory = pd.read_parquet("inventory.parquet")
        users = pd.read_parquet("users.parquet")
        return orders, regulars, abandoned_cart, inventory, users
    except Exception as e:
        logger.error(f"Error loading datasets: {e}")
        raise


try:
    orders, regulars, abandoned_cart, inventory, users = load_data()
except Exception as e:
    logger.critical(f"Failed to load data: {e}")
    exit(1)


def quick_check(df: pd.DataFrame, name: str) -> None:
    logger.info(f"Dataset: {name}")
    logger.info(f"Size: {df.shape}")
    logger.info(f"First rows:\n{df.head()}\n")


for df, name in zip(
    [orders, regulars, abandoned_cart, inventory, users],
    ["Orders", "Regulars", "Abandoned Cart", "Inventory", "Users"],
):
    quick_check(df, name)


def check_missing_and_duplicates(df: pd.DataFrame, name: str) -> None:
    logger.info(f"Checking {name}...")
    logger.info(f"Column types:\n{df.dtypes}")
    logger.info(f"Missing values:\n{df.isnull().sum()}")
    try:
        logger.info(f"Duplicates: {df.duplicated().sum()}")
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
    logger.info("\n")


for df, name in zip(
    [orders, regulars, abandoned_cart, inventory, users],
    ["Orders", "Regulars", "Abandoned Cart", "Inventory", "Users"],
):
    check_missing_and_duplicates(df, name)


def descriptive_analysis(df: pd.DataFrame, name: str) -> None:
    logger.info(f"\nDescriptive Analysis for {name}")
    try:
        logger.info(df.describe(include="all"))
    except Exception as e:
        logger.error(f"Error performing descriptive analysis on {name}: {e}")


for df, name in zip(
    [orders, regulars, abandoned_cart, inventory, users],
    ["Orders", "Regulars", "Abandoned Cart", "Inventory", "Users"],
):
    descriptive_analysis(df, name)

sns.set(style="whitegrid")


def plot_item_distribution(df: pd.DataFrame, name: str) -> None:
    if "item_ids" in df.columns:
        try:
            plt.figure(figsize=(10, 6))
            sns.histplot(df["item_ids"].apply(len), bins=30, kde=True)
            plt.title(f"Distribution of Number of Items in {name}")
            plt.xlabel("Number of Items")
            plt.ylabel("Frequency")
            plt.show()
        except Exception as e:
            logger.error(f"Error plotting item distribution for {name}: {e}")
    else:
        logger.warning(f"The column 'item_ids' is not found in {name}.")


plot_item_distribution(orders, "Orders")
plot_item_distribution(abandoned_cart, "Abandoned Carts")

try:
    regular_users = set(regulars["user_id"])
    abandoned_cart["regular_user"] = abandoned_cart["user_id"].isin(regular_users)

    abandonment_rates = abandoned_cart.groupby("regular_user").size() / users.shape[0]
    logger.info("Abandonment Rate of Carts by User Type")
    logger.info(abandonment_rates)

    abandonment_rates = abandonment_rates.reset_index(name="abandonment_rate")
    abandonment_rates["regular_user"] = abandonment_rates["regular_user"].replace(
        {True: "Regular", False: "Non-Regular"}
    )

    plt.figure(figsize=(8, 5))
    sns.barplot(x="regular_user", y="abandonment_rate", data=abandonment_rates)
    plt.title("Abandonment Rate of Carts by User Type")
    plt.xlabel("User Type")
    plt.ylabel("Abandonment Rate")
    plt.ylim(0, 1)
    plt.show()
except Exception as e:
    logger.error(f"Error calculating abandonment rates: {e}")

try:
    if "total_amount" in orders.columns:
        avg_total_amount = orders["total_amount"].mean()
        logger.info(f"The average total amount of orders is: {avg_total_amount}")

        abandoned_cart["created_at"] = pd.to_datetime(abandoned_cart["created_at"])
        abandoned_cart["abandon_date"] = abandoned_cart["created_at"].dt.date

        abandonment_by_date = abandoned_cart.groupby("abandon_date").size()

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=abandonment_by_date.index, y=abandonment_by_date.values)
        plt.title("Number of Abandoned Carts by Date")
        plt.xlabel("Date")
        plt.ylabel("Number of Abandoned Carts")
        plt.xticks(rotation=45)
        plt.show()
    else:
        logger.warning("Cannot perform alternative analysis: missing required columns.")
except Exception as e:
    logger.error(f"Error during additional analysis: {e}")
