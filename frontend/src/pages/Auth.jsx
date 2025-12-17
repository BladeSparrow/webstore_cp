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

    const processLoginResponse = async (response) => {
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);

            // Sync Guest Cart
            const guestCart = JSON.parse(localStorage.getItem('guest_cart') || "[]");
            let syncErrors = 0;

            if (guestCart.length > 0) {
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

            // Fetch user details to check manager status
            try {
                const meRes = await api.get('auth/me/', {
                    headers: { Authorization: `Bearer ${response.data.access}` }
                });
                localStorage.setItem('is_manager', meRes.data.is_manager);
                window.dispatchEvent(new Event("storage"));
            } catch (e) {
                console.error("Failed to fetch user info", e);
            }

            navigate('/');
            window.location.reload();
        }
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
                await processLoginResponse(response);
            } else {
                await api.post('auth/register/', formData);
                // Auto-login after registration
                const loginResponse = await api.post('auth/login/', {
                    username: formData.username,
                    password: formData.password
                });
                await processLoginResponse(loginResponse);
            }
        } catch (err) {
            console.error(err);
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

                        <input name="email" type="email" placeholder="Email" onChange={handleChange} required />
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
