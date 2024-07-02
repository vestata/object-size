const constraints = {
    video: {
        facingMode: 'environment' // 使用後置相機
    }
};

async function init() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        const video = document.getElementById('video');
        video.srcObject = stream;
    } catch (err) {
        console.error('錯誤: ' + err);
        alert('無法訪問相機: ' + err.message);
    }
}

async function captureAndProcessImage() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/png');

    // 發送圖像數據進行處理
    const response = await fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataURL })
    });

    const result = await response.json();
    console.log(result);
    const processed = document.getElementById('processed');
    processed.src = 'data:image/png;base64,' + result.processed_image;
}

document.getElementById('snap').addEventListener('click', captureAndProcessImage);

function setScaleSize(size) {
    const scale = document.getElementById('scale');
    if (size === 'small') {
        scale.style.width = '15px';
        scale.style.height = '60px';
    } else if (size === 'medium') {
        scale.style.width = '25px';
        scale.style.height = '100px';
    } else if (size === 'large') {
        scale.style.width = '35px';
        scale.style.height = '140px';
    }
}

window.onload = init;
