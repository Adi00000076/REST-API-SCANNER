let currentImageUrl = ''; // Track current image URL for transformations
let currentImageCanvas = null; // Canvas for image transformations

function startScan() {
    // Simulate scanning process and load images into the gallery
    const images = [
        'image1.jpg',
        'image2.jpg',
        'image3.jpg'
    ];

    const gallery = document.getElementById('image-gallery');
    gallery.innerHTML = ''; // Clear existing gallery

    images.forEach((img, index) => {
        // Create gallery image element
        const imgElement = document.createElement('img');
        imgElement.src = img;
        imgElement.alt = `Image ${index + 1}`;
        imgElement.className = 'img-thumbnail';
        imgElement.style.cursor = 'pointer';
        imgElement.onclick = () => loadImageForPreview(img);
        gallery.appendChild(imgElement);

        // Create and add thumbnail
        const thumbnail = document.createElement('img');
        thumbnail.src = img;
        thumbnail.alt = `Thumbnail ${index + 1}`;
        thumbnail.className = 'img-thumbnail';
        thumbnail.style.cursor = 'pointer';
        thumbnail.onclick = () => loadImageForPreview(img);
        document.getElementById('thumbnail-container').appendChild(thumbnail);
    });
}

function loadImageForPreview(imgUrl) {
    currentImageUrl = imgUrl;
    const thumbnailContainer = document.getElementById('thumbnail-container');
    thumbnailContainer.innerHTML = `<img src="${imgUrl}" alt="Preview" class="img-fluid" id="preview-image">`;
    initializeCanvas(imgUrl);
}

function initializeCanvas(imgUrl) {
    const canvas = document.getElementById('image-canvas');
    const context = canvas.getContext('2d');

    const image = new Image();
    image.src = imgUrl;

    image.onload = () => {
        canvas.width = image.width;
        canvas.height = image.height;
        context.drawImage(image, 0, 0);
        currentImageCanvas = canvas;
    };
}

function rotateImage() {
    if (!currentImageCanvas) return;

    const context = currentImageCanvas.getContext('2d');
    const image = new Image();
    image.src = currentImageUrl;

    image.onload = () => {
        const angle = 90; // Rotate by 90 degrees
        const { width, height } = image;

        currentImageCanvas.width = height;
        currentImageCanvas.height = width;

        context.clearRect(0, 0, currentImageCanvas.width, currentImageCanvas.height);
        context.translate(currentImageCanvas.width / 2, currentImageCanvas.height / 2);
        context.rotate(angle * Math.PI / 180);
        context.drawImage(image, -width / 2, -height / 2);
    };
}

function cropImage() {
    if (!currentImageCanvas) return;

    // Example cropping implementation
    const context = currentImageCanvas.getContext('2d');
    const croppedWidth = currentImageCanvas.width / 2;
    const croppedHeight = currentImageCanvas.height / 2;
    const croppedImage = context.getImageData(0, 0, croppedWidth, croppedHeight);

    currentImageCanvas.width = croppedWidth;
    currentImageCanvas.height = croppedHeight;
    context.putImageData(croppedImage, 0, 0);
}

function adjustBrightness() {
    const slider = document.getElementById('brightness-slider');
    const brightness = parseFloat(slider.value);

    const canvas = document.getElementById('edit-image-canvas');
    const context = canvas.getContext('2d');

    const image = new Image();
    image.src = currentImageUrl;

    image.onload = () => {
        canvas.width = image.width;
        canvas.height = image.height;
        context.drawImage(image, 0, 0);

        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
            data[i] = data[i] * brightness;       // Red
            data[i + 1] = data[i + 1] * brightness; // Green
            data[i + 2] = data[i + 2] * brightness; // Blue
        }

        context.putImageData(imageData, 0, 0);
    };
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

function toggleSettingsDialog() {
    const dialog = document.getElementById('settings-dialog');
    dialog.classList.toggle('hidden');
}

function closeSettingsDialog() {
    const dialog = document.getElementById('settings-dialog');
    dialog.classList.add('hidden');
}

function openTab(evt, tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.add('hidden'));

    const tabLinks = document.querySelectorAll('.tab-link');
    tabLinks.forEach(link => link.classList.remove('active'));

    document.getElementById(tabId).classList.remove('hidden');
    evt.currentTarget.classList.add('active');
}

function zoomIn() {
    // Implement zoom-in functionality
}

function zoomOut() {
    // Implement zoom-out functionality
}

function checkPageSize() {
    const pageSize = document.getElementById('page-size').value;
    const customSizeField = document.getElementById('custom-size');
    
    if (pageSize === 'Custom') {
        customSizeField.classList.remove('hidden');
    } else {
        customSizeField.classList.add('hidden');
    }
}

function validateCustomSize() {
    // Basic validation for custom size
    const customSize = document.getElementById('custom-size').value;
    const regex = /^\d+(\.\d+)? x \d+(\.\d+)?$/;
    if (!regex.test(customSize)) {
        alert('Invalid custom size format. Please use the format "width x height"');
    }
}

function closeThumbnail() {
    document.getElementById('preview-image').style.display = 'none';
}

function rotateThumbnail() {
    const img = document.getElementById('preview-image');
    let currentRotation = parseInt(img.getAttribute('data-rotation')) || 0;
    currentRotation = (currentRotation + 90) % 360;
    img.style.transform = `rotate(${currentRotation}deg)`;
    img.setAttribute('data-rotation', currentRotation);
}
