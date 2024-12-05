downloadZipButton.addEventListener('click', async () => {
    try {
        const response = await fetch('/download/modified_pdfs.zip');
        if (!response.ok) throw new Error('Failed to download ZIP file.');

        // Create a blob and trigger a download
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'modified_pdfs.zip';
        link.click();
    } catch (error) {
        alert('Error downloading ZIP file: ' + error.message);
    }
});
