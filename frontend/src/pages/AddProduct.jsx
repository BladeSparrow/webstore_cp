import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const AddProduct = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        price: '',
        category: '',
        manufacturer: '',
        short_descr: '',
        description: ''
    });
    const [categories, setCategories] = useState([]);
    const [manufacturers, setManufacturers] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchOptions();
    }, []);

    const fetchOptions = async () => {
        try {
            const catRes = await api.get('category/');
            const manRes = await api.get('manufacturers/');
            setCategories(catRes.data);
            setManufacturers(manRes.data);
        } catch (err) {
            console.error("Failed to fetch options", err);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('products/', formData);
            alert("Product created successfully!");
            navigate('/');
        } catch (err) {
            console.error(err);
            if (err.response && err.response.status === 403) {
                setError("Permission denied. You must be a manager.");
            } else {
                setError("Failed to create product. Check data.");
            }
        }
    };

    return (
        <div className="auth-container">
            <h2>Add Product</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
                <input name="code" placeholder="Code (Unique)" onChange={handleChange} required />
                <input name="name" placeholder="Name" onChange={handleChange} required />

                <select name="category" onChange={handleChange} required>
                    <option value="">Select Category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>

                <select name="manufacturer" onChange={handleChange} required>
                    <option value="">Select Manufacturer</option>
                    {manufacturers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>

                <input name="price" type="number" step="0.01" placeholder="Price (UAH)" onChange={handleChange} required />

                <input name="short_descr" placeholder="Short Description" onChange={handleChange} required />
                <textarea name="description" placeholder="Full Description" onChange={handleChange} />

                <button type="submit">Create Product</button>
            </form>
        </div>
    );
};

export default AddProduct;
