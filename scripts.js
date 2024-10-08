document.getElementById('imageForm').onsubmit = function(e) {
    e.preventDefault();

    const file = document.getElementById('imageInput').files[0];
    const reader = new FileReader();
    
    reader.onloadend = function() {
        const imageData = reader.result.split(',')[1]; // Get base64 data
        fetch('/image-sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image_data: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('output').innerText = data.text;
        });
    };

    if (file) {
        reader.readAsDataURL(file);
    }
};
