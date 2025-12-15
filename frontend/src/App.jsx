import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import ProductList from './pages/ProductList';
import Login from './pages/Auth';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import './App.css';

const Navbar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-brand">WebStore</div>
      <div className="nav-links">
        <Link to="/">Products</Link>
        <Link to="/cart">Cart</Link>
        {token ? (
          <button onClick={handleLogout} className="btn-link">Logout</button>
        ) : (
          <Link to="/login">Login/Register</Link>
        )}
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<ProductList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
