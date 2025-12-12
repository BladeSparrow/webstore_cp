import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: '',
        first_name: '',
        last_name: ''
    });
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                const response = await api.post('auth/login/', {
                    username: formData.username,
                    password: formData.password
                });
                localStorage.setItem('access_token', response.data.access);
                localStorage.setItem('refresh_token', response.data.refresh);

                // Sync Guest Cart
                const guestCart = JSON.parse(localStorage.getItem('guest_cart') || "[]");
                let syncErrors = 0;

                if (guestCart.length > 0) {
                    // Start sync
                    for (const item of guestCart) {
                        try {
                            // Ensure header is set for these requests specifically
                            const config = {
                                headers: { Authorization: `Bearer ${response.data.access}` }
                            };
                            await api.post('cart/', {
                                product_id: item.product.id,
                                quantity: item.quantity
                            }, config);
                        } catch (e) {
                            console.error("Failed to sync item", item, e);
                            syncErrors++;
                            // Capture first error for debugging
                            if (syncErrors === 1) {
                                alert(`Sync error for ${item.product.name}: ${JSON.stringify(e.response?.data || e.message)}`);
                            }
                        }
                    }

                    if (syncErrors === 0) {
                        localStorage.removeItem('guest_cart');
                    } else {
                        alert(`Warning: ${syncErrors} items failed to sync to your account. They remain in guest cart.`);
                    }
                }

                navigate('/');
            } else {
                await api.post('auth/register/', formData);
                alert("Registration successful! Please login.");
                setIsLogin(true);
            }
        } catch (err) {
            setError("Authentication failed. Check credentials.");
        }
    };

    return (
        <div className="auth-container">
            <h2>{isLogin ? 'Login' : 'Register'}</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
                <input
                    name="username"
                    placeholder="Username"
                    onChange={handleChange}
                    required
                />
                <input
                    name="password"
                    type="password"
                    placeholder="Password"
                    onChange={handleChange}
                    required
                />
                {!isLogin && (
                    <>
                        <input name="email" placeholder="Email" onChange={handleChange} />
                        <input name="first_name" placeholder="First Name" onChange={handleChange} />
                        <input name="last_name" placeholder="Last Name" onChange={handleChange} />
                    </>
                )}
                <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
            </form>
            <button className="link-btn" onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
            </button>
        </div>
    );
};

export default Auth;
