from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.dependencies import get_catalog_service, get_current_owner_user, get_current_user
from app.domain.user import User
from app.schemas.catalog import (
    CategoryResponse,
    CreateCategoryRequest,
    CreateProductRequest,
    ProductResponse,
    UpdateProductRequest,
)
from app.services.catalog_service import CatalogService
from app.services.product_media_service import ProductMediaService

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[CategoryResponse]:
    return [CategoryResponse.from_domain(category) for category in service.list_categories()]


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CreateCategoryRequest,
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> CategoryResponse:
    category = service.create_category(payload.name, current_owner)
    return CategoryResponse.from_domain(category)


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    search: Annotated[str | None, Query(max_length=120)] = None,
    include_inactive: bool = False,
) -> list[ProductResponse]:
    return [
        ProductResponse.from_domain(product)
        for product in service.list_all_products(
            search=search,
            include_inactive=include_inactive,
        )
    ]


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: CreateProductRequest,
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    product = service.create_product(
        category_id=payload.category_id,
        name=payload.name,
        price=payload.price,
        emoji=payload.emoji,
        actor=current_owner,
    )
    return ProductResponse.from_domain(product)


@router.post(
    "/products/{product_id}/image",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    product_id: UUID,
    image: Annotated[UploadFile, File()],
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    media_service = ProductMediaService()
    image_path = await media_service.save_product_image(image)

    try:
        product = service.update_product_image(
            product_id=product_id,
            image_path=image_path,
            actor=current_owner,
        )
    except Exception:
        media_service.delete_product_image(image_path)
        raise

    return ProductResponse.from_domain(product)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    payload: UpdateProductRequest,
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    product = service.update_product(
        product_id=product_id,
        category_id=payload.category_id,
        name=payload.name,
        price=payload.price,
        emoji=payload.emoji,
        remove_image=payload.remove_image,
        actor=current_owner,
    )
    return ProductResponse.from_domain(product)


@router.post("/products/{product_id}/deactivate", response_model=ProductResponse)
def deactivate_product(
    product_id: UUID,
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    product = service.deactivate_product(product_id, current_owner)
    return ProductResponse.from_domain(product)


@router.post("/products/{product_id}/restore", response_model=ProductResponse)
def restore_product(
    product_id: UUID,
    current_owner: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    product = service.restore_product(product_id, current_owner)
    return ProductResponse.from_domain(product)
