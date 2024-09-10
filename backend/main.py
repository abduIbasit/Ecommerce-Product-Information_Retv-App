# main.py
from fastapi import FastAPI, HTTPException
from models import ProductRequest
from scraper import product_scrape
import uvicorn

app = FastAPI()


@app.get("/")
@app.post("/")
def base():
    return {"status code":200, "message":"Hello!"}

@app.post("/scrape-products/")
async def scrape_products(request: ProductRequest):
    try:
        # Call the product scraping function with request data
        products = product_scrape(
            product_name=request.product_name,
            minimum_price=request.minimum_price,
            maximum_price=request.maximum_price,
            discount_percentage=request.discount_percentage,
            shipped_from_abroad=request.shipped_from_abroad
        )
        return {"top_products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)