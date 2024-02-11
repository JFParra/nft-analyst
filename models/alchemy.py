from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Contract(BaseModel):
    address: str


class TokenMetadata(BaseModel):
    tokenType: str


class Id(BaseModel):
    tokenId: str
    tokenMetadata: TokenMetadata


class TokenUri(BaseModel):
    gateway: Optional[str] = ""
    raw: Optional[str] = ""


class MediaItem(BaseModel):
    gateway: Optional[str] = ""
    thumbnail: Optional[str] = None  # Assume thumbnail can be optional
    raw: Optional[str] = ""
    format: Optional[str] = None  # Adjusted to optional
    bytes: Optional[int] = None  # Adjusted to optional


class Attribute(BaseModel):
    value: str
    trait_type: str


class Metadata(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    attributes: Optional[List[Attribute]] = []


class OpenSea(BaseModel):
    floorPrice: float
    collectionName: str
    collectionSlug: str
    safelistRequestStatus: str
    imageUrl: Optional[str] = None
    description: str
    twitterUsername: Optional[str] = None
    discordUrl: Optional[str] = None
    bannerImageUrl: Optional[str] = None
    lastIngestedAt: str


class ContractMetadata(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    totalSupply: Optional[str] = None
    tokenType: str
    contractDeployer: Optional[str] = None
    deployedBlockNumber: Optional[int] = None
    openSea: OpenSea


class ContractSupportModel(BaseModel):
    contract: Contract
    id: Id
    title: Optional[str] = ""
    description: Optional[str] = ""
    tokenUri: TokenUri
    media: List[MediaItem]
    metadata: Union[Metadata, dict] = Field(default_factory=dict)
    timeLastUpdated: str
    contractMetadata: ContractMetadata
    error: Optional[str] = None  # Add error field
