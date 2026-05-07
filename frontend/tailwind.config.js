/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#e3f2f9',
                    100: '#b3e0f0',
                    200: '#81cee6',
                    300: '#4fb9db',
                    400: '#26a6cd',
                    500: '#219ebc',
                    600: '#1a7a94',
                    700: '#155d72',
                    800: '#0f4252',
                    900: '#0a2a34',
                    950: '#05171e',
                },
                surface: {
                    50: '#f8fafb',
                    100: '#f0f4f5',
                    200: '#e5e7eb',
                    300: '#d1d5db',
                    400: '#9ca3af',
                    500: '#6b7280',
                    600: '#4b5563',
                    700: '#374151',
                    800: '#1f2937',
                    900: '#111827',
                    950: '#0e1117',
                }
            }
        }
    },
    plugins: []
}
