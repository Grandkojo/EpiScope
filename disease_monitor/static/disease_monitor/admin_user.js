(function() {
  function toggleHospitalRequirement() {
    var isAdminCheckbox = document.getElementById('id_is_admin');
    var hospitalRow = document.querySelector('.form-row.field-hospital, .fieldBox.field-hospital');
    var hospitalSelect = document.getElementById('id_hospital');
    if (!isAdminCheckbox || !hospitalRow || !hospitalSelect) return;

    var required = isAdminCheckbox.checked;
    hospitalRow.style.display = '';
    if (required) {
      hospitalSelect.setAttribute('required', 'required');
      hospitalRow.classList.add('required');
    } else {
      hospitalSelect.removeAttribute('required');
      hospitalRow.classList.remove('required');
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    toggleHospitalRequirement();
    var isAdminCheckbox = document.getElementById('id_is_admin');
    if (isAdminCheckbox) {
      isAdminCheckbox.addEventListener('change', toggleHospitalRequirement);
    }
  });
})(); 