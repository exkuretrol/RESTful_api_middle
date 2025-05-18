const dataset = document.currentScript.dataset;
const userLeaveBalanceUrl = dataset.userLeaveBalanceUrl;
const normalUserLeaveRequestListCreateUrl = dataset.normalUserLeaveRequestListCreateUrl;

$(function() {
    const start_datetime_el = $("#id_effective_start_datetime")            
    const end_datetime_el = $("#id_effective_end_datetime")

    $('input[name="datetimes"]').daterangepicker({
        timePicker: true,
        startDate: moment().set({ hour: 9, minute: 0, second: 0 }),
        endDate: moment().set({ hour: 18, minute: 0, second: 0 }),
        timePickerIncrement: 60,
        autoApply: true,
        locale: {
            format: 'M/DD HH:mm'
        }
    }, function(start, end, label) {
        start_datetime_el.val(start.format("YYYY-MM-DDTHH:mm:ssZ"));
        end_datetime_el.val(end.format("YYYY-MM-DDTHH:mm:ssZ"));
    });

    function refresh_user_leave_balance() {
        $.ajax({
            url: userLeaveBalanceUrl,
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                const list = $('#leave-balance-list');
                list.empty();

                data.results.forEach(function (item) {
                    const categoryName = item.category.name;
                    const remaining_amount = item.remaining_amount;
                    const remaining_days = Math.floor(remaining_amount / 8);
                    const remaining_hours = remaining_amount % 8;

                    const li = $('<li></li>').text(
                        `${categoryName}: ${remaining_days}天 ${remaining_hours}小時`
                    );
                    list.append(li);
                });
            },
            error: function (xhr, status, error) {
                console.error('取得假期資料失敗：', error);
            }
        });
    }

    refresh_user_leave_balance();

    const leaves_form = $("#leaves-form");

    leaves_form.on("submit", function(event) {
        event.preventDefault();

        var formData = leaves_form.serializeArray();

        $.ajax({
            url: normalUserLeaveRequestListCreateUrl,
            method: 'POST',
            data: formData,
            dataType: 'json',
            success: function (data) {
                console.log('請假申請成功：', data);
                refresh_user_leave_balance();
                alert("請假申請成功");
            },
            error: function (xhr, status, error) {
                console.error('請假申請失敗：', error);
                alert("請假申請失敗");
            }
        });
    });

    function refresh_user_leave_request_list() {
        $.ajax({
            url: normalUserLeaveRequestListCreateUrl,
            method: 'GET',
            success: function (data) {
                const $tbody = $('#leave-table tbody');
                $tbody.empty(); // 清空舊資料

                data.results.forEach(function (item) {
                    const row = `
                        <tr data-uuid="${item.uuid}">
                            <td>${moment(item.effective_start_datetime).format("MM/DD HH:mm")} ~ ${moment(item.effective_end_datetime).format("MM/DD HH:mm")}</td>
                            <td>${item.total_leave_hours}</td>
                            <td>${item.category}</td>
                            <td>${item.status}</td>
                            <td><button class="delete-btn">刪除</button></td>
                        </tr>
                    `;
                    $tbody.append(row);
                });
            },
            error: function () {
                alert('資料載入失敗');
            }
        });
    }


    refresh_user_leave_request_list();
});