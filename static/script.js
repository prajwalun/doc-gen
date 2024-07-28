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

// Handle drag-and-drop
var dropArea = document.getElementById('drop-area');
var fileInput = document.getElementById('file');

dropArea.addEventListener('dragover', function(event) {
    event.preventDefault();
    dropArea.classList.add('dragover');
});

dropArea.addEventListener('dragleave', function(event) {
    dropArea.classList.remove('dragover');
});

dropArea.addEventListener('drop', function(event) {
    event.preventDefault;
    dropArea.classList.remove('dragover');
    fileInput.files = event.dataTransfer.files;

    // Show file name in custom label
    var fileName = event.dataTransfer.files[0].name;
    var label = dropArea.querySelector('.custom-file-label');
    label.textContent = fileName;
});

fileInput.addEventListener('change', function(event) {
    var fileName = event.target.files[0].name;
    var label = dropArea.querySelector('.custom-file-label');
    label.textContent = fileName;
});
