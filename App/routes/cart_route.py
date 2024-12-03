from fastapi import APIRouter, status, HTTPException, Depends
from models.cart_model import CartProduct, ShoppingCart
from schemas.cart_schema import CartProductResponse, ShoppingCartResponse
from models.user_model import User, Role
from models.product_model import Product
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session
from utils.security import verify_user
from sqlalchemy import update

route = APIRouter()


@route.get('/{id_user}/cart/{id_cart}', status_code=status.HTTP_200_OK, response_model=ShoppingCartResponse)
async def getCart(id_user: int, id_cart: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cart = db.query(CartProduct).filter(CartProduct.id_cart == id_cart).all()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    cart_response = ShoppingCartResponse(
        id_cart=id_cart,
        id_user=id_user,
        products=[CartProductResponse(
            id_product=cp.id_product, quantity=cp.quantity) for cp in cart]
    )
    return cart_response

@route.post('/{id_usuario}/products/{id_product}', status_code=status.HTTP_201_CREATED, response_model=CartProductResponse)
async def addToCart(id_usuario: int, id_product: int, quantity: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id_user == id_usuario).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cart = db.query(ShoppingCart).filter(
        ShoppingCart.id_user == id_usuario).first()
    product = db.query(Product).filter(
        Product.id_product == id_product).first()
    if not cart:
        cart = ShoppingCart(id_user=id_usuario)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    cart_product = CartProduct(
        id_cart=cart.id_cart,
        id_product=product.id_product,
        quantity=quantity
    )
    db.add(cart_product)
    db.commit()
    db.refresh(cart_product)
    return cart_product

@route.delete('/{id_user}/cart/{id_cart}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_cart(id_user: int, id_cart: int, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verificar si el carrito existe
    cart = db.query(ShoppingCart).filter(ShoppingCart.id_cart ==
                                         id_cart, ShoppingCart.id_user == id_user).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    # Eliminar productos del carrito
    db.query(CartProduct).filter(CartProduct.id_cart == id_cart).delete()
    db.delete(cart)
    db.commit()

    return {"detail": "Cart deleted successfully"}

@route.post('/{id_user}/cart/{id_cart}', status_code=status.HTTP_200_OK)
async def checkout_shopping_cart(id_user: int, id_cart: int, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verificar si el carrito existe
    cart = db.query(ShoppingCart).filter(ShoppingCart.id_cart ==
                                         id_cart, ShoppingCart.id_user == id_user).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    # Procesar la compra (puedes agregar lógica para marcar el carrito como 'comprado')
    # Ejemplo: Se puede cambiar un estado o solo eliminar el carrito
    db.query(CartProduct).filter(CartProduct.id_cart == id_cart).delete()
    db.delete(cart)
    db.commit()

    return {"detail": "Cart checked out successfully"}
