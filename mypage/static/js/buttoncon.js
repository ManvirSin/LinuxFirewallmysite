$(document).ready(function() {

  // Function to clear form input fields
  function clearFormFields() {
    $('#rule-name').val('');
    $('#rule').val('');
  }

  // Function to reload rules table
  function reloadRulesTable() {
    $.get('{% url "get_firewall_rules" %}', function(data) {
      $('#rules-table tbody').empty();
      data.forEach(function(rule) {
        $('#rules-table tbody').append('<tr id="rule-' + rule.id + '">' +
                                        '<td>' + rule.name + '</td>' +
                                        '<td>' + rule.rule + '</td>' +
                                        '<td>' + rule.description + '</td>' +
                                        '<td><button class="btn btn-info modify-rule" data-rule-id="' + rule.id + '">Modify</button>' +
                                        '<button class="btn btn-danger delete-rule" data-rule-id="' + rule.id + '">Delete</button></td>' +
                                        '</tr>');
      });
    });
  }

  // Add rule form submission handler
  $('#rule-form').submit(function(event) {
    event.preventDefault();
    var ruleName = $('#rule-name').val();
    var rule = $('#rule').val();
    $.post('{% url "create_firewall_rule" %}', {
      'name': ruleName,
      'rule': rule
    }, function(data) {
      // Reload the rules table
      reloadRulesTable();
      // Clear the form input fields
      clearFormFields();
    });
  });

  // Modify rule button click handler
  $('#rules-table').on('click', '.modify-rule', function() {
    var ruleId = $(this).data('rule-id');
    var ruleName = $('#rule-' + ruleId + ' td:nth-child(1)').text();
    var rule = $('#rule-' + ruleId + ' td:nth-child(2)').text();
    $('#rule-name').val(ruleName);
    $('#rule').val(rule);
    $('#rule-form').attr('action', '{% url "modify_firewall_rule" %}' + ruleId);
    $('#rule-form').append('<input type="hidden" name="_method" value="PUT">');
  });

  // Delete rule button click handler
  $('#rules-table').on('click', '.delete-rule', function() {
    var ruleId = $(this).data('rule-id');
    $.ajax({
      url: '{% url "delete_firewall_rule" %}' + ruleId,
      type: 'DELETE',
      success: function(result) {
        $('#rule-' + ruleId).remove();
      }
    });
  });

  // Clear rule button click handler
  $('#rule-form').on('click', '.btn-secondary', function() {
    clearFormFields();
    $('#rule-form').removeAttr('action');
    $('#rule-form input[name="_method"]').remove();
  });

  // Load rules table on page load
  reloadRulesTable();

});
