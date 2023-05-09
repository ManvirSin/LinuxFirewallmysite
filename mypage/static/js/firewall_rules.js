// Function to add a new row to the configuration table
function addConfigurationRow(rule) {
  var row = $("<tr>");
  row.append($("<td>").text(rule.rule_name));
  row.append($("<td>").text(rule.chain));
  row.append($("<td>").text(rule.source_ip));
  row.append($("<td>").text(rule.destination_ip));
  row.append($("<td>").text(rule.protocol));
  row.append($("<td>").text(rule.source_port));
  row.append($("<td>").text(rule.destination_port));
  row.append($("<td>").text(rule.action));
  row.append($("<td>").text(rule.log_traffic));
  row.append($("<td>").text(rule.alert_user));
  row.append($("<td>").html("<a href='/modify_firewall_rule/" + rule.id + "' class='btn btn-warning'>Modify</a>"));
  row.append($("<td>").html("<a href='/delete_firewall_rule/" + rule.id + "' class='btn btn-danger' onclick='deleteFirewallRule(" + rule.id + ");'>Delete</a>"));
  $("#configuration-table tbody").append(row);
}

// Function to handle the form subm1ission and add a new configuration rule to the table
$("#configuration-form").submit(function(event) {
  event.preventDefault(); // Prevent the default form submission behavior

  // Make an AJAX request to submit the form data to the server
  $.ajax({
    type: "POST",
    url: $(this).attr("action"),
    data: $(this).serialize(),
    success: function(response) {
      // If the request was successful, add the new rule to the table and reset the form
      addConfigurationRow(response);
      $("#configuration-form")[0].reset();
    },
    error: function(response) {
      // If there was an error, display an error message
      alert("An error occurred while submitting the form.");
    }
  });
});

// Function to handle the delete button click and remove a configuration rule from the table
function deleteFirewallRule(id) {
  if (confirm("Are you sure you want to delete this rule?")) {
    // Make an AJAX request to delete the rule from the server
    $.ajax({
      type: "POST",
      url: "/delete_firewall_rule/" + id,
      success: function(response) {
        // If the request was successful, remove the rule from the table
        $("#configuration-table tbody tr[data-id=" + id + "]").remove();
      },
      error: function(response) {
        // If there was an error, display an error message
        alert("An error occurred while deleting the rule.");
      }
    });
  }
}

// Function to initialize the configuration table with existing rules
function initializeConfigurationTable() {
  $.getJSON("/get_firewall_rules/", function(data) {
    $.each(data, function(key, value) {
      addConfigurationRow(value);
    });
  });
}

// Initialize the configuration table on page load
$(document).ready(function() {
  initializeConfigurationTable();
});

// ... Other functions (addConfigurationRow, deleteFirewallRule, etc.) ...

// Function to add a new row to the NAT table
function addNatTableRow(rule) {
  var row = $("<tr>");
  row.append($("<td>").text(rule.source_ip));
  row.append($("<td>").text(rule.destination_ip));
  row.append($("<td>").text(rule.protocol));
  row.append($("<td>").text(rule.source_port));
  row.append($("<td>").text(rule.destination_port));
  row.append($("<td>").html("<a href='/modify_nat_rule/" + rule.id + "' class='btn btn-warning'>Modify</a> <a href='/delete_nat_rule/" + rule.id + "' class='btn btn-danger' onclick='deleteNatRule(" + rule.id + ");'>Delete</a>"));
  $("#nat-table tbody").append(row);
}

// Function to handle the delete button click and remove a NAT rule from the table
function deleteNatRule(id) {
  if (confirm("Are you sure you want to delete this rule?")) {
    // Make an AJAX request to delete the rule from the server
    $.ajax({
      type: "POST",
      url: "/delete_nat_rule/" + id,
      success: function(response) {
        // If the request was successful, remove the rule from the table
        $("#nat-table tbody tr[data-id=" + id + "]").remove();
      },
      error: function(response) {
        // If there was an error, display an error message
        alert("An error occurred while deleting the rule.");
      }
    });
  }
}

// Function to initialize the NAT table with existing rules
function initializeNatTable() {
  $.getJSON("/get_nat_rules/", function(data) {
    $.each(data, function(key, value) {
      addNatTableRow(value);
    });
  });
}

// Initialize both tables on page load
$(document).ready(function() {
  initializeConfigurationTable();
  initializeNatTable();
});
