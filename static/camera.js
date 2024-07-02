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

window.onload = init;

document.getElementById('snap').addEventListener('click', function() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const photo = document.getElementById('photo');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const data = canvas.toDataURL('image/png');
    photo.src = data;
});