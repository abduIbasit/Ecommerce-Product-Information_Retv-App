# models.py
"""Models for the Jumia catalogue scraper by Abdulbasit A"""

from pydantic import BaseModel, Field
from typing import Optional

class ProductRequest(BaseModel):
    product_name: str = Field(..., description="Name of the product to search for.")
    minimum_price: Optional[int] = Field(0, description="Minimum price filter for the product.")
    maximum_price: Optional[int] = Field(None, description="Maximum price filter for the product.")
    discount_percentage: Optional[int] = Field(None, description="Discount percentage filter for the product.")
    shipped_from_abroad: Optional[bool] = Field(False, description="Filter products shipped from abroad.")
