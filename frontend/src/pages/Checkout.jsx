import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Checkout = () => {
    const [formData, setFormData] = useState({
        email: '',
        address: '',
        card_number: '',
        expiry: '',
        cvv: ''
    });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('checkout/', formData);
            alert(`Success! Order #${response.data.order_number} created.`);
            navigate('/');
        } catch (err) {
            alert("Checkout failed.");
            console.error(err);
        }
    };

    return (
        <div className="checkout-page">
            <h2>Checkout</h2>
            <form onSubmit={handleSubmit} className="auth-container">
                <input name="email" placeholder="Email for confirmation" onChange={handleChange} required />
                <textarea name="address" placeholder="Shipping Address" onChange={handleChange} required />

                <h3>Payment Details (Mock)</h3>
                <input name="card_number" placeholder="Card Number" onChange={handleChange} required />
                <div className="row">
                    <input name="expiry" placeholder="MM/YY" onChange={handleChange} required />
                    <input name="cvv" placeholder="CVV" onChange={handleChange} required />
                </div>

                <button type="submit" className="btn-primary">Pay & Order</button>
            </form>
        </div>
    );
};

export default Checkout;
