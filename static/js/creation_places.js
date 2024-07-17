$(document).ready(function() {
    // Existing JavaScript code

    // Show modal when "New" is selected
    $('#disaster').change(function() {
        if ($(this).val() === 'new') {
            $('#addNewDisasterModal').modal('show');
        }
    });

    $('#province').change(function() {
        if ($(this).val() === 'new') {
            $('#addNewProvinceModal').modal('show');
        }
    });

    $('#municipality').change(function() {
        if ($(this).val() === 'new') {
            $('#addNewMunicipalityModal').modal('show');
        }
    });

    $('#barangay').change(function() {
        if ($(this).val() === 'new') {
            $('#addNewBarangayModal').modal('show');
        }
    });

    // Save new disaster
    $('#saveNewDisaster').click(function() {
        $.ajax({
            url: '/create_disaster/',
            method: 'POST',
            data: {
                name: $('#newDisasterName').val(),
                description: $('#newDisasterDescription').val(),
                date_occurred: $('#newDisasterDate').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    $('#disaster').append($('<option>', {
                        value: response.id,
                        text: response.name
                    }));
                    $('#disaster').val(response.id);
                    $('#addNewDisasterModal').modal('hide');
                } else {
                    alert('Error: ' + response.message);
                }
            }
        });
    });

    // Save new province
    $('#saveNewProvince').click(function() {
        $.ajax({
            url: '/create_province/',
            method: 'POST',
            data: {
                name: $('#newProvinceName').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    $('#province').append($('<option>', {
                        value: response.id,
                        text: response.name
                    }));
                    $('#province').val(response.id);
                    $('#addNewProvinceModal').modal('hide');
                } else {
                    alert('Error: ' + response.message);
                }
            }
        });
    });

    // Save new municipality
    $('#saveNewMunicipality').click(function() {
        $.ajax({
            url: '/create_municipality/',
            method: 'POST',
            data: {
                name: $('#newMunicipalityName').val(),
                province: $('#province').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    $('#municipality').append($('<option>', {
                        value: response.id,
                        text: response.name
                    }));
                    $('#municipality').val(response.id);
                    $('#addNewMunicipalityModal').modal('hide');
                } else {
                    alert('Error: ' + response.message);
                }
            }
        });
    });

    // Save new barangay
    $('#saveNewBarangay').click(function() {
        $.ajax({
            url: '/create_barangay/',
            method: 'POST',
            data: {
                name: $('#newBarangayName').val(),
                municipality: $('#municipality').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    $('#barangay').append($('<option>', {
                        value: response.id,
                        text: response.name
                    }));
                    $('#barangay').val(response.id);
                    $('#addNewBarangayModal').modal('hide');
                } else {
                    alert('Error: ' + response.message);
                }
            }
        });
    });
});
