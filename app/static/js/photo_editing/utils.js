// app/static/js/photo_editing/utils.js

/**
 * Utility functions for photo editing
 */
class PhotoUtils {
    /**
     * Convert a blob URL to a File object
     * @param {string} url - Data URL or blob URL
     * @param {string} filename - Output filename
     * @param {string} mimeType - MIME type of the file
     * @returns {Promise<File>} - File object
     */
    static async urlToFile(url, filename, mimeType) {
        const response = await fetch(url);
        const blob = await response.blob();
        return new File([blob], filename, { type: mimeType });
    }

    /**
     * Convert hex color to rgba
     * @param {string} hex - Hex color code
     * @param {number} opacity - Opacity value (0-1)
     * @returns {string} - RGBA color string
     */
    static hexToRgba(hex, opacity) {
        hex = hex.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

    /**
     * Show loading state on a button
     * @param {HTMLElement} button - Button element
     * @param {boolean} isLoading - Loading state
     * @param {string} originalHtml - Original button HTML
     * @param {string} loadingHtml - Loading button HTML
     */
    static toggleButtonLoading(button, isLoading, originalHtml, loadingHtml) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = loadingHtml;
        } else {
            button.disabled = false;
            button.innerHTML = originalHtml;
        }
    }
}

// Make the utilities globally available
window.PhotoUtils = PhotoUtils;