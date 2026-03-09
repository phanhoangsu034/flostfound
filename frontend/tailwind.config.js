export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#007BFF', // Blue
                found: '#28A745',   // Green
                lost: '#DC3545',    // Red
            }
        },
    },
    plugins: [],
}
