$(document).on("click", ".delete-rule", function() {
    var ruleId = $(this).data("rule-id");
    $.ajax({
      url: '/delete-rule/'+ruleId,
      type: 'DELETE',
      success: function(result) {
        $("#rule-" + ruleId).remove();
      }
    });
  });
  
  
  $(document).on("click", ".modify-rule", function() {
    var ruleId = $(this).data("rule-id");
    // Code to open a modal or redirect to a modify page
  });
  
  });
  