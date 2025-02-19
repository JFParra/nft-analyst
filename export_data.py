import contextlib
import sys
import tempfile
from argparse import ArgumentParser
from datetime import datetime, timedelta

from web3 import Web3

from config.configuration import Configuration
from core.generate_metadata_output import generate_metadata_output
from core.generate_sales_output import generate_sales_output
from core.generate_transfers_output import generate_transfers_output
from jobs.cleanup_outputs import clean_up_outputs
from jobs.export_update_logs import export_update_logs
from jobs.get_nft_metadata import get_metadata_for_collection
from jobs.get_nft_sales import get_nft_sales
from jobs.get_nft_transfers import get_nft_transfers
from jobs.get_recent_block import get_recent_block
from jobs.update_block_to_date_mapping import update_block_to_date_mapping
from jobs.update_eth_prices import update_eth_prices
from utils.app_logger import logging
from utils.check_contract_support import is_contract_supported
from utils.eth_service import EthService
from utils.extract_unique_column_value import extract_unique_column_value


# Set click CLI parameters
# @click.command(context_settings=dict(help_option_names=["-h", "--help"]))
# @click.option(
#     "-a",
#     "--alchemy-api-key",
#     required=True,
#     type=str,
#     help="The Alchemy API key to use for data extraction.",
# )
# @click.option(
#     "-c",
#     "--contract-address",
#     required=True,
#     type=str,
#     help="The contract address of the desired NFT collection.",
# )
def export_data():
    try:
        alchemy_api_key: str = CONFIGURATION.app_config.alchemy.api_key

        if not alchemy_api_key:
            raise Exception("Alchemy API key is required.")

        # Convert address to checksummed address (a specific pattern of uppercase and lowercase letters)
        contract_address: str = Web3.to_checksum_address(CONFIGURATION.app_config.nft.contract_address)

        # Check if contract address is supported by Alchemy
        contract_supported: bool = is_contract_supported(
            alchemy_config=CONFIGURATION.app_config.alchemy, contract_address=contract_address
        )

        # warnings.simplefilter(action="ignore", category=FutureWarning)

        if contract_supported:
            logging.info(f"Process started for contract address: {contract_address}")

            # Get current timestamp
            right_now = str(datetime.now().timestamp())

            # Assign file paths (persisting files only)
            date_block_mapping_csv = "./raw-data/date_block_mapping.csv"
            eth_prices_csv = "./raw-data/eth_prices.csv"
            sales_csv = "sales_" + contract_address + "_" + right_now + ".csv"
            metadata_csv = "metadata_" + contract_address + ".csv"
            transfers_csv = "transfers_" + contract_address + "_" + right_now + ".csv"
            updates_csv = "./update-logs/" + contract_address + ".csv"
            all_transfers_csv = "transfers_" + contract_address + ".csv"

            # Set provider
            provider_uri = "https://eth-mainnet.alchemyapi.io/v2/" + alchemy_api_key
            web3 = Web3(Web3.HTTPProvider(provider_uri))
            eth_service = EthService(web3)

            # Get block range
            # If update logs exist, read from the saved file and set the start block
            start_block = get_recent_block(updates_csv, contract_address, web3)

            yesterday = datetime.today() - timedelta(days=1)
            _, end_block = eth_service.get_block_range_for_date(yesterday)

            # If start_block == end_block, then data is already up to date
            if start_block == end_block:
                logging.info("Data is up to date. No updates required.")
                sys.exit(0)

            # Create tempfiles
            with tempfile.NamedTemporaryFile(
                    delete=False
            ) as nft_sales_csv, tempfile.NamedTemporaryFile(
                delete=False
            ) as nft_transfers_csv, tempfile.NamedTemporaryFile(
                delete=False
            ) as all_token_ids_txt, tempfile.NamedTemporaryFile(
                delete=False
            ) as raw_attributes_csv:
                with contextlib.redirect_stderr(None):
                    # Export transfers
                    get_nft_transfers(
                        start_block=start_block,
                        end_block=end_block,
                        api_key=alchemy_api_key,
                        contract_address=contract_address,
                        output=nft_transfers_csv.name,
                    )

                with contextlib.redirect_stderr(None):
                    # Export sales
                    get_nft_sales(
                        start_block=start_block,
                        end_block=end_block,
                        api_key=alchemy_api_key,
                        contract_address=contract_address,
                        output=nft_sales_csv.name,
                    )

                # Update date block mapping
                update_block_to_date_mapping(
                    filename=date_block_mapping_csv, eth_service=eth_service
                )

                # Update ETH prices
                update_eth_prices(filename=eth_prices_csv)

                # Generate sales output
                generate_sales_output(
                    sales_file=nft_sales_csv.name,
                    date_block_mapping_file=date_block_mapping_csv,
                    eth_prices_file=eth_prices_csv,
                    output=sales_csv,
                )

                # Generate transfers output
                generate_transfers_output(
                    transfers_file=nft_transfers_csv.name,
                    date_block_mapping_file=date_block_mapping_csv,
                    output=transfers_csv,
                )

                # Consolidate sales and transfers data into final outputs
                clean_up_outputs()

                # Re-generate list of token IDs from consolidated data set
                extract_unique_column_value(
                    input_filename=all_transfers_csv,
                    output_filename=all_token_ids_txt.name,
                    column="asset_id",
                )

                # Fetch metadata
                get_metadata_for_collection(
                    api_key=alchemy_api_key,
                    contract_address=contract_address,
                    output=raw_attributes_csv.name,
                )

                # Generate metadata output
                generate_metadata_output(
                    raw_attributes_file=raw_attributes_csv.name,
                    token_ids_file=all_token_ids_txt.name,
                    output=metadata_csv,
                )

                # Export to update log file
                export_update_logs(
                    update_log_file=updates_csv,
                    current_block_number=end_block,
                )

                logging.info("Data exported to transfers.csv, sales.csv and metadata.csv")
        else:
            logging.error(f"Provided contract: {contract_address} is not supported. Exiting export ...")
    except Exception as e:
        logging.error(f"Failure exporting data")
        logging.exception(e)


if __name__ == "__main__":
    """
    Main entry point into the script.
    """
    parser = ArgumentParser(description="Run export")
    parser.add_argument("config", help="path to config yaml (config.yaml)")

    args = parser.parse_args()

    CONFIGURATION = Configuration(args.config)

    export_data()
