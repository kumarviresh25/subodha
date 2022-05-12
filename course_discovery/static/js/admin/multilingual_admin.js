$( document ).ready(function() {
   $('.field-program_title').hide()
    $('.field-course_title').hide()
    let content_type = $('#id_content_type').val()
    $('#id_content_type').change(function(e){
        var content_type = this.value;
        _handleFields(content_type);
    })

    $('#id_program_title').change(function(e){
        let program_key = this.value;
        var url = window.location.origin+'/mx_discovery/getkeydata?key='+program_key+'&type=program';
        $.ajax({
            type: 'GET',
            url: url,
            success:function(data){
                _populateValues(data.title,data.short_description,data.full_description)
            }
        });
    })

    $('#id_course_title').change(function(e){
        let course_key = this.value;
        var url = window.location.origin+'/mx_discovery/getkeydata?key='+course_key+'&type=course';
        $.ajax({
            type: 'GET',
            url: url,
            success:function(data){
                _populateValues(data.title,data.short_description,data.full_description)
            }
        });
    })

    function _populateValues(title,short_desc,full_desc){
        $('#id_title').val(title);
        $('#id_short_description').val(short_desc);
        $('#id_full_description').val(full_desc);
    }

    function _handleFields(content_type){
        // function call to make the program and course key show.
        // And to set the required like seen for the program and course keys.
        // To prefilled the data in the title, short and full description fields.

        switch(content_type){
            case 'program':
                let program_title = $('#id_title').val();
                let program_short_desc = $('#id_short_description').val();
                let program_full_desc = $('#id_full_description').val();
                _populateValues(program_title,program_short_desc,program_full_desc);
                if ($('.field-course_title').show()){
                    $('.field-course_title').hide();
                }
                $('.field-program_title').show();
                $('.field-short_description').show();
                $('.field-full_description').show();
                if ($('.field-course_title label').hasClass('required')){
                    $('.field-course_title label').removeClass('required');
                    $('#id_course_title').prop('required',false);
                }
                if (! $('.field-program_title label').hasClass('required')){
                    $('.field-program_title label').addClass('required');
                    $('#id_program_title').prop('required',true);
                }
                
                break;
            case 'course':
                let course_title = $('#id_title').val();
                let course_short_desc = $('#id_short_description').val();
                let course_full_desc = $('#id_full_description').val();
                _populateValues(course_title,course_short_desc,course_full_desc);
                if ($('.field-program_title').show()){
                    $('.field-program_title').hide();
                }
                $('.field-course_title').show();
                $('.field-short_description').show();
                $('.field-full_description').show();
                if ($('.field-program_title label').hasClass('required')){
                    $('.field-program_title label').removeClass('required');
                    $('#id_program_title').prop('required',false);
                }
                if (! $('.field-course_title label').hasClass('required')){
                    $('.field-course_title label').addClass('required');
                    $('#id_course_title').prop('required',true);
                }
                break;
            case 'tag':
                let tag_title = $('#id_title').val();
                let tag_short_desc = $('#id_short_description').val();
                let tag_full_desc = $('#id_full_description').val();
                _populateValues(tag_title,tag_short_desc,tag_full_desc);
                $('.field-program_title').hide();
                $('.field-course_title').hide();
                $('#id_short_description').val('');
                $('.field-short_description').hide();
                $('#id_full_description').val('');
                $('.field-full_description').hide();
                if ($('.field-course_title label').hasClass('required')){
                    $('.field-course_title label').removeClass('required');
                    $('#id_course_title').prop('required',false);
                }
                if ($('.field-program_title label').hasClass('required')){
                    $('.field-program_title label').removeClass('required');
                    $('#id_program_title').prop('required',false);
                }
                break;
        }
    }

    _handleFields(content_type);
});
