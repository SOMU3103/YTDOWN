const urlInput = document.getElementById('urlInput');
const qualitySelect = document.getElementById('qualitySelect');
const typeSelect = document.getElementById('typeSelect');
const statusMessage = document.getElementById('statusMessage');
const downloadBtn = document.getElementById('downloadBtn');
const downloadForm = document.getElementById('downloadForm');
const downloadProgress = document.getElementById('downloadProgress');
const progressFill = document.getElementById('progressFill');
const downloadStatus = document.getElementById('downloadStatus');

let currentUrl = '';
let videoQualities = [];
let audioQualities = [];

urlInput.addEventListener('blur', fetchQualities);
urlInput.addEventListener('paste', function() {
    setTimeout(fetchQualities, 100);
});

typeSelect.addEventListener('change', function() {
    updateQualityDropdown();
});

async function fetchQualities() {
    const url = urlInput.value.trim();
    
    if (!url || url === currentUrl) return;
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) return;
    
    currentUrl = url;
    
    try {
        showStatus('Checking available qualities...');
        downloadBtn.disabled = true;
        
        const response = await fetch('/get_qualities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            videoQualities = data.video_qualities || [];
            audioQualities = data.audio_qualities || [];
            updateQualityDropdown();
            showStatus('✓ Qualities loaded', 2000);
        } else {
            showStatus('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error fetching qualities:', error);
        showStatus('Failed to fetch qualities. Please check the URL.');
    } finally {
        downloadBtn.disabled = false;
    }
}

function updateQualityDropdown() {
    qualitySelect.innerHTML = '';
    
    if (typeSelect.value === 'audio') {
        if (audioQualities.length > 0) {
            audioQualities.forEach((aq, index) => {
                const option = document.createElement('option');
                option.value = 'audio';
                option.textContent = index === 0 ? `Best (${aq.bitrate})` : aq.bitrate;
                qualitySelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = 'audio';
            option.textContent = 'Best Quality';
            qualitySelect.appendChild(option);
        }
    } else {
        if (videoQualities.length > 0) {
            videoQualities.forEach(vq => {
                const option = document.createElement('option');
                option.value = vq.resolution;
                
                let label = vq.label;
                if (vq.fps && vq.fps >= 60) {
                    label += ` (${vq.fps}fps)`;
                }
                
                if (vq.resolution === '2160') {
                    label = '2160p (4K)';
                } else if (vq.resolution === '1440') {
                    label = '1440p (2K)';
                } else if (vq.resolution === '1080') {
                    label = '1080p (HD)';
                } else if (vq.resolution === '720') {
                    label = '720p (HD)';
                }
                
                option.textContent = label;
                qualitySelect.appendChild(option);
            });
        } else {
            const defaults = [
                {res: '2160', label: '2160p (4K)'},
                {res: '1440', label: '1440p (2K)'},
                {res: '1080', label: '1080p (Full HD)'},
                {res: '720', label: '720p (HD)'},
                {res: '480', label: '480p'},
                {res: '360', label: '360p'}
            ];
            
            defaults.forEach(d => {
                const option = document.createElement('option');
                option.value = d.res;
                option.textContent = d.label;
                qualitySelect.appendChild(option);
            });
        }
    }
}

function showStatus(message, duration = null) {
    statusMessage.textContent = message;
    if (duration) {
        setTimeout(() => {
            statusMessage.textContent = '';
        }, duration);
    }
}

function showDownloadProgress(show = true) {
    if (show) {
        downloadProgress.style.display = 'block';
        progressFill.style.width = '100%';
    } else {
        downloadProgress.style.display = 'none';
        progressFill.style.width = '0%';
    }
}

downloadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    const type = typeSelect.value;
    const quality = qualitySelect.value;
    
    if (!url) {
        showStatus('Please enter a YouTube URL');
        return;
    }
    
    try {
        downloadBtn.disabled = true;
        downloadBtn.textContent = 'PREPARING...';
        showStatus('Starting download...');
        showDownloadProgress(true);
        downloadStatus.textContent = 'Fetching video data...';
        
        const formData = new FormData();
        formData.append('geturl', url);
        formData.append('type', type);
        formData.append('quality', quality);
        
        downloadStatus.textContent = 'Downloading from YouTube...';
        
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Download failed');
        }
        
        downloadStatus.textContent = 'Processing file...';
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        
        // Better filename extraction
        const contentDisposition = response.headers.get('content-disposition');
        let filename = type === 'audio' ? 'audio.mp3' : 'video.mp4';
        
        if (contentDisposition) {
            // Match filename with or without quotes, handle special characters
            const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?;?/i);
            if (filenameMatch && filenameMatch[1]) {
                filename = decodeURIComponent(filenameMatch[1].trim());
                // Remove any trailing underscores or spaces
                filename = filename.replace(/[_\s]+\.(mp3|mp4)$/i, '.$1');
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        downloadStatus.textContent = '✓ Download complete!';
        showStatus('✓ Download started successfully!', 3000);
        
        setTimeout(() => {
            showDownloadProgress(false);
        }, 2000);
        
    } catch (error) {
        console.error('Download error:', error);
        showStatus('Error: ' + error.message);
        showDownloadProgress(false);
    } finally {
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'DOWNLOAD';
    }
});

updateQualityDropdown();