// Bulk Mailer JS Helper
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('csvFileInput');
    const previewContainer = document.getElementById('filePreviewContainer');
    const recipientCountSpan = document.getElementById('recipientCountSpan');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            if (file.name.endsWith('.csv')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const text = e.target.result;
                    const lines = text.split('\n').filter(line => line.trim() !== '');
                    const count = Math.max(0, lines.length - 1); // minus header
                    
                    if (recipientCountSpan) {
                        recipientCountSpan.innerText = count + ' Recipients Loaded';
                    }

                    if (previewContainer) {
                        let html = '<div class="alert alert-info py-2 px-3 small fw-bold mb-2"><i class="fas fa-check-circle me-1"></i> File "' + file.name + '" read successfully! (' + count + ' contacts found)</div>';
                        previewContainer.innerHTML = html;
                    }
                };
                reader.readAsText(file);
            } else if (file.name.endsWith('.xlsx')) {
                if (recipientCountSpan) {
                    recipientCountSpan.innerText = 'Excel File Selected';
                }
                if (previewContainer) {
                    previewContainer.innerHTML = '<div class="alert alert-info py-2 px-3 small fw-bold mb-2"><i class="fas fa-file-excel me-1"></i> Excel file "' + file.name + '" attached.</div>';
                }
            }
        });
    }
});
