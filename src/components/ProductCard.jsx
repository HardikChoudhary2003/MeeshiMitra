// src/components/ProductCard.jsx
import React from 'react';

const ProductCard = ({ product }) => {
  // Format the price with the Indian Rupee symbol
  const formattedPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(product.price);

  return (
    <div className="bg-background rounded-lg shadow-md overflow-hidden flex flex-col">
      <img 
        src={product.image_url} 
        alt={product.product_name} 
        className="w-full h-48 object-cover" 
        // Add a fallback image in case the original fails to load
        onError={(e) => { e.target.onerror = null; e.target.src='https://source.unsplash.com/random/400x400/?product'; }}
      />
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="text-lg font-semibold text-on-background flex-grow">{product.product_name}</h3>
        <p className="text-sm text-on-background/80">{product.category}</p>
        <div className="flex justify-between items-center mt-4">
          <span className="text-lg font-bold text-primary">{formattedPrice}</span>
          <button className="bg-primary text-white px-4 py-2 rounded-full hover:bg-primary/90 transition-colors">
            View
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
