$(function() {
  $(".autosubmit").change(function () {
    var form = $(this).closest('form');
    form.append('<input type="hidden" name="_intermediate" value="true"></input>');
    form.submit();
  });
});
