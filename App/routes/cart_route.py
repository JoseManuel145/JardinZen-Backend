from fastapi import APIRouter, status, HTTPException, Depends
from models.cart_model import CartProduct, ShoppingCart
from schemas.cart_schema import CartProductResponse,ShoppingCartAddProducts, ShoppingCartResponse
from models.user_model import User, Role
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session
from utils.security import verify_user, get_current_user

route = APIRouter()

Base.metadata.create_all(bind=engine)

#Obtiene el carrito de compras con sus productos

@route.get('/{id_user}/cart/{id_cart}', status_code=status.HTTP_200_OK, response_model=ShoppingCartResponse)
async def get_shopping_cart(id_user: int, id_cart: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Buscar el carrito correspondiente
    cart = db.query(CartProduct).filter(CartProduct.id_cart == id_cart, CartProduct.id_cart == id_cart).all()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    # Convertir los productos a una respuesta adecuada
    cart_response = ShoppingCartResponse(
        id_cart=id_cart,
        user_id=id_user,
        products=[CartProductResponse(product_id=cp.id_product, quantity=cp.quantity) for cp in cart]
    )
    
    return cart_response


@route.post('/{id_user}/cart', status_code=status.HTTP_201_CREATED, response_model=ShoppingCartResponse)
async def create_or_update_cart(id_user: int, cart_data: ShoppingCartAddProducts, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verificar si el usuario ya tiene un carrito existente
    cart = db.query(ShoppingCart).filter(ShoppingCart.id_user == id_user).first()
    
    if not cart:
        # Si no tiene un carrito, crear uno
        cart = ShoppingCart(user_id=id_user)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Agregar los productos al carrito
    for product_data in cart_data.products:
        cart_product = CartProduct(
            id_cart=cart.id_cart,
            product_id=product_data.product_id,
            quantity=product_data.quantity
        )
        db.add(cart_product)
    
    db.commit()
    
    # Obtener el carrito actualizado con sus productos
    updated_cart = db.query(CartProduct).filter(CartProduct.id_cart == cart.id_cart).all()
    cart_response = ShoppingCartResponse(
        id_cart=cart.id_cart,
        user_id=id_user,
        products=[CartProductResponse(product_id=cp.id_product, quantity=cp.quantity) for cp in updated_cart]
    )
    
    return cart_response

@route.delete('/{id_user}/cart/{id_cart}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_cart(id_user: int, id_cart: int, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verificar si el carrito existe
    cart = db.query(ShoppingCart).filter(ShoppingCart.id_cart == id_cart, ShoppingCart.id_user == id_user).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    # Eliminar productos del carrito
    db.query(CartProduct).filter(CartProduct.id_cart == id_cart).delete()
    db.delete(cart)
    db.commit()
    
    return {"detail": "Cart deleted successfully"}

@route.post('/{id_user}/cart/{id_cart}/checkout', status_code=status.HTTP_200_OK)
async def checkout_shopping_cart(id_user: int, id_cart: int, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verificar si el carrito existe
    cart = db.query(ShoppingCart).filter(ShoppingCart.id_cart == id_cart, ShoppingCart.id_user == id_user).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    # Procesar la compra (puedes agregar lógica para marcar el carrito como 'comprado')
    # Ejemplo: Se puede cambiar un estado o solo eliminar el carrito
    db.delete(cart)
    db.commit()
    
    return {"detail": "Cart checked out successfully"}
