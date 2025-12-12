import React, { useEffect, useState } from 'react';
import api from '../api';

const ProductList = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await api.get('products/');
            setProducts(response.data);
            setLoading(false);
        } catch (err) {
            setError("Failed to load products");
            setLoading(false);
        }
    };

    const addToCart = async (product) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            // Authenticated: Use API
            try {
                await api.post('cart/', {
                    product_id: product.id,
                    quantity: 1
                });
                alert("Added to cart!");
            } catch (err) {
                alert("Failed to add to cart (API Error)");
            }
        } else {
            // Guest: Use LocalStorage
            let cart = JSON.parse(localStorage.getItem('guest_cart') || "[]");
            const existingItem = cart.find(item => item.product.id === product.id);

            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({
                    id: Date.now(), // Temporary ID for frontend key
                    product: product,
                    quantity: 1
                });
            }

            localStorage.setItem('guest_cart', JSON.stringify(cart));
            alert("Added to local cart!");
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="product-list">
            <h1>Products</h1>
            <div className="grid">
                {products.map(p => (
                    <div key={p.id} className="card">
                        <h3>{p.name}</h3>
                        <p>{p.short_descr}</p>
                        <p className="price">
                            {p.price_uah} UAH / {p.price_usd} USD
                        </p>
                        <button onClick={() => addToCart(p)}>Add to Cart</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProductList;
