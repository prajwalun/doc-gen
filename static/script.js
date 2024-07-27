document.addEventListener('DOMContentLoaded', function() {
    var uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.onsubmit = function(event) {
            event.preventDefault();
            document.getElementById('loading').style.display = 'block';
            var formData = new FormData(uploadForm);
            fetch('/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                if (data.documentation) {
                    window.location.href = '/documentation?documentation=' + encodeURIComponent(data.documentation);
                } else {
                    alert('Error: ' + (data.error || 'Failed to process the documentation.'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loading').style.display = 'none';
                alert('Failed to process the documentation. Please check the server logs.');
            });
        };
    }

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
