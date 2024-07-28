document.getElementById('uploadForm').onsubmit = function(event) {
    event.preventDefault();
    document.getElementById('loading').style.display = 'block';
    var formData = new FormData(this);
    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.documentation) {
            // Send a POST request to save the documentation
            fetch('/save-documentation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ documentation: data.documentation }),
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    window.location.href = '/documentation';
                } else {
                    alert('Error saving documentation');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving documentation');
            });
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        alert('An error occurred');
    });
};

document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
});

function setupDragAndDrop() {
    var dropArea = document.getElementById('drop-area');
    var fileInput = document.getElementById('file');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    dropArea.addEventListener('drop', function(e) {
        fileInput.files = e.dataTransfer.files;
        var fileName = e.dataTransfer.files[0].name;
        dropArea.querySelector('.custom-file-label').textContent = fileName;
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            var fileName = e.target.files[0].name;
            dropArea.querySelector('.custom-file-label').textContent = fileName;
        }
    });
}