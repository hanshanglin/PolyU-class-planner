
function subjectSearch() {
    var department = $("#select-department").val();
    var sem = $("input[name='sem-select']:checked").val();
    sem = sem.substring(3);
    $.ajax({
        type: "POST",
        url: "/api/subjectinfo",
        data: JSON.stringify({ "sem": sem, "department": department }),
        contentType: 'application/json; charset=UTF-8',
        success: function (data) {
            var obj = data;
            $('#subject-select').empty();
            for (var code in obj) {
                var group = "<optgroup label='&LA&' id='&LA&'></optgroup>".replace('&LA&', code).replace('&LA&', code + "-group");
                $('#subject-select').append(group);
                for (const msg of obj[code]) {
                    var tmp = "<option value='&VA&'>&MSG&</option>".replace('&VA&', msg).replace('&MSG&', msg);
                    $('#' + code + "-group").append(tmp);
                }
            }
            $('#subject-select').selectpicker('refresh');
            $('#subject-select').selectpicker('render');
        },
        error: function (data) {
            console.log(data);
        }

    });
}

var prev_subject = [];
var cur_arrange = {};
const templates = "<li class='cd-schedule__event'><a data-start='&sh&:&sm&' data-end='&eh&:&em&' data-content='&c1&' data-event='event-&nu&' href='#0'><em class='cd-schedule__name'>&c2&</em></a></li>"


function draw_table() {
    if (cur_arrange == null) return;
    for (var i of ['mon-list', 'tue-list', 'wed-list', 'thu-list', 'fri-list', 'sat-list']) {
        $('#' + i + " li").remove();
    }
    var cnt = 0;
    for (var i in cur_arrange) {
        var cur = cur_arrange[i];
        var tmp = templates;
        var sh = String(Math.floor(cur['Start Time'] / 100));
        var sm = String(Math.floor(cur['Start Time'] % 100));
        var eh = String(Math.floor(cur['End Time'] / 100));
        var em = String(Math.floor(cur['End Time'] % 100));

        tmp = tmp.replace("&sh&", sh);
        tmp = tmp.replace("&sm&", sm);
        tmp = tmp.replace("&eh&", eh);
        tmp = tmp.replace("&em&", em);
        tmp = tmp.replace("&c1&", cur['Subject Code']);
        tmp = tmp.replace("&c2&", cur['Subject Code'] + " " + cur['Component Code']);
        tmp = tmp.replace("&nu&", cnt % 4 + 1);

        $('#' + cur['Day of Week'].toLowerCase() + '-list').append(tmp);
        // console.log(tmp);
        cnt++;
    }
    table.placeEvents();
}
function selectElementContents(el) {
    var body = document.body, range, sel;
    if (document.createRange && window.getSelection) {
        range = document.createRange();
        sel = window.getSelection();
        sel.removeAllRanges();
        try {
            range.selectNodeContents(el);
            sel.addRange(range);
        } catch (e) {
            range.selectNode(el);
            sel.addRange(range);
        }
    } else if (body.createTextRange) {
        range = body.createTextRange();
        range.moveToElementText(el);
        range.select();
    }
    document.execCommand("copy")
    window.getSelection().empty()
}

function share() {
    if (cur_arrange == null || cur_arrange == {}) {
        $("#common-modal-body").text("Please generate a plan first~");
        $("#common-modal").modal("show");
        return
    }
    $.ajax({
        type: "POST",
        url: "/api/sharelink",
        data: JSON.stringify({ 'data': cur_arrange }),
        contentType: 'application/json; charset=UTF-8',
        success: function (data) {
            console.log(data)
        },
        error: function (data) {
            console.log(data);
        }

    });
}

function text_expert() {
    if (cur_arrange == null || cur_arrange == {}) {
        $("#common-modal-body").text("Please generate a plan first~");
        $("#common-modal").modal("show");
        return
    }
    $("#export-text-modal-body").empty();
    var cnt = 0;
    for (var i in cur_arrange) {
        var cur = cur_arrange[i];
        var tmp = "<tr><th scope='row'>&N&</th><td>&SUB&</td><td>&TIT&</td><td>&COM&</td><td>&DAY&</td><td>&STR&</td><td>&END&</td></tr>";
        tmp = tmp.replace("&N&", cnt)
            .replace("&SUB&", cur['Subject Code'])
            .replace("&TIT&", cur['Subject Title'])
            .replace("&COM&", cur['Component Code'])
            .replace("&DAY&", cur['Day of Week'])
            .replace("&STR&", cur['Start Time'])
            .replace("&END&", cur['End Time']);
        $("#export-text-modal-body").append(tmp);

        cnt++;
    }
    $("#export-text-modal").modal('show');
}

function pdf_expert() {
    if (cur_arrange == null || cur_arrange == {}) {
        $("#common-modal-body").text("Please generate a plan first~");
        $("#common-modal").modal("show");
        return
    }
    $("#export-text-modal-body").empty();
    var cnt = 0;
    for (var i in cur_arrange) {
        var cur = cur_arrange[i];
        var tmp = "<tr><th scope='row'>&N&</th><td>&SUB&</td><td>&TIT&</td><td>&COM&</td><td>&DAY&</td><td>&STR&</td><td>&END&</td></tr>";
        tmp = tmp.replace("&N&", cnt)
            .replace("&SUB&", cur['Subject Code'])
            .replace("&TIT&", cur['Subject Title'])
            .replace("&COM&", cur['Component Code'])
            .replace("&DAY&", cur['Day of Week'])
            .replace("&STR&", cur['Start Time'])
            .replace("&END&", cur['End Time']);
        $("#export-text-modal-body").append(tmp);

        cnt++;
    }
    $("#text-target").printThis()
}





function solve() {
    if (prev_subject == null || prev_subject.length == 0) {
        $("#common-modal-body").text("please select at least one subject");
        $("#common-modal").modal("show");
        return
    }
    var data = {}
    prev_subject.forEach(i => {
        var cur = i.split(" ")[0];
        var forbid = []
        var fixed = []
        $("#" + cur + "-setting .red").each(function () { forbid.push($(this).attr('id').split('-')[1]) })
        $("#" + cur + "-setting .green").each(function () { fixed.push($(this).attr('id').split('-')[1]) })
        data[cur] = {}
        data[cur]['forbid'] = forbid
        data[cur]['fixed'] = fixed
    });
    $.ajax({
        type: "POST",
        url: "/api/solve",
        data: JSON.stringify({ "sem": $("input[name='sem-select']:checked").val().substring(3), 'data': data }),
        contentType: 'application/json; charset=UTF-8',
        success: function (data) {
            if (data['solve'] == true) {
                //solved
                cur_arrange = data['result'];
                draw_table();
            }
            else {
                $("#common-modal-body").text(data['result']);
                $("#common-modal").modal("show");
            }
        },
        error: function (data) {
            console.log(data);
        }

    });
}

function subjectSelectChange() {
    var cur_subject = $('#subject-select').val();
    if (cur_subject == null) cur_subject = [];
    if (prev_subject == null) prev_subject = [];

    if (prev_subject.length < cur_subject.length) {
        // add
        var new_subject = cur_subject.filter(function (v) { return prev_subject.indexOf(v) == -1 });
        var new_subject_code = new_subject.toString().split(" ")[0];
        //ajax
        $.ajax({
            type: "POST",
            url: "/api/classinfo",
            data: JSON.stringify({ "subject": new_subject_code, "sem": $("input[name='sem-select']:checked").val().substring(3) }),
            contentType: 'application/json; charset=UTF-8',
            success: function (data) {
                if (data['code'] == new_subject_code) {
                    var container = "<div class='mt-3' id='&CODE&-setting'><h4>&HEAD&</h4></div>".replace("&CODE&", new_subject_code).replace("&HEAD&", new_subject);
                    $('#subject-setting-container').append(container);
                    for (const component_name of data['component']) {
                        var button = "<button type='button' class='btn btn-secondary grey mr-3 mt-1' id='&ID&' onclick='subjectToggle(this)'>&NAME&</button>"
                            .replace("&ID&", new_subject_code + '-' + component_name)
                            .replace("&NAME&", component_name);
                        $('#' + new_subject_code + "-setting").append(button);
                    }
                }
            },
            error: function (data) {
                console.log(data);
            }

        });

    } else {
        // del
        var del_subject = prev_subject.filter(function (v) { return cur_subject.indexOf(v) == -1 });
        del_subject = del_subject.toString().split(" ")[0];
        $("#" + del_subject + "-setting").remove();
    }


    prev_subject = cur_subject;

}


function subjectToggle(obj) {
    var t = obj;
    if ($(t).hasClass('grey')) {
        $(t).removeClass("grey").addClass("red");
    }
    else {
        if ($(t).hasClass('red')) {
            $(t).removeClass("red").addClass("green");
        } else {
            if ($(t).hasClass('green')) {
                $(t).removeClass("green").addClass("grey");
            }
        }
    }
}

var scheduleTemplate = document.getElementsByClassName('js-cd-schedule')[0];
var table = new ScheduleTemplate(scheduleTemplate);
var resizing = false;
$(document).ready(function () {

    window.addEventListener('resize', function (event) {
        // on resize - update events position and modal position (if open)
        if (!resizing) {
            resizing = true;

        }
    });

    table.scheduleReset();
    resizing = false;

    for (var i of ['mon-list', 'tue-list', 'wed-list', 'thu-list', 'fri-list', 'sat-list']) {
        $('#' + i + " li").remove();
    }
    table.placeEvents();

    if ($('#record').text() != "") {
        cur_arrange = JSON.parse($('#record').text());
        draw_table();
    }

});