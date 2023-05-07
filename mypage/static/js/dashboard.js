function deleteFirewallRule(ruleId) {
    if (confirm('Are you sure you want to delete this rule?')) {
      $.ajax({
        url: `/delete_firewall_rule/${ruleId}`,
        type: 'POST',
        success: function (response) {
          if (response.success) {
            location.reload();
          } else {
            alert('Error deleting rule.');
          }
        },
        error: function () {
          alert('Error deleting rule.');
        },
      });
    }
  }
  