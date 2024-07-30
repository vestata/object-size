// Placeholder for form submission logic
document.getElementById('volumeForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Add your form handling logic here
});

document.getElementById('aiForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Add your form handling logic here
});

document.getElementById('clearButton').addEventListener('click', clearForms);

// Example function to connect with LINE BOT API
function sendToLineBot(data) {
    fetch('YOUR_LINE_BOT_API_ENDPOINT', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

document.getElementById('upload1').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageData = e.target.result.split(',')[1];
            fetch('{{ url_for("process") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: `data:image/jpeg;base64,${imageData}` })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('圖像處理失敗');
                } else {
                    // 更新箱子數量
                    document.getElementById('ai-large').value = data.large.length;
                    document.getElementById('ai-medium').value = data.medium.length;
                    document.getElementById('ai-small').value = data.small.length;
                    // store the number of boxes needed in local
                    localStorage.setItem('ai-large', data.large.length);
                    localStorage.setItem('ai-medium', data.medium.length);
                    localStorage.setItem('ai-small', data.small.length);

                    // return to main.html
                    window.location.href = '{{ url_for("home") }}';
                }
            })
            .catch(console.error);
        };
    }
});

window.onload = function() {
    clearLocalStorage();

    document.getElementById('ai-large').value = localStorage.getItem('ai-large') || '';
    document.getElementById('ai-medium').value = localStorage.getItem('ai-medium') || '';
    document.getElementById('ai-small').value = localStorage.getItem('ai-small') || '';
};

function clearLocalStorage() {
    localStorage.removeItem('ai-large');
    localStorage.removeItem('ai-medium');
    localStorage.removeItem('ai-small');
}

// 清空表單的函數
function clearForms() {
    // 清空容積計算估價表單
    document.getElementById('length').value = '';
    document.getElementById('width').value = '';
    document.getElementById('height').value = '';
    document.getElementById('large').value = '';
    document.getElementById('medium').value = '';
    document.getElementById('small').value = '';
    document.getElementById('amount-estimate').value = '';

    // 清空AI辨識估價表單
    document.getElementById('ai-large').value = '';
    document.getElementById('ai-medium').value = '';
    document.getElementById('ai-small').value = '';
    document.getElementById('hang-box').value = '';
    document.getElementById('ai-amount-estimate').value = '';
    document.getElementById('savings').value = '';

    // 清除本地儲存
    localStorage.removeItem('ai-large');
    localStorage.removeItem('ai-medium');
    localStorage.removeItem('ai-small');
}

function fit_boxes(length, width, height) {
    const box_config = {
        small: { width: 47, height: 33, depth: 30, volume: 47 * 33 * 30 },  
        medium: { width: 48, height: 45, depth: 42, volume: 48 * 45 * 42 }, 
        large: { width: 69, height: 47, depth: 47, volume: 69 * 47 * 47 }   
    };

    const box_order = ['large', 'medium', 'small'];
    let remaining_volume = length * width * height;
    let box_count = { small: 0, medium: 0, large: 0 };

    // function can_fit(box, l, w, h) {
    //     return (l <= box.width && w <= box.height && h <= box.depth) || 
    //            (l <= box.width && w <= box.depth && h <= box.height) || 
    //            (l <= box.height && w <= box.width && h <= box.depth) || 
    //            (l <= box.height && w <= box.depth && h <= box.width) || 
    //            (l <= box.depth && w <= box.width && h <= box.height) || 
    //            (l <= box.depth && w <= box.height && h <= box.width);
    // }

    for (let box_size of box_order) {
        let box_volume = box_config[box_size].volume;
        let box = box_config[box_size];

        // while (remaining_volume >= box_volume && can_fit(box, length, width, height)) {
        while (remaining_volume >= box_volume) {
            remaining_volume -= box_volume;
            box_count[box_size]++;
        }
    }

    return box_count;
}

function calculateVolume() {
    const length = parseFloat(document.getElementById('length').value);
    const width = parseFloat(document.getElementById('width').value);
    const height = parseFloat(document.getElementById('height').value);

    if (!isNaN(length) && length > 0 && !isNaN(width) && width > 0 && !isNaN(height) && height > 0) {
        const { small, medium, large } = fit_boxes(length, width, height);
        document.getElementById('large').value = large;
        document.getElementById('medium').value = medium;
        document.getElementById('small').value = small;
    } else {
        document.getElementById('large').value = '';
        document.getElementById('medium').value = '';
        document.getElementById('small').value = '';
    }
}
