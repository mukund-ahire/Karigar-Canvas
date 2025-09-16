document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('creation-form');
    const formSection = document.getElementById('form-section');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    const resetButton = document.getElementById('reset-btn');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Show loading spinner and hide form
        formSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/generate-all', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const data = await response.json();

            // Populate results
            document.getElementById('story-output').innerText = data.story;
            document.getElementById('social-output').innerText = data.social;
            // The image is sent as a base64 string, so we add the proper prefix
            document.getElementById('magic-photo').src = `data:image/png;base64,${data.magic_photo}`;
            
            // Show results and hide loading
            loadingSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please check the console and try again.');
            // Reset view on error
            loadingSection.classList.add('hidden');
            formSection.classList.remove('hidden');
        }
    });

    resetButton.addEventListener('click', () => {
        // Reset the form and show it again
        form.reset();
        resultsSection.classList.add('hidden');
        formSection.classList.remove('hidden');
    });
});