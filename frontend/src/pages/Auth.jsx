import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        telegram_id: '',
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
                // ... login logic remains same ...
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
                    // ... sync logic remains same ...
                    for (const item of guestCart) {
                        try {
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
                        }
                    }

                    if (syncErrors === 0) {
                        localStorage.removeItem('guest_cart');
                    }
                }

                navigate('/');
            } else {
                await api.post('auth/register/', formData);
                alert("Registration successful! Please login.");
                setIsLogin(true);
            }
        } catch (err) {
            console.error(err);
            setError("Authentication failed. Check credentials or Telegram ID uniqueness.");
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
                        <input name="telegram_id" placeholder="Telegram ID (e.g. 123456789)" onChange={handleChange} required />
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
