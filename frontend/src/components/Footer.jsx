import React from 'react';

const Footer = () => {
    return (
        <footer className="bg-white border-t border-gray-200 text-center py-6 mt-10">
            <div className="container mx-auto">
                <p className="text-gray-600 font-medium">Lost & Found Club</p>
                <p className="text-gray-500 text-sm mt-1">© {new Date().getFullYear()} - Connecting Lost Items to Owners</p>
            </div>
        </footer>
    );
};
export default Footer;
