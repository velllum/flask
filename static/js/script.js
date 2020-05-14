

function loadCalculator(select){
    var type = $('select[name="type"]');
    var symbol = $('select[name="symbol"]');

    $(type).html('<option value="hidden" hidden> -- тип конвертера -- </option>');
    $(symbol).html('');

    $.ajax({
        url: '/processCalculator',
        data: {calculator:select.value},
        method: 'POST',
    }).done(function(data) {
            $.each(data, function (name, value) {
                $(type).append('<option value="' + name + '">' + value + '</option>');

            });
        });
    }


function loadCategory(select){
    var symbol = $('select[name="symbol"]');
    $(symbol).html('<option value="hidden" hidden> -- един. измерения -- </option>');

    $.ajax({
        url: '/processType',
        data: {type:select.value},
        method: 'POST',
    }).done(function(data) {
            $.each(data, function (key, val) {
                prevGroup = $('<optgroup />').prop('label', key).appendTo(symbol);
                $.each(val, function (name, value) {
                    $(prevGroup).append('<option value="' + name + '">' + value + '</option>');

                });
            });
        });
    }