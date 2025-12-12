import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

const Cart = () => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCart();
    }, []);

    const fetchCart = async () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const response = await api.get('cart/');
                setCart(response.data);
                setLoading(false);
            } catch (err) {
                console.error(err);
                setLoading(false);
            }
        } else {
            // Guest Cart
            const guestItems = JSON.parse(localStorage.getItem('guest_cart') || "[]");
            const total = guestItems.reduce((sum, item) => sum + (parseFloat(item.product.price_uah) * item.quantity), 0);
            setCart({
                items: guestItems,
                total_price: total.toFixed(2)
            });
            setLoading(false);
        }
    };

    const removeItem = async (itemId) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                await api.delete(`cart/items/${itemId}/`);
                fetchCart();
            } catch (err) {
                alert("Failed to remove item");
            }
        } else {
            // Guest Remove
            let guestItems = JSON.parse(localStorage.getItem('guest_cart') || "[]");
            guestItems = guestItems.filter(item => item.id !== itemId);
            localStorage.setItem('guest_cart', JSON.stringify(guestItems));
            fetchCart();
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!cart || !cart.items || cart.items.length === 0) {
        return (
            <div>
                <h2>Your Cart is Empty</h2>
                <Link to="/">Go Shopping</Link>
            </div>
        );
    }

    const handleCheckout = () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            navigate('/checkout');
        } else {
            alert("Please login to proceed to payment.");
            navigate('/login');
        }
    };

    return (
        <div className="cart-page">
            <h2>Your Cart</h2>
            <div className="cart-items">
                {cart.items.map(item => (
                    <div key={item.id} className="cart-item">
                        <span>{item.product.name}</span>
                        <span>{item.quantity} x {item.product.price_uah} UAH</span>
                        <button onClick={() => removeItem(item.id)}>Remove</button>
                    </div>
                ))}
            </div>
            <div className="cart-total">
                <h3>Total: {cart.total_price} UAH</h3>
                <button onClick={handleCheckout} className="btn-primary">Proceed to Checkout</button>
            </div>
        </div>
    );
};

export default Cart;
