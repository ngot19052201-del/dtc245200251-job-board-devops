// Client-side interactions
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Client-side file size and format validation for CV uploads
  const cvInputs = document.querySelectorAll('input[type="file"][name="cv"]');
  cvInputs.forEach(input => {
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const validExtensions = ['pdf', 'doc', 'docx'];
        const fileExt = file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(fileExt)) {
          alert('Định dạng tệp không hợp lệ! Vui lòng chỉ tải lên tệp PDF, DOC hoặc DOCX.');
          e.target.value = '';
          return;
        }

        if (file.size > maxSize) {
          alert('Dung lượng tệp vượt quá 5MB! Vui lòng chọn tệp nhỏ hơn.');
          e.target.value = '';
          return;
        }
      }
    });
  });
});
