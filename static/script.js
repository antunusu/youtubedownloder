document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const pasteBtn = document.getElementById('paste-btn');
    
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const resultState = document.getElementById('result-state');
    
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');
    
    const videoThumb = document.getElementById('video-thumb');
    const videoDuration = document.getElementById('video-duration');
    const videoTitle = document.getElementById('video-title');
    const formatGrid = document.getElementById('format-grid');
    
    const downloadProgress = document.getElementById('download-progress');
    const successMessage = document.getElementById('success-message');
    
    // UI Helpers
    const hideAllStates = () => {
        loadingState.classList.add('hidden');
        errorState.classList.add('hidden');
        resultState.classList.add('hidden');
    };

    const showError = (msg) => {
        hideAllStates();
        errorMessage.textContent = msg;
        errorState.classList.remove('hidden');
    };

    // Auto-paste functionality
    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text && (text.includes('youtube.com') || text.includes('youtu.be'))) {
                urlInput.value = text;
                // Optional: auto-submit after pasting
                // urlForm.dispatchEvent(new Event('submit'));
            } else {
                alert('No valid YouTube URL found in clipboard');
            }
        } catch (err) {
            console.error('Failed to read clipboard contents: ', err);
            // Fallback for browsers that block clipboard API without permissions
            urlInput.focus();
            document.execCommand('paste');
        }
    });

    // Form Submission (Analyze URL)
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        // Reset UI
        hideAllStates();
        loadingState.classList.remove('hidden');
        downloadProgress.classList.add('hidden');
        successMessage.classList.add('hidden');
        // Disable buttons
        const submitBtn = urlForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to analyze URL');
            }

            renderResults(data, url);
        } catch (error) {
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
        }
    });

    retryBtn.addEventListener('click', () => {
        urlInput.focus();
        urlInput.select();
    });

    // Render logic for formats
    const renderResults = (data, url) => {
        hideAllStates();
        
        videoThumb.src = data.thumbnail;
        videoTitle.textContent = data.title;
        videoDuration.textContent = data.duration;
        
        formatGrid.innerHTML = '';
        
        data.formats.forEach(format => {
            const btn = document.createElement('button');
            btn.className = 'format-btn';
            
            const iconClass = format.type === 'audio' 
                ? 'ph-music-notes' 
                : (format.id === '1080p' ? 'ph-monitor-play' : 'ph-video');
            
            btn.innerHTML = `
                <i class="ph ${iconClass}"></i>
                <span>${format.label}</span>
            `;
            
            btn.addEventListener('click', () => initiateDownload(url, format.id, btn));
            
            formatGrid.appendChild(btn);
        });

        // Smooth scroll to results
        resultState.classList.remove('hidden');
        resultState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };

    // Download handler
    const initiateDownload = async (url, formatId, clickedBtn) => {
        // Disable all buttons to prevent multiple requests
        const allBtns = formatGrid.querySelectorAll('.format-btn');
        allBtns.forEach(btn => btn.disabled = true);
        
        // Add loading state to clicked button
        const originalContent = clickedBtn.innerHTML;
        clickedBtn.innerHTML = '<i class="ph-bold ph-spinner-gap spin"></i><span>Processing...</span>';
        
        // Show progress UI
        successMessage.classList.add('hidden');
        downloadProgress.classList.remove('hidden');
        
        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format: formatId })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to process download');
            }

            // Trigger file download
            if (data.download_url) {
                const a = document.createElement('a');
                a.href = data.download_url;
                a.download = ''; // Let browser use server filename
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                // Show success
                downloadProgress.classList.add('hidden');
                successMessage.classList.remove('hidden');
            }

        } catch (error) {
            alert('Error during download: ' + error.message);
            downloadProgress.classList.add('hidden');
        } finally {
            // Restore buttons
            allBtns.forEach(btn => btn.disabled = false);
            clickedBtn.innerHTML = originalContent;
        }
    };
});
