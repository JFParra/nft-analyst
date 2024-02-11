import logging

from requests import get

from config.configuration import AlchemyConfig
from models.alchemy import ContractSupportModel


def is_contract_supported(alchemy_config: AlchemyConfig, contract_address: str) -> bool:
    try:
        # Do a single request to check if the contract address is supported by Alchemy's NFT API

        response = get(
            f"{alchemy_config.base_url}/{alchemy_config.api_key}/getNFTMetadata?contractAddress={contract_address}&tokenId=1"
            , headers={
                "Accept": "application/json",
            })

        response.raise_for_status()  # raises exception when not a 2xx response

        if response.status_code == 200:

            test = response.json()
            m = ContractSupportModel.model_validate(test)

            contract_check = m.id.tokenMetadata.tokenType

            if contract_check == "UNKNOWN":
                logging.exception(
                    "Contract address {contract_address} not supported. \n".format(
                        contract_address=contract_address
                    )
                    + "See https://docs.alchemy.com/alchemy/enhanced-apis/nft-api#what-nfts-are-supported for more information."
                )
                return False
            elif contract_check == "NOT_A_CONTRACT":
                if m.error:
                    logging.error(f"{m.error}, provided contract: {contract_address}")
                return False

            return True

        return False
    except Exception as e:
        logging.exception(e)
        return False
